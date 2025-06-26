"""SQS and SNS setup for AWS"""

import asyncio
import json
import logging
import re
import time
import uuid
from datetime import date
from functools import lru_cache
from json import JSONDecodeError

from botocore.exceptions import ClientError
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from people_api.database.models.pending_registration import (
    PendingRegistration,
    PendingRegistrationData,
    PendingRegistrationMessage,
)
from people_api.dbs import get_async_sessions
from people_api.services.member_onboarding import send_initial_payment_email
from people_api.utils import get_aws_client

from .member_utils import convert_pending_to_member_models


class SQSSettings(BaseSettings):
    """Settings for SQS/SNS integration."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    topic_name: str = "member_onboarding"
    queue_name: str = "pending_member_first_payment"
    dlq_name: str = "dlq"


@lru_cache
def get_sqs_settings() -> SQSSettings:
    """Get SQS settings from environment variables."""
    return SQSSettings()


def setup_sqs_and_sns():
    """Set up SQS and SNS for AWS with DLQ."""
    logging.info("Setting up SQS and SNS with DLQ")
    try:
        sns = get_aws_client(service="sns")
        sqs = get_aws_client(service="sqs")
    except ClientError as e:
        logging.error("Error creating AWS clients: %s", e)
        raise

    topic_name = get_sqs_settings().topic_name
    main_queue_name = get_sqs_settings().queue_name
    dlq_queue_name = get_sqs_settings().dlq_name

    logging.info("Creating or getting SNS topic and SQS queue")
    try:
        topic_response = sns.create_topic(Name=topic_name)
        topic_arn = topic_response["TopicArn"]
    except ClientError as e:
        logging.error("Error creating or getting SNS topic: %s", e)
        raise

    try:
        dlq_response = sqs.create_queue(QueueName=dlq_queue_name)
        dlq_url = dlq_response["QueueUrl"]
        dlq_attrs = sqs.get_queue_attributes(QueueUrl=dlq_url, AttributeNames=["QueueArn"])
        dlq_arn = dlq_attrs["Attributes"]["QueueArn"]
    except ClientError as e:
        logging.error("Error creating or getting DLQ queue: %s", e)
        raise

    try:
        redrive_policy = json.dumps({"deadLetterTargetArn": dlq_arn, "maxReceiveCount": "2"})
        main_response = sqs.create_queue(
            QueueName=main_queue_name, Attributes={"RedrivePolicy": redrive_policy}
        )
        main_url = main_response["QueueUrl"]
        queue_attrs = sqs.get_queue_attributes(QueueUrl=main_url, AttributeNames=["QueueArn"])
        queue_arn = queue_attrs["Attributes"]["QueueArn"]
    except ClientError as e:
        logging.error("Error creating or getting main SQS queue: %s", e)
        raise

    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "Allow-SNS-SendMessage",
                "Effect": "Allow",
                "Principal": {"Service": "sns.amazonaws.com"},
                "Action": "SQS:SendMessage",
                "Resource": queue_arn,
                "Condition": {"ArnEquals": {"aws:SourceArn": topic_arn}},
            }
        ],
    }

    try:
        sqs.set_queue_attributes(QueueUrl=main_url, Attributes={"Policy": json.dumps(policy)})
    except ClientError as e:
        logging.error("Error setting SQS queue policy: %s", e)
        raise

    time.sleep(15)
    logging.info("Subscribing SQS queue to SNS topic")

    try:
        sns.subscribe(TopicArn=topic_arn, Protocol="sqs", Endpoint=queue_arn)
    except ClientError as e:
        logging.error("Error subscribing SQS queue to SNS topic: %s", e)
        raise

    logging.info("SQS, SNS, and DLQ setup complete")
    return sns, sqs, topic_arn, main_url, dlq_url


def _build_member_models(data: PendingRegistrationData) -> None:
    """Instantiate domain models using ``PendingRegistrationData``.

    This ensures that all fields comply with the validations defined on the
    member-related models. The created instances are discarded and only serve
    as a validation mechanism that can be reused when converting a pending
    registration into a real member.
    """

    # Just instantiate the models to validate the payload fields.
    convert_pending_to_member_models(data)


async def process_message(raw_message: str) -> PendingRegistration:
    """
    Parse and validate the raw SNS message JSON string.
    Convert any date/datetime objects in data to ISO format strings.
    """

    def convert_dates(obj):
        if isinstance(obj, dict):
            return {k: convert_dates(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [convert_dates(i) for i in obj]
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        return obj

    def process_legal_representatives(data_dict):
        """Set legal_representatives to [] if fields are empty or if age >= 18."""

        birth_date_str = data_dict.get("birth_date")
        if birth_date_str:
            birth_date = date.fromisoformat(birth_date_str)
            today = date.today()
            age = (
                today.year
                - birth_date.year
                - ((today.month, today.day) < (birth_date.month, birth_date.day))
            )

            if age >= 18:
                data_dict["legal_representatives"] = []
                return

            legal_reps = data_dict.get("legal_representatives", [])
            filtered_reps = []
            for rep in legal_reps:
                if rep.get("name") and rep.get("email") and rep.get("phone_number"):
                    filtered_reps.append(rep)

            if not filtered_reps:
                raise ValueError(
                    "At least one legal representative with complete information (name, email, phone) is required for members under 18 years old"
                )

            data_dict["legal_representatives"] = filtered_reps

    try:
        data_dict = json.loads(raw_message)

        process_legal_representatives(data_dict)

        if "cpf" in data_dict and isinstance(data_dict["cpf"], str):
            data_dict["cpf"] = re.sub(r"\D", "", data_dict["cpf"])

        if "phone_number" in data_dict and isinstance(data_dict["phone_number"], str):
            data_dict["phone_number"] = re.sub(r"\D", "", data_dict["phone_number"])

        message = PendingRegistrationMessage(
            data=PendingRegistrationData(**data_dict),
            token=str(uuid.uuid4()),
        )

        data_dict = message.data.model_dump()
        data_serializable = convert_dates(data_dict)

        _build_member_models(PendingRegistrationData(**data_serializable))

        pending_reg = PendingRegistration(
            data=data_serializable,
            token=message.token,
        )
        return pending_reg

    except ValidationError as e:
        logging.error("Validation error in message: %s", e.json())
        raise e


async def consume_and_store_messages(sqs_client, queue_url, *, max_polls: int | None = None):
    """Continuously consume messages from SQS, validate, and store in the database.

    Args:
        sqs_client: Boto3 SQS client.
        queue_url: URL of the SQS queue to consume from.
        max_polls: Optional maximum number of polling iterations; if set, exit after polling this many times.
    """
    logging.info("Starting to consume messages from SQS queue...")
    poll_count = 0

    while True:
        if max_polls is not None and poll_count >= max_polls:
            logging.info("Reached max_polls=%d, exiting consume loop", max_polls)
            break
        poll_count += 1
        await asyncio.sleep(1)
        try:
            response = sqs_client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=20,
                VisibilityTimeout=30,
            )
            messages = response.get("Messages", [])
            if not messages:
                logging.debug("No messages received. Continuing...")
                continue

            logging.info("Received %d messages from SQS", len(messages))

            for msg in messages:
                try:
                    body = json.loads(msg["Body"])
                    logging.info("Processing message: %s", body)

                    pending = await process_message(body["Message"])

                    async for sessions in get_async_sessions():
                        sessions.rw.add(pending)
                    logging.info("Added pending registration: %s", pending)

                    sqs_client.delete_message(
                        QueueUrl=queue_url, ReceiptHandle=msg["ReceiptHandle"]
                    )
                    logging.info(
                        "Successfully deleted message with ReceiptHandle: %s",
                        msg["ReceiptHandle"],
                    )
                    async for sessions in get_async_sessions():
                        await send_initial_payment_email(
                            session=sessions.rw,
                            pending_registration=pending,
                        )
                except (ValidationError, JSONDecodeError, ClientError, ValueError) as e:
                    logging.error("Error processing message: %s", e)
                    logging.warning("Skipping message due to error: %s", e)
                    try:
                        sqs_client.change_message_visibility(
                            QueueUrl=queue_url,
                            ReceiptHandle=msg["ReceiptHandle"],
                            VisibilityTimeout=0,
                        )
                    except ClientError as ce:
                        logging.error("Error resetting message visibility: %s", ce)
                    continue

        except ClientError as e:
            logging.error("AWS ClientError while receiving or processing messages from SQS: %s", e)
            logging.error("Error receiving or processing messages from SQS: %s", e)

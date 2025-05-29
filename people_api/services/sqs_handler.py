"""SQS and SNS setup for AWS"""

import asyncio
import json
import logging
import time
from functools import lru_cache
from json import JSONDecodeError

from botocore.exceptions import ClientError
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from people_api.database.models.models import (
    Addresses,
    Emails,
    LegalRepresentatives,
    Phones,
    Registration,
)
from people_api.database.models.pending_registration import (
    PendingRegistration,
    PendingRegistrationData,
    PendingRegistrationMessage,
)
from people_api.dbs import get_async_sessions
from people_api.utils import get_aws_client


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

    Registration(
        name=data.full_name,
        social_name=data.social_name,
        birth_date=data.birth_date,
        cpf=data.cpf,
        profession=data.profession,
    )

    Addresses(
        registration_id=0,
        state=data.address.state,
        city=data.address.city,
        address=data.address.street,
        neighborhood=data.address.neighborhood,
        zip=data.address.zip_code,
    )

    Emails(
        registration_id=0,
        email_address=data.email,
    )

    Phones(
        registration_id=0,
        phone_number=data.phone_number,
    )

    for rep in data.legal_representatives or []:
        LegalRepresentatives(
            registration_id=0,
            full_name=rep.name,
            email=rep.email,
            phone=rep.phone_number,
        )


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

    try:
        message = PendingRegistrationMessage.model_validate_json(raw_message)
        data_dict = message.data.model_dump()
        data_serializable = convert_dates(data_dict)

        # Validate that the payload can be converted into the models used for a
        # real member. Any validation errors raised here will surface as
        # ``ValidationError`` and be handled by the caller.
        _build_member_models(message.data)

        pending_reg = PendingRegistration(
            id=message.id,
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
                except (ValidationError, JSONDecodeError, ClientError) as e:
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

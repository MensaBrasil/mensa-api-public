"""Test SQS and SNS integration using Moto server."""

import asyncio
import json
import os

import boto3
import pytest

os.environ.setdefault("TOPIC_NAME", "member_onboarding")
os.environ.setdefault("QUEUE_NAME", "pending_member_first_payment")
os.environ.setdefault("DLQ_NAME", "dlq")

from people_api.database.models.pending_registration import PendingRegistration
from people_api.services.sqs_handler import (
    consume_and_store_messages,
)

os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
TOPIC_NAME = os.environ["TOPIC_NAME"]
QUEUE_NAME = os.environ["QUEUE_NAME"]


@pytest.fixture
def aws_clients(moto_server):
    """Create AWS clients for SNS and SQS using Moto server."""
    sns = boto3.client("sns", endpoint_url=moto_server)
    sqs = boto3.client("sqs", endpoint_url=moto_server)
    return sns, sqs


@pytest.fixture
def set_policy(aws_clients):
    """Set up the policy for SQS to allow SNS to send messages."""
    sns, sqs = aws_clients

    topic_response = sns.create_topic(Name=TOPIC_NAME)
    topic_arn = topic_response["TopicArn"]

    queue_response = sqs.create_queue(QueueName=QUEUE_NAME)
    queue_url = queue_response["QueueUrl"]

    attrs = sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=["QueueArn"])
    queue_arn = attrs["Attributes"]["QueueArn"]

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

    sqs.set_queue_attributes(QueueUrl=queue_url, Attributes={"Policy": json.dumps(policy)})

    sns.subscribe(TopicArn=topic_arn, Protocol="sqs", Endpoint=queue_arn)

    return sns, sqs, topic_arn, queue_url


def test_sqs_sns_setup(aws_clients):
    """Test the setup of SNS and SQS with Moto server."""
    sns, sqs = aws_clients

    topic_response = sns.create_topic(Name=TOPIC_NAME)
    assert "TopicArn" in topic_response
    topic_arn = topic_response["TopicArn"]

    queue_response = sqs.create_queue(QueueName=QUEUE_NAME)
    assert "QueueUrl" in queue_response
    queue_url = queue_response["QueueUrl"]

    attrs = sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=["QueueArn"])
    queue_arn = attrs["Attributes"]["QueueArn"]

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

    sqs.set_queue_attributes(QueueUrl=queue_url, Attributes={"Policy": json.dumps(policy)})

    subscription = sns.subscribe(TopicArn=topic_arn, Protocol="sqs", Endpoint=queue_arn)
    assert "SubscriptionArn" in subscription


def test_sqs_sns_message_delivery(set_policy):
    """Test message delivery from SNS to SQS."""
    sns, sqs, topic_arn, queue_url = set_policy

    message = {"hahahaha": "ole ola"}
    sns.publish(TopicArn=topic_arn, Message=json.dumps(message))
    response = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)
    messages = response.get("Messages", [])
    assert len(messages) == 1

    sns_message = json.loads(messages[0]["Body"])
    original_message = json.loads(sns_message["Message"])
    assert original_message == message


@pytest.mark.asyncio
async def test_process_valid_message(set_policy, sync_rw_session):
    """Test that a valid message is processed and stored in PendingMessages."""

    sns, sqs, topic_arn, queue_url = set_policy

    valid_payload = json.dumps(
        {
            "id": 123,
            "data": {
                "full_name": "Maria da Silva",
                "social_name": "Maria Silva",
                "email": "maria.silva@example.com",
                "birth_date": "1990-05-20",
                "cpf": "25760480057",
                "profession": "Engenheira de Software",
                "gender": "Feminino",
                "phone_number": "+5511987654321",
                "address": {
                    "street": "Rua das Flores",
                    "neighborhood": "Jardim Primavera",
                    "city": "São Paulo",
                    "state": "SP",
                    "zip_code": "01234567",
                    "country": "Brasil",
                },
                "legal_representatives": [
                    {
                        "name": "João Silva",
                        "email": "joao.silva@example.com",
                        "phone_number": "+5511999998888",
                    },
                    {
                        "name": "Ana Pereira",
                        "email": "ana.pereira@example.com",
                        "phone_number": "+5511988887777",
                    },
                ],
            },
            "token": "valid-token",
        }
    )

    sns.publish(TopicArn=topic_arn, Message=valid_payload)

    await asyncio.sleep(0.5)

    await consume_and_store_messages(sqs_client=sqs, queue_url=queue_url, max_polls=1)

    async def check_message_deletion(sqs_client, queue_url, retries=3, delay=1):
        for _ in range(retries):
            response = sqs.receive_message(QueueUrl=queue_url)
            if "Messages" not in response:
                return True
            await asyncio.sleep(delay)
        return False

    assert await check_message_deletion(sqs, queue_url)

    stored = sync_rw_session.query(PendingRegistration).filter_by(id=123).one_or_none()
    assert stored is not None
    assert stored.token == "valid-token"
    # The data payload should include the new optional fields 'gender' and 'address.country'
    expected_data = {
        "full_name": "Maria da Silva",
        "social_name": "Maria Silva",
        "email": "maria.silva@example.com",
        "birth_date": "1990-05-20",
        "cpf": "25760480057",
        "profession": "Engenheira de Software",
        "gender": "Feminino",
        "phone_number": "+5511987654321",
        "address": {
            "street": "Rua das Flores",
            "neighborhood": "Jardim Primavera",
            "city": "São Paulo",
            "state": "SP",
            "zip_code": "01234567",
            "country": "Brasil",
        },
        "legal_representatives": [
            {
                "name": "João Silva",
                "email": "joao.silva@example.com",
                "phone_number": "+5511999998888",
            },
            {
                "name": "Ana Pereira",
                "email": "ana.pereira@example.com",
                "phone_number": "+5511988887777",
            },
        ],
    }
    assert stored.data == expected_data


@pytest.mark.asyncio
async def test_process_invalid_message_remains_in_queue(set_policy):
    """Test that an invalid message is not deleted and remains in the queue."""

    sns, sqs, topic_arn, queue_url = set_policy

    invalid_payload = json.dumps({"id": "not-an-int", "data": {}, "token": "invalid-token"})

    sns.publish(TopicArn=topic_arn, Message=invalid_payload)

    response = sqs.receive_message(
        QueueUrl=queue_url, MaxNumberOfMessages=10, VisibilityTimeout=1, WaitTimeSeconds=2
    )
    assert "Messages" in response, "Message did not arrive in the queue"

    try:
        await consume_and_store_messages(sqs_client=sqs, queue_url=queue_url, max_polls=1)
    except Exception:
        pass

    await asyncio.sleep(2)

    response_after = {}
    for _ in range(3):
        response_after = sqs.receive_message(
            QueueUrl=queue_url, MaxNumberOfMessages=10, VisibilityTimeout=0, WaitTimeSeconds=2
        )
        if "Messages" in response_after:
            break
        await asyncio.sleep(1)

    assert "Messages" in response_after, "Message was not found back in the queue"

    bodies = [json.loads(msg["Body"]) for msg in response_after["Messages"]]
    messages = [json.loads(body["Message"]) for body in bodies]

    assert any(message.get("token") == "invalid-token" for message in messages), (
        "Invalid message is not in the queue"
    )


@pytest.mark.asyncio
async def test_invalid_phone_keeps_message(set_policy):
    """Invalid member data should not be stored."""

    sns, sqs, topic_arn, queue_url = set_policy

    invalid_payload = json.dumps(
        {
            "id": 999,
            "data": {
                "full_name": "Maria da Silva",
                "social_name": "Maria Silva",
                "email": "maria.silva@example.com",
                "birth_date": "1990-05-20",
                "cpf": "25760480057",
                "profession": "Engenheira de Software",
                "phone_number": "12345",
                "address": {
                    "street": "Rua das Flores",
                    "neighborhood": "Jardim Primavera",
                    "city": "São Paulo",
                    "state": "SP",
                    "zip_code": "01234567",
                },
                "legal_representatives": [],
            },
            "token": "invalid-phone",
        }
    )

    sns.publish(TopicArn=topic_arn, Message=invalid_payload)

    await consume_and_store_messages(sqs_client=sqs, queue_url=queue_url, max_polls=1)

    await asyncio.sleep(1)

    response_after = sqs.receive_message(
        QueueUrl=queue_url, MaxNumberOfMessages=10, VisibilityTimeout=0, WaitTimeSeconds=2
    )

    assert "Messages" in response_after
    bodies = [json.loads(m["Body"]) for m in response_after["Messages"]]
    messages = [json.loads(b["Message"]) for b in bodies]
    assert any(m["token"] == "invalid-phone" for m in messages)


@pytest.mark.asyncio
async def test_invalid_message_goes_to_dlq(aws_clients, sync_rw_session):
    """Test that an invalid message is moved to the DLQ after maxReceiveCount is exceeded."""

    sns, sqs = aws_clients

    existing_queues = sqs.list_queues().get("QueueUrls", [])
    for queue_url in existing_queues:
        sqs.delete_queue(QueueUrl=queue_url)

    topic_response = sns.create_topic(Name=TOPIC_NAME)
    topic_arn = topic_response["TopicArn"]

    dlq_response = sqs.create_queue(QueueName=os.environ["DLQ_NAME"])
    dlq_url = dlq_response["QueueUrl"]
    dlq_attrs = sqs.get_queue_attributes(QueueUrl=dlq_url, AttributeNames=["QueueArn"])
    dlq_arn = dlq_attrs["Attributes"]["QueueArn"]

    redrive_policy = json.dumps({"deadLetterTargetArn": dlq_arn, "maxReceiveCount": "2"})
    main_response = sqs.create_queue(
        QueueName=QUEUE_NAME, Attributes={"RedrivePolicy": redrive_policy}
    )
    main_url = main_response["QueueUrl"]

    attrs = sqs.get_queue_attributes(QueueUrl=main_url, AttributeNames=["QueueArn"])
    queue_arn = attrs["Attributes"]["QueueArn"]

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

    sqs.set_queue_attributes(QueueUrl=main_url, Attributes={"Policy": json.dumps(policy)})

    sns.subscribe(TopicArn=topic_arn, Protocol="sqs", Endpoint=queue_arn)

    invalid_payload = json.dumps({"id": "not-an-int", "data": {}, "token": "invalid-token"})
    sns.publish(TopicArn=topic_arn, Message=invalid_payload)

    for _ in range(3):
        await asyncio.sleep(0.2)
        messages = sqs.receive_message(
            QueueUrl=main_url, MaxNumberOfMessages=1, VisibilityTimeout=1
        ).get("Messages", [])

        if messages:
            try:
                await consume_and_store_messages(sqs_client=sqs, queue_url=main_url, max_polls=1)
            except Exception as e:
                print(f"Error processing message: {e}")

        await asyncio.sleep(1.5)

    await asyncio.sleep(1.5)

    dlq_response = sqs.receive_message(QueueUrl=dlq_url, MaxNumberOfMessages=1)
    assert "Messages" in dlq_response

    body = json.loads(dlq_response["Messages"][0]["Body"])
    payload = json.loads(body["Message"])
    assert payload["token"] == "invalid-token"

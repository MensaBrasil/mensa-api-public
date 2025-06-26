"""Test SQS and SNS integration using Moto server."""

import asyncio
import copy
import json
import os

import boto3
import pytest

from people_api.database.models.pending_registration import PendingRegistration
from people_api.database.models.types import CPFNumber, PhoneNumber, ZipNumber
from people_api.services.sqs_handler import (
    consume_and_store_messages,
)

os.environ.setdefault("TOPIC_NAME", "member_onboarding")
os.environ.setdefault("QUEUE_NAME", "pending_member_first_payment")
os.environ.setdefault("DLQ_NAME", "dlq")

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
@pytest.mark.parametrize(
    "payload, expected_data",
    [
        (
            json.dumps(
                {
                    "full_name": "Maria da Silva",
                    "social_name": "Maria Silva",
                    "email": "maria.silva@example.com",
                    "birth_date": "1990-05-20",
                    "cpf": "123.456.789-09",
                    "profession": "Engenheira de Software",
                    "gender": "Feminino",
                    "admission_type": "test",
                    "phone_number": "+55 (11) 987654321",
                    "address": {
                        "street": "Rua das Flores",
                        "neighborhood": "Jardim Primavera",
                        "city": "São Paulo",
                        "state": "SP",
                        "zip_code": "01234-567",
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
            ),
            {
                "full_name": "Maria da Silva",
                "social_name": "Maria Silva",
                "email": "maria.silva@example.com",
                "birth_date": "1990-05-20",
                "cpf": "12345678909",
                "profession": "Engenheira de Software",
                "admission_type": "test",
                "gender": "Feminino",
                "phone_number": "+55 (11) 987654321",
                "address": {
                    "street": "Rua das Flores",
                    "neighborhood": "Jardim Primavera",
                    "city": "São Paulo",
                    "state": "SP",
                    "zip_code": "01234-567",
                    "country": "Brasil",
                },
                "legal_representatives": [],
            },
        ),
        (
            json.dumps(
                {
                    "full_name": "Maria da Silva",
                    "social_name": "Maria Silva",
                    "email": "maria.silva@example.com",
                    "birth_date": "1990-05-20",
                    "cpf": "987.654.321-00",
                    "profession": "Engenheira de Software",
                    "gender": "Feminino",
                    "admission_type": "report",
                    "phone_number": "+55 (11) 987654321",
                    "address": {
                        "street": "Rua das Flores",
                        "neighborhood": "Jardim Primavera",
                        "city": "São Paulo",
                        "state": "SP",
                        "zip_code": "01234-567",
                        "country": "Brasil",
                    },
                    "legal_representatives": [
                        {
                            "name": None,
                            "email": None,
                            "phone_number": None,
                        },
                    ],
                }
            ),
            {
                "full_name": "Maria da Silva",
                "social_name": "Maria Silva",
                "email": "maria.silva@example.com",
                "birth_date": "1990-05-20",
                "cpf": "98765432100",
                "profession": "Engenheira de Software",
                "gender": "Feminino",
                "admission_type": "report",
                "phone_number": "+55 (11) 987654321",
                "address": {
                    "street": "Rua das Flores",
                    "neighborhood": "Jardim Primavera",
                    "city": "São Paulo",
                    "state": "SP",
                    "zip_code": "01234-567",
                    "country": "Brasil",
                },
                "legal_representatives": [],
            },
        ),
        (
            json.dumps(
                {
                    "full_name": "Carlos Souza",
                    "social_name": "Carlos Souza",
                    "email": "carlos.souza@example.com",
                    "birth_date": "2016-10-15",
                    "cpf": "111.444.777-35",
                    "profession": "Analista de Sistemas",
                    "gender": "Masculino",
                    "admission_type": "test",
                    "phone_number": "+55 (11) 976543210",
                    "address": {
                        "street": "Avenida Central",
                        "neighborhood": "Centro",
                        "city": "Rio de Janeiro",
                        "state": "RJ",
                        "zip_code": "20000-000",
                        "country": "Brasil",
                    },
                    "legal_representatives": [
                        {
                            "name": "Pedro Lima",
                            "email": "pedro.lima@example.com",
                            "phone_number": "+55 (11) 912345678",
                        },
                        {
                            "name": None,
                            "email": None,
                            "phone_number": None,
                        },
                    ],
                }
            ),
            {
                "full_name": "Carlos Souza",
                "social_name": "Carlos Souza",
                "email": "carlos.souza@example.com",
                "birth_date": "2016-10-15",
                "cpf": "11144477735",
                "profession": "Analista de Sistemas",
                "admission_type": "test",
                "gender": "Masculino",
                "phone_number": "+55 (11) 976543210",
                "address": {
                    "street": "Avenida Central",
                    "neighborhood": "Centro",
                    "city": "Rio de Janeiro",
                    "state": "RJ",
                    "zip_code": "20000-000",
                    "country": "Brasil",
                },
                "legal_representatives": [
                    {
                        "name": "Pedro Lima",
                        "email": "pedro.lima@example.com",
                        "phone_number": "+55 (11) 912345678",
                    },
                ],
            },
        ),
    ],
)
async def test_process_valid_message(set_policy, sync_rw_session, payload, expected_data):
    """Test that a valid message is processed and stored in PendingMessages."""

    sns, sqs, topic_arn, queue_url = set_policy

    sns.publish(TopicArn=topic_arn, Message=payload)

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

    stored = sync_rw_session.query(PendingRegistration).all()
    assert len(stored) == 1
    stored = stored[0]

    def normalize(data):
        data = copy.deepcopy(data)
        if "cpf" in data:
            data["cpf"] = CPFNumber.validate_cpf(data["cpf"], None)
        if "phone_number" in data:
            data["phone_number"] = PhoneNumber.validate_phone(data["phone_number"], None)
        if "address" in data and "zip_code" in data["address"]:
            data["address"]["zip_code"] = ZipNumber.validate_zip(data["address"]["zip_code"], None)
        if "legal_representatives" in data:
            for rep in data["legal_representatives"]:
                if rep and rep.get("phone_number"):
                    rep["phone_number"] = PhoneNumber.validate_phone(rep["phone_number"], None)
        return data

    def remove_null_legal_rep(data):
        if data.get("legal_representatives"):
            data["legal_representatives"] = [
                rep
                for rep in data["legal_representatives"]
                if rep and rep.get("name") not in (None, "", "null")
            ]
        return data

    expected_normalized = normalize(expected_data)
    expected_final = remove_null_legal_rep(expected_normalized)
    stored_data_final = remove_null_legal_rep(stored.data)

    assert stored_data_final == expected_final


@pytest.mark.asyncio
async def test_process_invalid_message_underage_no_legal_reps(set_policy, sync_rw_session):
    """Test that an invalid message (underage with no legal representatives) raises an exception and is not stored."""

    sns, sqs, topic_arn, queue_url = set_policy

    invalid_message = json.dumps(
        {
            "full_name": "Lucas Pereira",
            "social_name": "Lucas Pereira",
            "email": "lucas.pereira@example.com",
            "birth_date": "2010-08-12",
            "cpf": "12466302063",
            "profession": "Estudante",
            "gender": "Masculino",
            "phone_number": "+55 (21) 912345678",
            "address": {
                "street": "Rua Nova",
                "neighborhood": "Bairro Novo",
                "city": "Belo Horizonte",
                "state": "MG",
                "zip_code": "30123-456",
                "country": "Brasil",
            },
            "legal_representatives": [],
        }
    )

    # Publish the invalid message
    sns.publish(TopicArn=topic_arn, Message=invalid_message)

    # Try to consume and store messages (should not store due to validation)
    # Wait a moment to ensure the message is available
    await asyncio.sleep(1)

    try:
        await consume_and_store_messages(sqs_client=sqs, queue_url=queue_url, max_polls=1)
    except ValueError:
        # Expected error for underage with no legal representatives
        pass

    # Wait for visibility timeout to expire
    await asyncio.sleep(2)

    # Message should remain in the queue (not deleted)
    response = sqs.receive_message(
        QueueUrl=queue_url, MaxNumberOfMessages=10, VisibilityTimeout=0, WaitTimeSeconds=2
    )
    assert "Messages" in response, "Message should remain in the queue due to validation error"
    bodies = [json.loads(m["Body"]) for m in response["Messages"]]
    messages = [json.loads(b["Message"]) for b in bodies]
    original_data = json.loads(invalid_message)
    assert any(m == original_data for m in messages), "Invalid message should still be in the queue"

    # Message should NOT be stored in the database
    stored_records = sync_rw_session.query(PendingRegistration).all()
    assert len(stored_records) == 0, "Invalid message should not be stored in the database"


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
            "full_name": "Maria da Silva",
            "social_name": "Maria Silva",
            "email": "maria.silva@example.com",
            "birth_date": "1990-05-20",
            "cpf": "12466302063",
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
    original_data = json.loads(invalid_payload)
    assert any(m == original_data for m in messages)


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

"""Test SQS and SNS integration using Moto server."""

import json
import os

import boto3
import pytest

os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

TOPIC_NAME = "member_onboarding"
QUEUE_NAME = "pending_member_first_payment"


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

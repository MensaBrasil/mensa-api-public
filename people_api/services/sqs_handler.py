"""SQS and SNS setup for AWS"""

import json
import logging
import time

from botocore.exceptions import ClientError

from people_api.utils import get_aws_client


def setup_sqs_and_sns():
    """Set up SQS and SNS for AWS."""
    logging.info("Setting up SQS and SNS")
    try:
        sns = get_aws_client(service="sns")
        sqs = get_aws_client(service="sqs")
    except ClientError as e:
        logging.error("Error creating AWS clients: %s", e)
        raise

    topic_name = "member_onboarding"
    queue_name = "pending_member_first_payment"

    logging.info("Creating or getting SNS topic and SQS queue")
    try:
        topic_response = sns.create_topic(Name=topic_name)
        topic_arn = topic_response["TopicArn"]
    except ClientError as e:
        logging.error("Error creating or getting SNS topic: %s", e)
        raise

    try:
        queue_response = sqs.create_queue(QueueName=queue_name)
        queue_url = queue_response["QueueUrl"]
        attrs = sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=["QueueArn"])
        queue_arn = attrs["Attributes"]["QueueArn"]
    except ClientError as e:
        logging.error("Error creating or getting SQS queue: %s", e)
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
        sqs.set_queue_attributes(QueueUrl=queue_url, Attributes={"Policy": json.dumps(policy)})
    except ClientError as e:
        logging.error("Error setting SQS queue policy: %s", e)
        raise

    time.sleep(15)  # Wait for the policy to propagate
    logging.info("Subscribing SQS queue to SNS topic")
    try:
        sns.subscribe(TopicArn=topic_arn, Protocol="sqs", Endpoint=queue_arn)
    except ClientError as e:
        logging.error("Error subscribing SQS queue to SNS topic: %s", e)
        raise
    logging.info("SQS and SNS setup complete")

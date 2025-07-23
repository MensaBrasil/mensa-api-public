"""Module to redrive messages from a Dead Letter Queue (DLQ) to the main SQS queue."""

import logging

from people_api.services.sqs_handler import get_sqs_settings
from people_api.utils import get_aws_client


async def redrive_dlq_to_sqs():
    """Redrive messages from the DLQ to the main SQS queue."""
    sqs = get_aws_client("sqs")
    settings = get_sqs_settings()
    dlq_url = sqs.get_queue_url(QueueName=settings.dlq_name)["QueueUrl"]
    main_url = sqs.get_queue_url(QueueName=settings.queue_name)["QueueUrl"]

    logging.info("Starting redrive from DLQ (%s) to main queue (%s)", dlq_url, main_url)

    while True:
        response = sqs.receive_message(
            QueueUrl=dlq_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=2,
            VisibilityTimeout=10,
        )
        messages = response.get("Messages", [])
        if not messages:
            logging.info("No more messages in DLQ.")
            break

        for msg in messages:
            try:
                body = msg["Body"]

                logging.info("Processing message: %s", body)

                sqs.send_message(
                    QueueUrl=main_url,
                    MessageBody=body,
                )
                logging.info("Redriven message to main queue.")

                sqs.delete_message(
                    QueueUrl=dlq_url,
                    ReceiptHandle=msg["ReceiptHandle"],
                )
                logging.info("Deleted message from DLQ.")
            except Exception as e:
                logging.error("Error redriving message: %s", e)

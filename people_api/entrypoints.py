"""Entrypoints for the service."""

from __future__ import annotations

import argparse
import asyncio
from collections.abc import Callable

from people_api.app import start_api
from people_api.cronjobs.workspace_groups.update_workspace_groups import run_update
from people_api.scripts.redrive_dlq import redrive_dlq_to_sqs
from people_api.services.sqs_handler import (
    consume_and_store_messages,
    setup_sqs_and_sns,
)


def api(_: argparse.Namespace) -> None:
    """Start the API service."""
    start_api()


def update_workspace_groups(_: argparse.Namespace) -> None:
    """Run the workspace groups update job."""
    asyncio.run(run_update())


def sqs_handler(_: argparse.Namespace) -> None:
    """Start the SQS/SNS handler."""
    _, sqs, _, queue_url, _ = setup_sqs_and_sns()
    asyncio.run(consume_and_store_messages(sqs_client=sqs, queue_url=queue_url))


def redrive_dlq(_: argparse.Namespace) -> None:
    """Redrive messages from DLQ to main SQS queue."""
    asyncio.run(redrive_dlq_to_sqs())


def build_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser for the CLI."""
    parser = argparse.ArgumentParser(description="Start a service.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_api = subparsers.add_parser("api", help="Start the API server")
    parser_api.set_defaults(func=api)

    parser_update = subparsers.add_parser("update_workspace_groups", help="Update workspace groups")
    parser_update.set_defaults(func=update_workspace_groups)

    parser_sqs = subparsers.add_parser("sqs_handler", help="Start the SQS handler")
    parser_sqs.set_defaults(func=sqs_handler)

    parser_redrive = subparsers.add_parser(
        "redrive_dlq", help="Redrive messages from DLQ to main SQS queue"
    )
    parser_redrive.set_defaults(func=redrive_dlq)

    return parser


def main(argv: list[str] | None = None) -> None:
    """Parse arguments and dispatch to the selected entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    func: Callable[[argparse.Namespace], None] = args.func
    func(args)

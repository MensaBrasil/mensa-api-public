"""Entrypoints for the service."""

import argparse
import asyncio

from people_api.app import start_api
from people_api.cronjobs.workspace_groups.update_workspace_groups import run_update


def main():
    """Start a service."""
    parser = argparse.ArgumentParser(description="Start a service.")
    parser.add_argument(
        "command",
        choices=["api", "update_workspace_groups"],
        help="Service to start: 'api' or 'update_workspace_groups'",
    )
    args = parser.parse_args()

    if args.command == "api":
        start_api()
    elif args.command == "update_workspace_groups":
        asyncio.run(run_update())


if __name__ == "__main__":
    main()

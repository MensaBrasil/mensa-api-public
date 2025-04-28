"""Service to update workspace groups. Active Adult Associates, Inactive Adult Associates, Active JB Associantes, Inactive JB Associates"""

# pylint: disable=C0413

import asyncio
import logging
import sys

import requests

from people_api.cronjobs.workspace_groups.helpers.core import (
    get_email_list_from_workspace,
    update_workspace_group,
)
from people_api.cronjobs.workspace_groups.helpers.get_service import get_service
from people_api.cronjobs.workspace_groups.helpers.orm_queries import (
    get_active_adult_emails,
    get_active_jb_emails,
    get_inactive_adult_emails,
    get_inactive_jb_emails,
)
from people_api.settings import get_settings

UPTIME_URL = get_settings().google_workspace_cronjob_uptime_url


async def run_update() -> None:
    """Update workspace groups"""
    logging.log(logging.INFO, "Workspace groups update script started")
    try:
        logging.log(logging.INFO, "Returning google service")
        service = get_service()
        logging.log(logging.INFO, "Google service returned successfully")

        groups_ids = [
            "02et92p040v7t2i",
            "03znysh72dw4xp8",
            "0279ka653mesfkc",
            "00pkwqa10wow8wq",
        ]
        functions = [
            get_active_adult_emails,
            get_inactive_adult_emails,
            get_active_jb_emails,
            get_inactive_jb_emails,
        ]

        logging.log(logging.INFO, "Updating workspace groups")
        for ids, f in zip(groups_ids, functions):
            logging.log(logging.INFO, "Updating workspace group: %s", ids)

            logging.log(logging.INFO, "Getting emails from workspace...")
            active_associates = get_email_list_from_workspace(service=service, group_key=ids)
            logging.log(logging.INFO, "Emails retrieved from workspace successfully!")

            logging.log(logging.INFO, "Getting emails from database...")
            active_on_db = await f()
            active_emails = [email for _, email in active_on_db]
            logging.log(logging.INFO, "Emails retrieved from database successfully!")

            logging.log(logging.INFO, "Sending/Removing emails from workspace...")
            update_workspace_group(
                db_emails=active_emails,
                workspace_emails=active_associates,
                service=service,
                group_key=ids,
            )
            logging.log(logging.INFO, "Workspace group %s updated successfully!", ids)

        logging.log(logging.INFO, "All workspace groups updated successfully")
        # Request uptime URL to notify successful execution

        try:
            response = requests.get(UPTIME_URL, timeout=10)
            print(f"Uptime notification sent. Status code: {response.status_code}")
        except Exception as uptime_error:
            print(f"Failed to notify uptime service: {uptime_error}")
            sys.exit(1)

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_update())

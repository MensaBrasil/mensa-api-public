"""Service to update workspace groups. Active Adult Associates, Inactive Adult Associates, Active JB Associantes, Inactive JB Associates"""

# pylint: disable=C0413

import asyncio
import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
)

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

settings = get_settings()

UPTIME_URL = settings.google_workspace_cronjob_uptime_url

async def main():
    """Update workspace groups"""
    try:
        service = get_service()

        # Adult Active Associates
        adult_active_associates = get_email_list_from_workspace(
            service=service, group_key="02et92p040v7t2i"
        )
        adult_active_on_db = await get_active_adult_emails()
        adult_active_emails = [email for _, email in adult_active_on_db]

        # Adult Inactive Associates
        adult_inactive_associates = get_email_list_from_workspace(
            service=service, group_key="03znysh72dw4xp8"
        )
        adult_inactive_on_db = await get_inactive_adult_emails()
        adult_inactive_emails = [email for _, email in adult_inactive_on_db]

        # JB Active Associates
        jb_active_associates = get_email_list_from_workspace(
            service=service, group_key="0279ka653mesfkc"
        )
        jb_active_on_db = await get_active_jb_emails()
        jb_active_emails = [email for _, email in jb_active_on_db]

        # JB Inactive Associates
        jb_inactive_associates = get_email_list_from_workspace(
            service=service, group_key="00pkwqa10wow8wq"
        )
        jb_inactive_on_db = await get_inactive_jb_emails()
        jb_inactive_emails = [email for _, email in jb_inactive_on_db]

        # Update all groups
        update_workspace_group(
            db_emails=adult_active_emails,
            workspace_emails=adult_active_associates,
            service=service,
            group_key="02et92p040v7t2i",
        )
        update_workspace_group(
            db_emails=adult_inactive_emails,
            workspace_emails=adult_inactive_associates,
            service=service,
            group_key="03znysh72dw4xp8",
        )
        update_workspace_group(
            db_emails=jb_active_emails,
            workspace_emails=jb_active_associates,
            service=service,
            group_key="0279ka653mesfkc",
        )
        update_workspace_group(
            db_emails=jb_inactive_emails,
            workspace_emails=jb_inactive_associates,
            service=service,
            group_key="00pkwqa10wow8wq",
        )

        print("Workspace groups updated successfully!")
        # Request uptime URL to notify successful execution

        try:
            response = requests.get(UPTIME_URL, timeout=10)
            print(f"Uptime notification sent. Status code: {response.status_code}")
        except Exception as uptime_error:
            print(f"Failed to notify uptime service: {uptime_error}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())

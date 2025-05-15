"""Core functions for workspace groups cronjobs."""

import logging

import googleapiclient
from googleapiclient.errors import HttpError


def get_email_list_from_workspace(service, group_key) -> list:
    """
    Get email list from google workspace.
    """
    emails = []
    page_token = None

    while True:
        results = (
            service.members()
            .list(groupKey=group_key, maxResults=500, pageToken=page_token)
            .execute()
        )
        members = results.get("members", [])
        emails.extend(
            [
                {
                    "id": member.get("id"),
                    "email": member.get("email"),
                    "role": member.get("role"),
                    "type": member.get("type"),
                    "status": member.get("status"),
                }
                for member in members
            ]
        )
        page_token = results.get("nextPageToken")
        if not page_token:
            break

    return emails


def update_workspace_group(
    db_emails: list,
    workspace_emails: list,
    service: googleapiclient.discovery.Resource,
    group_key: str,
) -> None:
    """Update workspace group with active associates and remove inactive ones."""

    for email in db_emails:
        if email not in [member.get("email") for member in workspace_emails]:
            try:
                service.members().insert(groupKey=group_key, body={"email": email}).execute()
            except HttpError as error:
                print(f"HTTPERROR: Failed to add {email}: {error}")
            except googleapiclient.errors.Error as error:
                print(f"Failed to add {email}: {error}")
            except Exception as error:
                print(f"Failed to add {email}: {error}")

    for associate in workspace_emails:
        if associate.get("email") not in db_emails:
            try:
                service.members().delete(
                    groupKey=group_key, memberKey=associate.get("email")
                ).execute()
            except HttpError as error:
                print(f"HTTPERROR: Failed to remove {associate.get('email')}: {error}")
            except googleapiclient.errors.Error as error:
                print(f"Failed to remove {associate.get('email')}: {error}")
            except Exception as error:
                print(f"Failed to remove {associate.get('email')}: {error}")


def set_group_managers(service, group_key: str, manager_emails: list[str]) -> None:
    """
    Ensures the given list of emails are set as MANAGERS of the Google Group.
    """

    for email in manager_emails:
        try:
            service.members().insert(
                groupKey=group_key, body={"email": email, "role": "MANAGER"}
            ).execute()
            logging.info("Set %s as MANAGER for group %s", email, group_key)
        except HttpError as e:
            if e.resp.status == 409:
                logging.info("%s is already a MANAGER or member of group %s", email, group_key)
            else:
                logging.error("Failed to set manager %s for group %s: %s", email, group_key, e)

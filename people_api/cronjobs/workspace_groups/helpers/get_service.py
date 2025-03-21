"""Helper function to create and return an Admin SDK Directory API service."""

from google.oauth2 import service_account
from googleapiclient.discovery import build

from people_api.settings import get_settings

settings = get_settings()


SCOPES = settings.google_api_scopes.split(",")
SERVICE_ACCOUNT_FILE = settings.service_account_file
GOOGLE_SERVICE_ACCOUNT = settings.google_service_account


def get_service():
    """Creates and returns an Admin SDK Directory API service with proper cleanup."""
    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        delegated_creds = creds.with_subject(GOOGLE_SERVICE_ACCOUNT)
        gservice = build("admin", "directory_v1", credentials=delegated_creds)
        return gservice
    except Exception as e:
        print(f"Error creating service: {e}")
        raise

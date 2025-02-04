"""Service responsible for handling Google Workspace user creation."""

import secrets
import string

from fastapi import Depends, Form, Header, HTTPException
from google.oauth2 import service_account
from googleapiclient.discovery import build
from starlette.status import HTTP_403_FORBIDDEN

from ..settings import get_settings

SETTINGS = get_settings()


def verify_secret_key(x_api_key: str = Header(...)):
    if x_api_key != SETTINGS.google_api_key:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API Key")
    return x_api_key


def generate_password(length=9):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for i in range(length))


# Replace with your service account key JSON file path
SERVICE_ACCOUNT_KEY_PATH = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/admin.directory.user"]


def create_google_workspace_user(primary_email, given_name, family_name, secondary_email=None):
    # Generate a random password
    password = generate_password()

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_KEY_PATH, scopes=SCOPES
    )
    service = build("admin", "directory_v1", credentials=creds)

    user = {
        "primaryEmail": primary_email,
        "name": {
            "givenName": given_name,
            "familyName": "\u200e",
        },
        "password": password,
        "changePasswordAtNextLogin": True,
    }

    if secondary_email:
        user["emails"] = [{"address": secondary_email, "type": "work"}]

    try:
        response = service.users().insert(body=user).execute()
        return response, password  # Return the response and the generated password
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


class WorkspaceService:
    @staticmethod
    def create_user(
        primary_email: str = Form(...),
        given_name: str = Form(...),
        family_name: str = Form(...),
        secondary_email: str = Form(None),
        api_key: str = Depends(verify_secret_key),
    ):
        try:
            user_data, password = create_google_workspace_user(
                primary_email, given_name, family_name, secondary_email
            )
            return {
                "message": "User created successfully",
                "user_data": {"email": user_data["primaryEmail"], "password": password},
            }
        except HTTPException as e:
            raise HTTPException(
                status_code=400,
                detail={"message": "User creation failed", "error": e.detail},
            ) from e

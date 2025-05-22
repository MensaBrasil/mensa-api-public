"""Service responsible for handling Google Workspace user creation."""

import secrets
import string
import unicodedata

import gspread
from fastapi import Depends, Form, Header, HTTPException, status
from google.oauth2 import service_account
from googleapiclient.discovery import build
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.status import HTTP_403_FORBIDDEN

from people_api.dbs import AsyncSessionsTuple
from people_api.services.iam_service import IamService

from ..database.models.models import Emails
from ..settings import get_settings

SETTINGS = get_settings()


def verify_secret_key(x_api_key: str = Header(...)):
    """Verify the API key provided in the request header."""
    if x_api_key != SETTINGS.google_api_key:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API Key")
    return x_api_key


def generate_password(length=9):
    """Generate a random password of specified length."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


# Replace with your service account key JSON file path
SERVICE_ACCOUNT_KEY_PATH = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/admin.directory.user"]


def create_google_workspace_user(primary_email, given_name, family_name, secondary_email=None):
    """Create a new user in Google Workspace."""
    # Generate a random password
    password = generate_password()

    creds = service_account.Credentials.from_service_account_file(
        get_settings().service_account_file, scopes=SCOPES
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


def normalize_name(name):
    """Normalize a name to remove non-ASCII characters and convert to lowercase."""
    if not name:
        return ""
    nfkd_form = unicodedata.normalize("NFKD", name)
    only_ascii = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    only_letters = "".join([c for c in only_ascii if c.isalpha() or c.isspace()])
    return only_letters.lower()


class WorkspaceService:
    """Service for handling Google Workspace user creation."""

    @staticmethod
    def create_user(
        primary_email: str = Form(...),
        given_name: str = Form(...),
        family_name: str = Form(...),
        secondary_email: str = Form(None),
        api_key: str = Depends(verify_secret_key),
    ):
        """Create a new user in Google Workspace."""
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

    @staticmethod
    async def create_mensa_email(registration_id: int, sessions: AsyncSessionsTuple):
        """Create a Mensa email for a member based on their registration ID."""
        try:
            member = await IamService.get_member_by_id(registration_id, sessions.ro)
            if not member:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Member not found",
                )
        except Exception as e:
            raise HTTPException(
                status_code=getattr(e, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
                detail=getattr(
                    e,
                    "detail",
                    {
                        "message": "Failed to fetch member information",
                        "error": str(e),
                    },
                ),
            ) from e

        try:
            member_emails = (
                await sessions.ro.exec(Emails.get_emails_for_member(member.registration_id))
            ).all()

            if member_emails:
                for email in member_emails:
                    if email.email_address and email.email_address.endswith("@mensa.org.br"):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Mensa email already exists for this member. Email Address: {str(email.email_address)}",
                        )

            if not member.name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Member name is required to create a Mensa email.",
                )
            complete_name = normalize_name(member.name).split()
            if len(complete_name) < 2:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Member name must contain at least a first and last name.",
                )
            first_name = complete_name[0]
            last_name = complete_name[-1]
            primary_email = f"{first_name}.{last_name}@mensa.org.br"

            creds = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_KEY_PATH, scopes=SCOPES
            )
            delegated_creds = creds.with_subject(get_settings().google_service_account)
            service = build("admin", "directory_v1", credentials=delegated_creds)

            try:
                existing_user = service.users().get(userKey=primary_email).execute()
                if existing_user:
                    primary_email = (
                        f"{first_name}.{last_name}{member.registration_id}@mensa.org.br".lower()
                    )
            except Exception:
                # Ignore the error if the user is not found, as this is expected
                pass

        except Exception as e:
            raise HTTPException(
                status_code=getattr(e, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
                detail=getattr(
                    e,
                    "detail",
                    {
                        "message": "Internal Server Error",
                        "error": str(e),
                    },
                ),
            ) from e

        try:
            user_data, password = create_google_workspace_user(
                primary_email=primary_email,
                given_name=first_name.capitalize(),
                family_name=last_name.capitalize(),
            )
            new_email = Emails(
                registration_id=member.registration_id,
                email_type="mensa",
                email_address=user_data["primaryEmail"],
            )
            sessions.rw.add(new_email)

            return {
                "message": "Mensa email created successfully",
                "user_data": {"email": user_data["primaryEmail"], "password": password},
                "information": "User will be prompted to change the password at the first login.",
            }
        except HTTPException as e:
            raise HTTPException(
                status_code=e.status_code,
                detail=e.detail,
            ) from e

    @staticmethod
    async def reset_email_password(registration_id: int, mensa_email: str, session: AsyncSession):
        """Reset the password for a Google Workspace user."""
        # Verify if email is vinculated to the registration_id
        member = await IamService.get_member_by_id(registration_id, session)
        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
        email_list: list = []
        db_emails = (await session.exec(Emails.get_emails_for_member(registration_id))).all()
        for email in db_emails:
            email_list.append(email.email_address)
        if mensa_email not in email_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mensa email not found for the member.",
            )

        # Generate a random password
        password = generate_password()

        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_KEY_PATH, scopes=SCOPES
        )
        delegated_creds = creds.with_subject(get_settings().google_workspace_admin_account)
        service = build("admin", "directory_v1", credentials=delegated_creds)

        try:
            # Check if the user exists in Google Workspace
            user = service.users().get(userKey=mensa_email).execute()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            # Update the user's password
            user["password"] = password
            user["changePasswordAtNextLogin"] = True

            response = service.users().update(userKey=mensa_email, body=user).execute()
            return {
                "message": "Password reset successfully",
                "user_data": {"email": response["primaryEmail"], "password": password},
                "information": "User will be prompted to change the password at the first login.",
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            ) from e

    @staticmethod
    async def get_google_spreadsheets_client() -> gspread.Client:
        """Get Google Drive and Google Sheets service."""

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = service_account.Credentials.from_service_account_file(
            get_settings().service_account_file, scopes=scopes
        )

        gsclient = gspread.authorize(creds)

        return gsclient

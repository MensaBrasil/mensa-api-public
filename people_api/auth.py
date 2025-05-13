"""This module contains the authentication logic for the API"""

import logging
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth
from jose import jwt
from sqlmodel import Session

from people_api.database.models.models import Emails, Registration
from people_api.dbs import AsyncSessionsTuple, get_async_sessions, get_read_only_session
from people_api.schemas import InternalToken, UserToken
from people_api.services import IamService
from people_api.settings import get_settings

http_bearer = HTTPBearer()

ro_session = next(get_read_only_session())


async def verify_firebase_token(
    authorization: HTTPAuthorizationCredentials = Security(http_bearer),
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
) -> UserToken | InternalToken:
    """
    Verifies the Firebase token and returns the decoded token data.
    """
    token = authorization.credentials
    try:
        internal_token_result = verify_internal_token(token)
        if internal_token_result.get("valid", False):
            decoded_token = internal_token_result["decoded_token"]
            return InternalToken(**decoded_token)

        decoded_token = auth.verify_id_token(token)
        email = decoded_token.get("email")
        if email:
            registration_id_result = await sessions.ro.exec(
                Emails.select_registration_id_by_email(email)
            )
            rows = registration_id_result.all()
            if not rows:
                raise HTTPException(
                    status_code=401,
                    detail="E-mail is not attached to a registration ID",
                )
            if len(rows) > 1:
                raise HTTPException(
                    status_code=400,
                    detail="Multiple registration IDs found for the provided email",
                )
            registration_id = rows[0]
            decoded_token["registration_id"] = registration_id

            token_data = UserToken(**decoded_token)
            permissions = await IamService.get_member_permissions(token_data, sessions.ro)
            decoded_token["permissions"] = permissions
        else:
            raise HTTPException(status_code=401, detail="E-mail not found")

        return UserToken(**decoded_token)
    except Exception as e:
        logging.info(e)
        raise HTTPException(status_code=401, detail="Invalid Token") from e


def permission_required(required_permissions: str | list[str]):
    """
    Dependency factory that verifies if the authenticated user has at least one
    of the required permissions.
    """

    async def dependency(token_data: UserToken = Depends(verify_firebase_token)):
        if isinstance(required_permissions, str):
            reqs = [required_permissions]
        else:
            reqs = required_permissions
        if not any(req in token_data.permissions for req in reqs):
            raise HTTPException(
                status_code=403,
                detail="Access denied. You don't have the required permission(s).",
            )
        return token_data

    return dependency


def get_registration_id(token_data: UserToken = Depends(verify_firebase_token)) -> int:
    """Returns the registration ID from the token data."""
    return token_data.registration_id


ALGORITHM = "RS256"

with open(f"{get_settings().private_internal_token_key}.pem", "rb") as key_file:
    PRIVATE_SECRET_KEY = key_file.read()
with open(f"{get_settings().public_internal_token_key}.pem", "rb") as key_file:
    PUBLIC_SECRET_KEY = key_file.read()


def create_token(
    registration_id: int | None,
    ttl: int = 30,
    session: Session = ro_session,
) -> str:
    """
    Generates a JSON Web Token (JWT) with specified claims and expiration time.

    Args:
        registration_id (int | None): The registration ID of the user. If None,
            the token will not be associated with a specific user.
        ttl (int, optional): Time-to-live for the token in seconds. Defaults to 30 seconds.
        session (Session): Database session dependency for querying
            user and registration data. Defaults to a read-only session.

    Returns:
        str: The encoded JWT token.

    Raises:
        HTTPException: If the provided registration ID does not exist in the database.
            If the TTL is not a positive integer.

    Notes:
        - The token includes standard claims like issuer (`iss`), subject (`sub`),
            issued-at time (`iat`) and expiration time (`exp`).
        - For authenticated users (valid registration_id), the token includes:
            - registration_id: The user's registration ID
            - email_mensa: The user's Mensa email address (if available)
            - permissions: List of permissions assigned to the user
    """

    if ttl <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TTL (time-to-live) must be a positive integer.",
        )

    claims: dict = {}

    claims["iss"] = "mensa_api"
    claims["sub"] = str(registration_id) if registration_id else "none"
    claims["exp"] = datetime.now(tz=timezone.utc) + timedelta(seconds=ttl)
    claims["iat"] = datetime.now(tz=timezone.utc)
    claims["registration_id"] = None
    claims["email"] = None
    claims["permissions"] = []

    if registration_id:
        registration = session.exec(Registration.select_stmt_by_id(registration_id)).first()

        if not registration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registration ID not found",
            )

        email_result = session.exec(
            Emails.get_emails_for_member(registration.registration_id)
        ).all()
        for e in email_result:
            if e.email_address and e.email_address.endswith("@mensa.org.br"):
                email = str(e.email_address)
                break
        else:
            email = None

        permissions = IamService.get_all_permissions_for_member(
            registration_id=registration.registration_id, session=session
        )

        claims["registration_id"] = registration_id
        claims["email"] = email
        claims["permissions"] = permissions

    token = jwt.encode(claims, PRIVATE_SECRET_KEY, algorithm=ALGORITHM)

    return token


def verify_internal_token(jwt_token: str) -> dict:
    """
    Verifies the internal JWT token and returns the decoded token data.
    Args:
        jwt_token (str): The JWT token to verify.
    Returns:
        dict[str, bool | dict]: A dictionary containing 'valid' (bool) and 'decoded_token' (dict)
    Raises:
        jwt.ExpiredSignatureError: If the token has expired.
        jwt.JWTClaimsError: If there are claims errors in the token.
        jwt.JWTError: For other JWT-related errors.
        ValueError: If the token is invalid or cannot be decoded.
    """
    try:
        decoded_token = jwt.decode(jwt_token, PUBLIC_SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        logging.info("Token has expired")
        return {"valid": False, "decoded_token": {}}
    except jwt.JWTClaimsError as e:
        logging.info("JWT claims error: %s", e)
        return {"valid": False, "decoded_token": {}}
    except jwt.JWTError as e:
        logging.info("JWT error: %s", e)
        return {"valid": False, "decoded_token": {}}
    except ValueError as e:
        logging.info("Value error during token validation: %s", e)
        return {"valid": False, "decoded_token": {}}

    return {"valid": True, "decoded_token": decoded_token}

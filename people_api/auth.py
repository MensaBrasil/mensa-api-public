"""This module contains the authentication logic for the API"""

import logging

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth
from people_api.schemas import UserToken
from .dbs import AsyncSessionsTuple, get_async_sessions
from .services import IamService
from people_api.database.models.models import Emails

http_bearer = HTTPBearer()


async def verify_firebase_token(
    authorization: HTTPAuthorizationCredentials = Security(http_bearer),
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
) -> UserToken:
    """
    Verifies the Firebase token and returns the decoded token data.
    """
    token = authorization.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        email = decoded_token.get("email")
        if email:
            registration_id_result = await sessions.ro.execute(Emails.select_registration_id_by_email(email))
            rows = registration_id_result.all()
            if not rows:
                raise HTTPException(
                    status_code=401,
                    detail="E-mail is not attached to a registration ID"
                )
            if len(rows) > 1:
                raise HTTPException(
                    status_code=400,
                    detail="Multiple registration IDs found for the provided email"
                )
            registration_id = rows[0][0]
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
    of the required permissions..
    """

    async def dependency(token_data: UserToken = Depends(verify_firebase_token)):
        if isinstance(required_permissions, str):
            reqs = [required_permissions]
        else:
            reqs = required_permissions
        if not any(req in token_data.permissions for req in reqs):
            raise HTTPException(
                status_code=403, detail="Access denied. You don't have the required permission(s)."
            )
        return token_data

    return dependency

def get_registration_id(token_data: UserToken = Depends(verify_firebase_token)) -> int:
    return token_data.registration_id

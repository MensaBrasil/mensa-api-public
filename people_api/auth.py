"""This module contains the authentication logic for the API"""

from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth

http_bearer = HTTPBearer()


def verify_firebase_token(authorization: HTTPAuthorizationCredentials = Security(http_bearer)):
    """Verify the Firebase token and return the decoded token"""
    token = authorization.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        # Catching all exceptions for debugging
        raise HTTPException(status_code=401, detail="Invalid Token") from e

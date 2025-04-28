"""
This module contains tests for authentication and authorization using IAM service.
"""

import asyncio
from datetime import datetime

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from people_api.auth import create_token, verify_firebase_token


def test_auth_permission_valid_role(test_client, mock_valid_token_auth):
    """Test authentication for a role-based permission."""

    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    response = test_client.get("/test/auth-role-valid", headers=headers)
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
    assert response.json() == {"message": "Authenticated with CREATE.EVENT permission"}


def test_auth_permission_invalid_role(test_client, mock_valid_token_auth):
    """Test that a user without the required permission is denied access."""

    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    response = test_client.get("/test/auth-role-invalid", headers=headers)
    assert response.status_code == 403, f"Expected 403 but got {response.status_code}"
    assert "Access denied" in response.json()["detail"]


def test_auth_permission_valid_group(test_client, mock_valid_token_auth):
    """Test authentication for a group-based permission."""

    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    response = test_client.get("/test/auth-group-valid", headers=headers)
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
    assert response.json() == {"message": "Authenticated with WHATSAPP.BOT permission"}


def test_auth_permission_invalid_group(test_client, mock_valid_token_auth):
    """Test that a user without the required permission is denied access."""
    headers = {"Authorization": f"Bearer {mock_valid_token_auth}"}
    response = test_client.get("/test/auth-group-invalid", headers=headers)
    assert response.status_code == 403, f"Expected 403 but got {response.status_code}"
    assert "Access denied" in response.json()["detail"]


def test_create_valid_internal_token_and_verify(sync_rw_session):
    """Test that a token created for (registration_id=5) is valid and contains correct claims."""

    token = create_token(5, ttl=60, session=sync_rw_session)
    compatible_token = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    assert token is not None
    assert isinstance(token, str)
    assert "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9" in token

    decoded_token = asyncio.run(verify_firebase_token(compatible_token))
    assert decoded_token.iss == "mensa_api"
    assert decoded_token.sub == "5"
    assert decoded_token.registration_id == 5
    assert decoded_token.email == "fernando.filho@mensa.org.br"
    assert set(decoded_token.permissions) == {
        "CREATE.EVENT",
        "DELETE.EVENT",
        "WHATSAPP.BOT",
    }
    assert isinstance(decoded_token.exp, datetime)
    assert isinstance(decoded_token.iat, datetime)


def test_create_internal_token_with_invalid_registration_id(sync_rw_session):
    """Test that a token created for an invalid registration_id raises an error."""

    with pytest.raises(HTTPException) as exc_info:
        create_token(9999, ttl=60, session=sync_rw_session)
    assert exc_info.value.status_code == 404
    assert "Registration ID not found" in str(exc_info.value.detail)


def test_create_internal_token_with_invalid_ttl(sync_rw_session):
    """Test that a token created with an invalid TTL raises an error."""

    with pytest.raises(HTTPException) as exc_info:
        create_token(5, ttl=-1, session=sync_rw_session)
    assert exc_info.value.status_code == 400
    assert "TTL (time-to-live) must be a positive integer." in str(exc_info.value.detail)


def test_create_internal_token_without_registration_id(sync_rw_session):
    """Test that a token created without a registration_id has default claims."""

    token = create_token(None, ttl=30, session=sync_rw_session)
    assert token is not None
    assert isinstance(token, str)
    compatible_token = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    decoded_token = asyncio.run(verify_firebase_token(compatible_token))
    assert decoded_token.iss == "mensa_api"
    assert decoded_token.sub == "none"
    assert decoded_token.registration_id is None
    assert decoded_token.email is None
    assert decoded_token.permissions == []
    assert isinstance(decoded_token.exp, datetime)
    assert isinstance(decoded_token.iat, datetime)


def test_create_internal_token_with_zero_ttl(sync_rw_session):
    """Test that a token created with zero TTL raises an error."""

    with pytest.raises(HTTPException) as exc_info:
        create_token(5, ttl=0, session=sync_rw_session)
    assert exc_info.value.status_code == 400
    assert "TTL (time-to-live) must be a positive integer." in str(exc_info.value.detail)


def test_create_internal_token_email_not_found(sync_rw_session, run_db_query):
    """Test that a token is created with email=None if no Mensa email is found."""

    run_db_query(
        """
        DELETE FROM emails WHERE registration_id = 5 AND email_address LIKE '%@mensa.org.br';
        """
    )

    token = create_token(5, ttl=60, session=sync_rw_session)
    compatible_token = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    decoded_token = asyncio.run(verify_firebase_token(compatible_token))
    assert decoded_token.email is None
    assert decoded_token.registration_id == 5
    assert "CREATE.EVENT" in decoded_token.permissions


def test_create_internal_token_permissions_empty(sync_rw_session, mocker):
    """Test that a token is created with empty permissions if none are found."""

    mocker.patch("people_api.services.IamService.get_all_permissions_for_member", return_value=[])
    token = create_token(5, ttl=60, session=sync_rw_session)
    compatible_token = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    decoded_token = asyncio.run(verify_firebase_token(compatible_token))
    assert decoded_token.permissions == []
    assert decoded_token.registration_id == 5
    assert decoded_token.email == "fernando.filho@mensa.org.br"

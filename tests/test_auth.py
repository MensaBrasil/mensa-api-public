"""
This module contains tests for authentication and authorization using IAM service.
"""

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

import time
from unittest.mock import patch

from fastapi.testclient import TestClient

MOCK_API_KEY = "bia"


# Test to verify a valid SQL query
@patch("people_api.services.data_service.API_KEY", MOCK_API_KEY)
def test_valid_query(test_client: TestClient):
    """Test a valid SQL query"""

    response = test_client.post(
        "/data/query",
        json={"query": "SELECT * FROM registration LIMIT 1;"},
        headers={"data_endpoint_token": MOCK_API_KEY},
    )  # noqa: F821
    assert response.status_code == 200
    assert "results" in response.json()


# Test to verify handling of an invalid SQL query
@patch("people_api.services.data_service.API_KEY", MOCK_API_KEY)
def test_invalid_query(test_client: TestClient):
    """Test an invalid SQL query"""
    time.sleep(2)

    response = test_client.post(
        "/data/query",
        headers={"data_endpoint_token": MOCK_API_KEY},
        json={"query": "SELECT * FROM non_existent_table;"},
    )

    assert response.status_code == 400  # Bad Request
    assert "detail" in response.json()


# Test to verify that a read-only constraint is enforced
@patch("people_api.services.data_service.API_KEY", MOCK_API_KEY)
def test_read_only_constraint(test_client: TestClient):
    """Test a write operation in a read-only transaction"""

    response = test_client.post(
        "/data/query",
        headers={"data_endpoint_token": MOCK_API_KEY},
        json={"query": "DROP TABLE emails;"},
    )
    assert response.status_code == 403  # Should fail due to read-only mode
    assert "detail" in response.json()


# Test for failed authentication with an incorrect API key
@patch("people_api.services.data_service.API_KEY", MOCK_API_KEY)
def test_failed_authentication(test_client: TestClient):
    """Test authentication with an incorrect API key"""

    response = test_client.post(
        "/data/query",
        headers={"data_endpoint_token": "wrong_api_key"},
        json={"query": "SELECT * FROM registration LIMIT 1;"},
    )
    assert response.status_code == 403  # Forbidden
    assert response.json()["detail"] == "Could not validate credentials"


# Test for successful authentication with the correct API key
@patch("people_api.services.data_service.API_KEY", MOCK_API_KEY)
def test_successful_authentication(test_client: TestClient):
    """Test authentication with the correct API key"""

    response = test_client.post(
        "/data/query",
        headers={"data_endpoint_token": MOCK_API_KEY},
        json={"query": "SELECT * FROM registration LIMIT 1;"},
    )
    assert response.status_code == 200
    assert "results" in response.json()


# Test for failed authentication when no API key is set
@patch("people_api.services.data_service.API_KEY", None)
def test_failed_authentication_no_api_key(test_client: TestClient):
    """Test authentication failure when the API key is not set"""

    response = test_client.post(
        "/data/query",
        json={"query": "SELECT * FROM registration LIMIT 1;"},
    )
    assert response.status_code == 403  # Forbidden
    assert response.json()["detail"] == "API Key is not set"

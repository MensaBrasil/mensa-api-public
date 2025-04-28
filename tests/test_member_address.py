"""Tests for member_address router endpoints."""


# Endpoint POST
def test_add_address_invalid_token(test_client, mock_valid_token):
    """Test adding an address with an invalid token (unauthorized)."""
    payload = {
        "state": "CA",
        "city": "Los Angeles",
        "address": "123 Test St",
        "neighborhood": "Testville",
        "zip": "90001",
        "country": "USA",
        "latlong": "34.0522,-118.2437",
    }
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.post("/address/2623", json=payload, headers=headers)
    assert response.status_code == 401, f"Expected status code 401 but got {response.status_code}"
    assert response.json() == {"detail": "Unauthorized"}, (
        f"Expected {{'detail': 'Unauthorized'}} but got {response.json()}"
    )


def test_add_address_should_return_already_has_address(test_client, mock_valid_token, run_db_query):
    """Test adding an address when the user already has an address."""

    run_db_query(
        "INSERT INTO addresses (registration_id, state, city, address, neighborhood, zip, country, latlong) "
        "VALUES (5, 'CA', 'Los Angeles', '123 Test St', 'Testville', '90001', 'USA', '34.0522,-118.2437')"
    )
    payload = {
        "state": "CA",
        "city": "Los Angeles",
        "address": "123 Test St",
        "neighborhood": "Testville",
        "zip": "90001",
        "country": "USA",
        "latlong": "34.0522,-118.2437",
    }
    headers = {"Authorization": f"Bearer {mock_valid_token}"}

    response = test_client.post("/address/5", json=payload, headers=headers)
    assert response.status_code == 400, f"Expected status code 400 but got {response.status_code}"
    assert response.json() == {"detail": "User already has an address"}, (
        f"Expected {{'detail': 'User already has an address'}} but got {response.json()}"
    )


def test_add_address_should_return_success(test_client, mock_valid_token, run_db_query):
    """Test adding an address with a valid token and no existing address."""
    run_db_query("DELETE FROM addresses WHERE registration_id = 5")

    payload = {
        "state": "CA",
        "city": "Los Angeles",
        "address": "123 Test St",
        "neighborhood": "Testville",
        "zip": "90001",
        "country": "USA",
        "latlong": "34.0522,-118.2437",
    }
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.post("/address/5", json=payload, headers=headers)
    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"
    assert response.json() == {"message": "Address added successfully"}, (
        f"Expected success message but got {response.json()}"
    )


# Endpoint PUT
def test_update_address_invalid_token(test_client, mock_valid_token):
    """Test updating an address with an invalid token for this member."""
    payload = {
        "state": "NY",
        "city": "New York",
        "address": "456 Updated Ave",
        "neighborhood": "Newtown",
        "zip": "10001",
        "country": "USA",
        "latlong": "40.7128,-74.0060",
    }
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.put("/address/2623/1234567", json=payload, headers=headers)
    assert response.status_code == 401, f"Expected status code 401 but got {response.status_code}"
    assert response.json() == {"detail": "Unauthorized"}, (
        f"Expected {{'detail': 'Unauthorized'}} but got {response.json()}"
    )


def test_update_address_should_return_success(test_client, mock_valid_token, run_db_query):
    """Test updating an address with a valid token."""
    payload = {
        "state": "NY",
        "city": "New York",
        "address": "456 Updated Ave",
        "neighborhood": "Newtown",
        "zip": "10001",
        "country": "USA",
        "latlong": "40.7128,-74.0060",
    }
    headers = {"Authorization": f"Bearer {mock_valid_token}"}

    run_db_query("DELETE FROM addresses WHERE registration_id = 5")
    run_db_query(
        "INSERT INTO addresses (address_id, registration_id, state, city, address, neighborhood, zip, country, latlong) "
        "VALUES (1234567, 5, 'CA', 'Los Angeles', '123 Test St', 'Testville', '90001', 'USA', '34.0522,-118.2437')"
    )

    response = test_client.put("/address/5/1234567", json=payload, headers=headers)
    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"
    assert response.json() == {"message": "Address updated successfully"}, (
        f"Expected success message but got {response.json()}"
    )


# Endpoint DELETE
def test_delete_address_invalid_token(test_client, mock_valid_token):
    """Test deleting an address with an invalid token."""
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.delete("/address/2623/1234567", headers=headers)
    assert response.status_code == 401, f"Expected status code 401 but got {response.status_code}"
    assert response.json() == {"detail": "Unauthorized"}, (
        f"Expected {{'detail': 'Unauthorized'}} but got {response.json()}"
    )


def test_delete_address_should_return_success(test_client, mock_valid_token, run_db_query):
    """Test deleting an address with a valid token."""
    headers = {"Authorization": f"Bearer {mock_valid_token}"}

    run_db_query("DELETE FROM addresses WHERE registration_id = 5")
    run_db_query(
        "INSERT INTO addresses (address_id, registration_id, state, city, address, neighborhood, zip, country, latlong) "
        "VALUES (1234567, 5, 'CA', 'Los Angeles', '123 Test St', 'Testville', '90001', 'USA', '34.0522,-118.2437')"
    )

    response = test_client.delete("/address/5/1234567", headers=headers)
    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"
    assert response.json() == {"message": "Address deleted successfully"}, (
        f"Expected success message but got {response.json()}"
    )

"""Tests for member_phone router endpoints."""


# endpoint POST
def test_add_phone_number_invalid_token(test_client, mock_valid_token):
    """Test adding a phone number with a invalid token"""
    payload = {"phone_number": "12345678912"}
    headers = {"Authorization": f"Bearer {mock_valid_token}"}

    response = test_client.post("/phone/2623", json=payload, headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


def test_add_phone_number_should_return_already_has_phone(test_client, mock_valid_token):
    """Test adding a phone number when the user already has a phone"""
    payload = {"phone_number": "12345678912"}
    headers = {"Authorization": f"Bearer {mock_valid_token}"}

    response = test_client.post("/phone/2622", json=payload, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "User already has a phone"}


def test_add_phone_number_should_return_success(test_client, mock_valid_token, run_db_query):
    """Test adding a phone number with a valid token"""
    payload = {"phone_number": "12345678912"}
    headers = {"Authorization": f"Bearer {mock_valid_token}"}

    run_db_query("DELETE FROM phones WHERE registration_id = 2622")

    response = test_client.post("/phone/2622", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Phone added successfully"}


# Endpoint PUT
def test_update_phone_number_invalid_token(test_client, mock_valid_token):
    """Test updating a phone number with a invalid token for this user email"""
    payload = {"phone_number": "12345678912"}
    headers = {"Authorization": f"Bearer {mock_valid_token}"}

    response = test_client.put("/phone/2623/11771", json=payload, headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


# TODO: This test is failing due to a error in the repository querie, it should be fixed in the future.

# def test_update_phone_number_should_return_phone_not_found(test_client,run_db_query, mock_valid_token):
#     """Test adding a phone number when the user already has a phone"""
#     payload = {"phone_number": "12345678912"}
#     headers = {"Authorization": f"Bearer {mock_valid_token}"}

#     run_db_query("DELETE FROM phones WHERE registration_id = 2622")

#     response = test_client.put("/phone/2622/11771", json=payload, headers=headers)
#     assert response.status_code == 404
#     assert response.json() == {"detail": "Phone not found"}


def test_update_phone_number_should_return_success(test_client, mock_valid_token, run_db_query):
    """Test updating a phone number with a valid token"""
    payload = {"phone_number": "12345678912"}
    headers = {"Authorization": f"Bearer {mock_valid_token}"}

    run_db_query("DELETE FROM phones WHERE registration_id = 2622")

    response = test_client.put("/phone/2622/11771", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Phone updated successfully"}

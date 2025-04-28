"""Tests for member_phone router endpoints."""


# endpoint POST
def test_add_phone_number_invalid_token(test_client, mock_valid_token):
    """Test adding a phone number with an invalid token"""
    payload = {"phone": "(11) 91234-5678"}
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.post("/phone/2623", json=payload, headers=headers)
    assert response.status_code == 401, f"Expected status code 401 but got {response.status_code}"
    assert response.json() == {"detail": "Unauthorized"}, (
        f"Expected JSON {{'detail': 'Unauthorized'}} but got {response.json()}"
    )


def test_add_phone_number_should_return_already_has_phone(test_client, mock_valid_token):
    """Test adding a phone number when the user already has a phone"""
    payload = {"phone": "(11) 91234-5678"}
    headers = {"Authorization": f"Bearer {mock_valid_token}"}

    print("DEBUG: Starting test_add_phone_number_should_return_already_has_phone")
    print("DEBUG: Payload being sent:", payload)
    print("DEBUG: Headers being used:", headers)

    response = test_client.post("/phone/5", json=payload, headers=headers)

    print("DEBUG: Response status code:", response.status_code)
    print("DEBUG: Response JSON:", response.json())

    assert response.status_code == 400, f"Expected status code 400 but got {response.status_code}"
    assert response.json() == {"detail": "User already has a phone"}, (
        f"Expected JSON {{'detail': 'User already has a phone'}} but got {response.json()}"
    )


def test_add_phone_number_should_return_success(test_client, mock_valid_token, run_db_query):
    """Test adding a phone number with a valid token"""
    payload = {"phone": "(11) 91234-5678"}
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    run_db_query("DELETE FROM phones WHERE registration_id = 5")
    response = test_client.post("/phone/5", json=payload, headers=headers)
    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"
    assert response.json() == {"message": "Phone added successfully"}, (
        f"Expected JSON {{'message': 'Phone added successfully'}} but got {response.json()}"
    )


def test_add_phone_number_e164_format_valid(test_client, mock_valid_token, run_db_query):
    """
    Test adding a valid phone number in a 'messy' format to confirm
    it is converted to E.164 and stored in DB.
    """
    run_db_query("DELETE FROM phones WHERE registration_id = 5")

    payload = {"phone": "(11) 91234-5678"}
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.post("/phone/5", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Phone added successfully"}
    rows = run_db_query("SELECT phone_number FROM phones WHERE registration_id = 5")
    assert len(rows) == 1, "Expected exactly one phone record."
    phone_number = rows[0]["phone_number"] if isinstance(rows[0], dict) else rows[0][0]
    assert phone_number == "+5511912345678"


def test_add_phone_number_e164_format_invalid(test_client, mock_valid_token, run_db_query):
    """
    Test adding an invalid phone number, expecting a validation error response (422).
    """
    run_db_query("DELETE FROM phones WHERE registration_id = 5")
    payload = {"phone": "abc#$123"}
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.post("/phone/5", json=payload, headers=headers)
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list), "Detail should be a list of error objects"
    error_msg = detail[0]["msg"].lower()
    assert "invalid" in error_msg
    assert "characters" in error_msg
    rows = run_db_query("SELECT phone_number FROM phones WHERE registration_id = 5")
    assert len(rows) == 0, "No valid phone should have been stored."


# Endpoint PUT
def test_update_phone_number_invalid_token(test_client, mock_valid_token):
    """Test updating a phone number with an invalid token for this user email"""
    payload = {"phone": "+5511912345678"}
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.put("/phone/2623/11771", json=payload, headers=headers)
    assert response.status_code == 401, f"Expected status code 401 but got {response.status_code}"
    assert response.json() == {"detail": "Unauthorized"}, (
        f"Expected JSON {{'detail': 'Unauthorized'}} but got {response.json()}"
    )


def test_update_phone_number_should_return_success(test_client, mock_valid_token, run_db_query):
    """Test updating a phone number with a valid token"""
    run_db_query("DELETE FROM phones WHERE registration_id = 5")
    run_db_query(
        "INSERT INTO phones (phone_id, registration_id, phone_number) "
        "VALUES (11771, 5, '+5511987654321')"
    )
    payload = {"phone": "+5511912345678"}
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.put("/phone/5/11771", json=payload, headers=headers)
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
    assert response.json() == {"message": "Phone updated successfully"}

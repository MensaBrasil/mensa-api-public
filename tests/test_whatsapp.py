from typing import Any
from unittest.mock import patch

from fastapi.testclient import TestClient

MOCK_API_KEY = "bia"


@patch("people_api.services.whatsapp_service.API_KEY", MOCK_API_KEY)
def test_update_phone_with_valid_data_or_invalid_data(
    test_client: TestClient, run_db_query: Any
) -> None:
    """Test updating a member's phone number when birth_date and CPF are valid"""

    run_db_query(
        """
        UPDATE registration
        SET cpf = '12345678909', birth_date = '1991-01-01', deceased = false
        WHERE registration_id IN (
            SELECT registration_id FROM emails WHERE email_address = 'fernando.filho@mensa.org.br'
        )
    """
    )

    registration_id = run_db_query(
        "SELECT registration_id FROM emails WHERE email_address = 'fernando.filho@mensa.org.br'"
    )[0][0]

    # Invalid CPF test case
    payload = {
        "phone": "1234567890",
        "birth_date": "01/01/1991",
        "cpf": "11111111111",  
        "registration_id": registration_id,
        "is_representative": False,
        "token": MOCK_API_KEY,  # Add the token in the body
    }

    response = test_client.post("/whatsapp/update-data", json=payload)
    assert response.status_code == 400

    # Valid CPF test case
    payload = {
        "phone": "1234567890",
        "birth_date": "01/01/1991",
        "cpf": "12345678909",  # Valid CPF
        "registration_id": registration_id,
        "is_representative": False,
        "token": MOCK_API_KEY,  # Add the token in the body
    }

    response = test_client.post("/whatsapp/update-data", json=payload)

    # Debugging output
    print("Response status code:", response.status_code)
    print("Response content:", response.json())

    assert response.status_code == 200
    assert response.json() == {"message": "Phone number updated successfully."}

    updated_phone = run_db_query(
        """
        SELECT phone_number FROM phones
        WHERE registration_id IN (
            SELECT registration_id FROM emails WHERE email_address = 'fernando.filho@mensa.org.br'
        )
    """
    )
    assert updated_phone == [("1234567890",)]


@patch("people_api.services.whatsapp_service.API_KEY", MOCK_API_KEY)
def test_update_phone_for_representative_with_valid_data_or_invalid_data(
    test_client: TestClient, run_db_query: Any
) -> None:
    """Test updating a representative's phone number when CPF is valid"""

    # Clean and seed the database
    run_db_query(
        """
        DELETE FROM legal_representatives
        WHERE registration_id IN (
            SELECT registration_id FROM emails WHERE email_address = 'fernando.filho@mensa.org.br'
        )
    """
    )

    run_db_query(
        """
        INSERT INTO legal_representatives (registration_id, cpf, full_name, phone, alternative_phone)
        VALUES (
            (SELECT registration_id FROM emails WHERE email_address = 'fernando.filho@mensa.org.br'),
            '98765432100',
            'Test Legal Rep',
            '1234567890',
            '1234567890'
        )
    """
    )

    # Fetch registration_id
    registration_id = run_db_query(
        "SELECT registration_id FROM emails WHERE email_address = 'fernando.filho@mensa.org.br'"
    )[0][0]

    print("Fetched registration_id:", registration_id)

    # Payload
    payload = {
        "phone": "0987654321",
        "birth_date": None,  # Ensure None is valid or provide a date
        "cpf": "98765432100",  # Adjust format if needed
        "registration_id": registration_id,
        "is_representative": True,
        "token": MOCK_API_KEY,  # Adjust if token should be a header
    }

    # Send request
    response = test_client.post("/whatsapp/update-data", json=payload)

    # Log response
    print("Response status code:", response.status_code)
    print("Response JSON:", response.json())

    # Assertions
    assert response.status_code == 200
    assert response.json() == {"message": "Representative's phone number updated successfully."}


@patch("people_api.services.whatsapp_service.API_KEY", MOCK_API_KEY)
def test_update_phone_with_wrong_api_key(test_client: TestClient, run_db_query: Any):
    """Test updating a member's phone number with an incorrect API key."""

    run_db_query(
        """
        UPDATE registration
        SET cpf = '12345678909', birth_date = '01/01/1991', deceased = false
        WHERE registration_id IN (
            SELECT registration_id FROM emails WHERE email_address = 'fernando.filho@mensa.org.br'
        )
    """
    )

    registration_id = run_db_query(
        "SELECT registration_id FROM emails WHERE email_address = 'fernando.filho@mensa.org.br'"
    )[0][0]

    # Test case with wrong API key in the payload
    payload = {
        "phone": "1234567890",
        "birth_date": "01/01/1991",
        "cpf": "12345678909",
        "registration_id": registration_id,
        "is_representative": False,
        "token": "wrong_api_key",  # Wrong API key
    }

    response = test_client.post("/whatsapp/update-data", json=payload)
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid API Key"

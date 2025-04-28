"""Integration tests for /whatsapp/update-data endpoint"""

import os
from typing import Any
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

MOCK_API_KEY = "bia"

os.environ["OPENAI_API_KEY"] = "dummy_openai_key"

dummy_threads = MagicMock()
dummy_threads.create.return_value = MagicMock(id="dummy_thread_id")


@patch("people_api.services.whatsapp_service.utils.API_KEY", MOCK_API_KEY)
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

    payload = {
        "phone": "1234567890",
        "birth_date": "01/01/1991",
        "cpf": "11111111111",
        "registration_id": registration_id,
        "is_representative": False,
        "token": MOCK_API_KEY,
    }

    response = test_client.post("/whatsapp/update-data", json=payload)
    assert response.status_code == 400

    payload = {
        "phone": "1234567890",
        "birth_date": "01/01/1991",
        "cpf": "12345678909",
        "registration_id": registration_id,
        "is_representative": False,
        "token": MOCK_API_KEY,
    }

    response = test_client.post("/whatsapp/update-data", json=payload)

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


@patch("people_api.services.whatsapp_service.utils.API_KEY", MOCK_API_KEY)
def test_update_phone_for_representative_with_valid_data_or_invalid_data(
    test_client: TestClient, run_db_query: Any
) -> None:
    """Test updating a representative's phone number when CPF is valid"""

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

    registration_id = run_db_query(
        "SELECT registration_id FROM emails WHERE email_address = 'fernando.filho@mensa.org.br'"
    )[0][0]

    print("Fetched registration_id:", registration_id)

    payload = {
        "phone": "0987654321",
        "birth_date": None,
        "cpf": "98765432100",
        "registration_id": registration_id,
        "is_representative": True,
        "token": MOCK_API_KEY,
    }

    response = test_client.post("/whatsapp/update-data", json=payload)

    assert response.status_code == 200
    assert response.json() == {"message": "Representative's phone number updated successfully."}


@patch("people_api.services.whatsapp_service.utils.API_KEY", MOCK_API_KEY)
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

    payload = {
        "phone": "1234567890",
        "birth_date": "01/01/1991",
        "cpf": "12345678909",
        "registration_id": registration_id,
        "is_representative": False,
        "token": "wrong_api_key",
    }

    response = test_client.post("/whatsapp/update-data", json=payload)
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid API Key"

import os
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

MOCK_API_KEY = "bia"

os.environ["OPENAI_API_KEY"] = "dummy_openai_key"

dummy_threads = MagicMock()
dummy_threads.create.return_value = MagicMock(id="dummy_thread_id")


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


@patch("people_api.services.whatsapp_service.API_KEY", MOCK_API_KEY)
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


@patch(
    "people_api.services.twilio_service.TwilioService.send_whatsapp_message",
    new_callable=AsyncMock,
    return_value=None,
)
@patch(
    "people_api.services.whatsapp_service.openai_client",
    new=MagicMock(
        beta=MagicMock(
            threads=AsyncMock(create=AsyncMock(return_value=MagicMock(id="dummy_thread_id")))
        )
    ),
)
@patch("people_api.services.whatsapp_service.API_KEY", MOCK_API_KEY)
def test_chatbot_message_valid(mock_twilio, run_db_query, test_client: TestClient):
    """
    Integration test for /whatsapp/chatbot-message with a valid member (registration id 5).
    Expected: 200 response.
    """

    run_db_query(
        """
        INSERT INTO membership_payments (registration_id, payment_date, expiration_date, amount_paid, observation, payment_method, transaction_id, payment_status)
        VALUES (
            5,
            CURRENT_DATE,
            CURRENT_DATE + INTERVAL '1 year',
            100.00,
            'Test Payment for reg ',
            'Credit Card',
            'TX456',
            'active'
        )
        """
    )

    payload = {
        "SmsMessageSid": "SM123",
        "NumMedia": "0",
        "ProfileName": "TestUser",
        "MessageType": "text",
        "SmsSid": "SM123",
        "WaId": "0000000097654322",
        "SmsStatus": "received",
        "Body": "Hello from registration 5",
        "To": "whatsapp:+10000000000",
        "MessagingServiceSid": "MG123",
        "NumSegments": "1",
        "ReferralNumMedia": "0",
        "MessageSid": "SM123",
        "AccountSid": "AC123",
        "From": "whatsapp:+552197654322",
        "ApiVersion": "2010-04-01",
    }
    response = test_client.post("/whatsapp/chatbot-message", data=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    result = response.json()
    assert isinstance(result, str), "Expected the chatbot response to be a string"


@patch("people_api.services.whatsapp_service.API_KEY", MOCK_API_KEY)
def test_chatbot_message_missing_phone(test_client: TestClient):
    """
    Integration test for /whatsapp/chatbot-message when no phone record is found.
    Expected: 404 response.
    """
    payload = {
        "SmsMessageSid": "SM124",
        "NumMedia": "0",
        "ProfileName": "TestUser",
        "MessageType": "text",
        "SmsSid": "SM124",
        "WaId": "0000000099999999",
        "SmsStatus": "received",
        "Body": "Hello, no phone!",
        "To": "whatsapp:+10000000000",
        "MessagingServiceSid": "MG124",
        "NumSegments": "1",
        "ReferralNumMedia": "0",
        "MessageSid": "SM124",
        "AccountSid": "AC124",
        "From": "whatsapp:+0000000000",
        "ApiVersion": "2010-04-01",
    }
    response = test_client.post("/whatsapp/chatbot-message", data=payload)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    error_detail = response.json().get("detail", "")
    assert "Member not found" in error_detail, f"Unexpected error detail: {error_detail}"



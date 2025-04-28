"""Integration tests for the WhatsApp chatbot message validation endpoint."""

from unittest.mock import AsyncMock, patch


def test_chatbot_validation_member_not_found(test_client):
    """
    Integration test for /whatsapp/chatbot-message with a phone number not attached to a member.
    """

    payload = {
        "SmsMessageSid": "SM123",
        "NumMedia": "0",
        "ProfileName": "TestUser",
        "MessageType": "text",
        "SmsSid": "SM123",
        "WaId": "5500221354565",
        "SmsStatus": "received",
        "Body": "Hello!!",
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
    assert response.status_code == 404
    assert response.json()["detail"] == "Member not found"


def test_chatbot_validation_payment_expired(test_client):
    """
    Integration test for /whatsapp/chatbot-message with a phone number attached to a member
    but with an expired payment.
    """

    payload = {
        "SmsMessageSid": "SM123",
        "NumMedia": "0",
        "ProfileName": "TestUser",
        "MessageType": "text",
        "SmsSid": "SM123",
        "WaId": "552198765432",
        "SmsStatus": "received",
        "Body": "Hello!! I'm member with reg id 6!",
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
    assert response.status_code == 403
    assert response.json()["detail"] == "Member is not active"


def test_chatbot_validation_member_active(test_client):
    """
    Integration test for /whatsapp/chatbot-message with a phone number attached to an active member.
    """

    payload = {
        "SmsMessageSid": "SM123",
        "NumMedia": "0",
        "ProfileName": "TestUser",
        "MessageType": "text",
        "SmsSid": "SM123",
        "WaId": "552199876543",
        "SmsStatus": "received",
        "Body": "Hello!! I'm member with reg id 7!",
        "To": "whatsapp:+10000000000",
        "MessagingServiceSid": "MG123",
        "NumSegments": "1",
        "ReferralNumMedia": "0",
        "MessageSid": "SM123",
        "AccountSid": "AC123",
        "From": "whatsapp:+552199876543",
        "ApiVersion": "2010-04-01",
    }

    with patch(
        "people_api.services.whatsapp_service.chatbot.client.WhatsappChatBot.chatbot_message",
        new_callable=AsyncMock,
    ) as mock_chatbot_message:
        mock_chatbot_message.return_value = {"message": "Welcome!"}
        response = test_client.post("/whatsapp/chatbot-message", data=payload)
        assert response.status_code == 200
        assert "Welcome" in response.json()["message"]
        mock_chatbot_message.assert_awaited_once()

"""Integration tests for the WhatsApp chatbot message Client."""

from unittest.mock import AsyncMock, patch

valid_payload = {
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


def test_chatbot_reset_command_success(test_client):
    """
    Integration test for /whatsapp/chatbot-message with a phone number attached to an active member.
    """
    reset_payload = valid_payload.copy()
    reset_payload["Body"] = "!reset"

    with patch(
        "people_api.services.whatsapp_service.chatbot.client.TwilioService.send_whatsapp_message",
        new_callable=AsyncMock,
    ) as mock_send:
        response = test_client.post("/whatsapp/chatbot-message", data=reset_payload)
        assert response.status_code == 200
        assert response.json() == "Thread reset successfully!"
        mock_send.assert_awaited_once_with(
            to_=reset_payload["From"], message="Thread reset successfully!"
        )

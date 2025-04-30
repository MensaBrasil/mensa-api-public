"""Integration tests for the WhatsApp chatbot thread handler."""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from people_api.services.whatsapp_service.chatbot.thread_handler import ThreadService

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


@pytest.mark.asyncio
async def test_chatbot_create_new_thread_when_no_thread_exists(test_client):
    """
    Integration test for /whatsapp/chatbot-message with a phone number not attached to an active member.
    """
    new_thread_payload = valid_payload.copy()
    new_thread_payload["Body"] = "Hello, chatbot!"

    with (
        patch(
            "people_api.services.whatsapp_service.chatbot.thread_handler.openai_client.beta.threads.create",
            new_callable=AsyncMock,
        ) as mock_openai_create_thread,
        patch(
            "people_api.services.whatsapp_service.chatbot.thread_handler.get_member_info_by_phone_number",
            new_callable=AsyncMock,
        ) as mock_get_member_info,
        patch(
            "people_api.services.whatsapp_service.chatbot.thread_handler.openai_client.beta.threads.messages.create",
            new_callable=AsyncMock,
        ) as mock_openai_create_message,
        patch(
            "people_api.services.whatsapp_service.chatbot.client.MessageHandler.process_message",
            new_callable=AsyncMock,
        ) as mock_process_message,
        patch(
            "people_api.services.whatsapp_service.chatbot.client.TwilioService.send_whatsapp_message",
            new_callable=AsyncMock,
        ) as mock_send,
    ):
        # Mock OpenAI thread creation
        mock_thread_obj = AsyncMock()
        mock_thread_obj.id = "mock_thread_id"
        mock_openai_create_thread.return_value = mock_thread_obj
        mock_get_member_info.return_value = None  # Simulate user not found
        mock_process_message.return_value = (
            "Hello, user! I'm the mensa chatbot. How can I assist you today?"
        )

        response = test_client.post("/whatsapp/chatbot-message", data=new_thread_payload)
        assert response.status_code == 200
        assert response.json() == "Hello, user! I'm the mensa chatbot. How can I assist you today?"
        mock_openai_create_thread.assert_awaited_once()
        mock_openai_create_message.assert_awaited_once()
        mock_process_message.assert_awaited_once()
        mock_send.assert_awaited_once_with(
            to_=new_thread_payload["From"],
            message="Hello, user! I'm the mensa chatbot. How can I assist you today?",
        )


@pytest.mark.asyncio
async def test_chatbot_resume_already_existent_thread(test_client):
    """
    Integration test for /whatsapp/chatbot-message with a phone number attached to an active member and existing thread.
    """
    existing_thread_payload = valid_payload.copy()
    existing_thread_payload["Body"] = "Hello, chatbot!"

    # Simulate an existing thread and message count
    phone_number = existing_thread_payload["WaId"]
    ThreadService.threads_by_phone[phone_number] = "existing_thread_id"
    ThreadService.message_counts[phone_number] = {"existing_thread_id": 1}

    with (
        patch(
            "people_api.services.whatsapp_service.chatbot.client.MessageHandler.process_message",
            new_callable=AsyncMock,
        ) as mock_process_message,
        patch(
            "people_api.services.whatsapp_service.chatbot.client.TwilioService.send_whatsapp_message",
            new_callable=AsyncMock,
        ) as mock_send,
    ):
        mock_process_message.return_value = (
            "Hello, user! I'm the mensa chatbot. How can I assist you today?"
        )

        response = test_client.post("/whatsapp/chatbot-message", data=existing_thread_payload)
        assert response.status_code == 200
        assert response.json() == "Hello, user! I'm the mensa chatbot. How can I assist you today?"
        mock_process_message.assert_awaited_once()
        mock_send.assert_awaited_once_with(
            to_=existing_thread_payload["From"],
            message="Hello, user! I'm the mensa chatbot. How can I assist you today?",
        )

    ThreadService.threads_by_phone.pop(phone_number, None)
    ThreadService.message_counts.pop(phone_number, None)


@pytest.mark.asyncio
async def test_check_message_length_raises_on_long_message():
    """Test that check_message_length raises ValueError for messages longer than 150 characters."""
    long_message = "a" * 151
    with pytest.raises(ValueError) as exc:
        ThreadService.check_message_length(long_message)
    assert "O limite máximo de 150 caracteres" in str(exc.value)


@pytest.mark.asyncio
async def test_check_message_length_allows_short_message():
    """Test that check_message_length does not raise for messages shorter than 150 characters."""
    short_message = "a" * 150
    # Should not raise
    ThreadService.check_message_length(short_message)


def test_check_thread_creation_limit_raises_when_limit_exceeded():
    """Test that check_thread_creation_limit raises ValueError when the limit is exceeded."""
    phone_number = "123"
    today = datetime.now()
    ThreadService.thread_timestamps[phone_number] = [today] * 5
    with pytest.raises(ValueError) as exc:
        ThreadService.check_thread_creation_limit(phone_number)
    assert "O limite máximo de sessões por dia" in str(exc.value)
    ThreadService.thread_timestamps.pop(phone_number, None)


def test_check_thread_creation_limit_allows_within_limit():
    """Test that check_thread_creation_limit does not raise when within limit."""
    phone_number = "123"
    today = datetime.now()
    ThreadService.thread_timestamps[phone_number] = [today] * 4
    # Should not raise
    ThreadService.check_thread_creation_limit(phone_number)
    ThreadService.thread_timestamps.pop(phone_number, None)


def test_record_message_increments_count():
    """Test that record_message increments the message count for a thread."""
    phone_number = "555"
    thread_id = "thread1"
    message = "hello"
    ThreadService.message_counts.pop(phone_number, None)
    ThreadService.record_message(phone_number, thread_id, message)
    assert ThreadService.message_counts[phone_number][thread_id] == 1
    ThreadService.record_message(phone_number, thread_id, message)
    assert ThreadService.message_counts[phone_number][thread_id] == 2
    ThreadService.message_counts.pop(phone_number, None)


@pytest.mark.asyncio
async def test_get_or_create_thread_creates_new_thread_when_limit_not_reached(
    monkeypatch,
):
    """Test that get_or_create_thread creates a new thread when the limit is not reached."""
    phone_number = "999"
    session = AsyncMock()
    ThreadService.threads_by_phone.pop(phone_number, None)
    ThreadService.message_counts.pop(phone_number, None)
    ThreadService.thread_timestamps.pop(phone_number, None)

    mock_thread = AsyncMock()
    mock_thread.id = "new_thread_id"
    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.thread_handler.openai_client.beta.threads.create",
        AsyncMock(return_value=mock_thread),
    )
    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.thread_handler.get_member_info_by_phone_number",
        AsyncMock(return_value=None),
    )
    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.thread_handler.openai_client.beta.threads.messages.create",
        AsyncMock(),
    )

    thread_id = await ThreadService.get_or_create_thread(phone_number, session)
    assert thread_id == "new_thread_id"
    assert ThreadService.threads_by_phone[phone_number] == "new_thread_id"
    assert ThreadService.message_counts[phone_number]["new_thread_id"] == 0
    assert len(ThreadService.thread_timestamps[phone_number]) == 1

    ThreadService.threads_by_phone.pop(phone_number, None)
    ThreadService.message_counts.pop(phone_number, None)
    ThreadService.thread_timestamps.pop(phone_number, None)


@pytest.mark.asyncio
async def test_get_or_create_thread_returns_existing_if_under_15():
    """Test that get_or_create_thread returns existing thread if under 15 messages."""
    phone_number = "888"
    session = AsyncMock()
    ThreadService.threads_by_phone[phone_number] = "existing_thread"
    ThreadService.message_counts[phone_number] = {"existing_thread": 10}

    thread_id = await ThreadService.get_or_create_thread(phone_number, session)
    assert thread_id == "existing_thread"

    ThreadService.threads_by_phone.pop(phone_number, None)
    ThreadService.message_counts.pop(phone_number, None)


@pytest.mark.asyncio
async def test_get_or_create_thread_raises_http_exception_on_thread_limit(monkeypatch):
    """Test that get_or_create_thread raises HTTPException when the thread limit is reached."""
    phone_number = "777"
    session = AsyncMock()
    ThreadService.threads_by_phone[phone_number] = "existing_thread"
    ThreadService.message_counts[phone_number] = {"existing_thread": 15}
    ThreadService.thread_timestamps[phone_number] = [datetime.now()] * 5

    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.thread_handler.openai_client.beta.threads.create",
        AsyncMock(),
    )
    with pytest.raises(HTTPException) as exc:
        await ThreadService.get_or_create_thread(phone_number, session)
    assert exc.value.status_code == 429

    ThreadService.threads_by_phone.pop(phone_number, None)
    ThreadService.message_counts.pop(phone_number, None)
    ThreadService.thread_timestamps.pop(phone_number, None)

"""Integration tests for the WhatsApp chatbot message handler endpoint."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from people_api.services.whatsapp_service.chatbot.message_handler import MessageHandler


@pytest.mark.asyncio
async def test_process_message_success(monkeypatch):
    """Test process_message returns assistant response on success."""
    thread_id = "thread123"
    message = "Hello!"
    registration_id = 7

    # Mock openai_client.beta.threads.messages.create
    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.message_handler.openai_client.beta.threads.messages.create",
        AsyncMock(),
    )

    # Mock run object and create_and_poll
    run_mock = MagicMock()
    run_mock.status = "completed"
    run_mock.required_action = None
    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.message_handler.openai_client.beta.threads.runs.create_and_poll",
        AsyncMock(return_value=run_mock),
    )

    # Mock messages_response for assistant reply
    last_message_mock = MagicMock()
    last_message_mock.role = "assistant"
    last_message_mock.content = [MagicMock()]
    last_message_mock.content[0].text = MagicMock()
    last_message_mock.content[0].text.value = "Hello, how can I help you?"
    messages_response_mock = MagicMock()
    messages_response_mock.data = [last_message_mock]
    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.message_handler.openai_client.beta.threads.messages.list",
        AsyncMock(return_value=messages_response_mock),
    )

    # Patch get_settings
    settings_mock = MagicMock()
    settings_mock.chatgpt_assistant_id = "assistant_id"
    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.message_handler.get_settings",
        lambda: settings_mock,
    )

    # Patch ToolCallService
    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.message_handler.ToolCallService.handle_tool_calls",
        AsyncMock(return_value=run_mock),
    )

    response = await MessageHandler.process_message(thread_id, message, registration_id)
    assert response == "Hello, how can I help you?"


@pytest.mark.asyncio
async def test_process_message_requires_action(monkeypatch):
    """Test process_message handles requires_action and completes."""
    thread_id = "thread456"
    message = "Test"
    registration_id = 8

    # Mock openai_client.beta.threads.messages.create
    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.message_handler.openai_client.beta.threads.messages.create",
        AsyncMock(),
    )

    # Simulate requires_action then completed
    run_requires_action = MagicMock()
    run_requires_action.status = "requires_action"
    run_requires_action.required_action = True
    run_completed = MagicMock()
    run_completed.status = "completed"
    run_completed.required_action = None

    create_and_poll_mock = AsyncMock(side_effect=[run_requires_action, run_completed])
    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.message_handler.openai_client.beta.threads.runs.create_and_poll",
        create_and_poll_mock,
    )

    # Patch ToolCallService to return completed run
    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.message_handler.ToolCallService.handle_tool_calls",
        AsyncMock(return_value=run_completed),
    )

    # Patch get_settings
    settings_mock = MagicMock()
    settings_mock.chatgpt_assistant_id = "assistant_id"
    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.message_handler.get_settings",
        lambda: settings_mock,
    )

    # Mock messages_response for assistant reply
    last_message_mock = MagicMock()
    last_message_mock.role = "assistant"
    last_message_mock.content = [MagicMock()]
    last_message_mock.content[0].text = MagicMock()
    last_message_mock.content[0].text.value = "Tool action reply"
    messages_response_mock = MagicMock()
    messages_response_mock.data = [last_message_mock]
    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.message_handler.openai_client.beta.threads.messages.list",
        AsyncMock(return_value=messages_response_mock),
    )

    response = await MessageHandler.process_message(thread_id, message, registration_id)
    assert response == "Tool action reply"


@pytest.mark.asyncio
async def test_process_message_no_assistant_response(monkeypatch):
    """Test process_message raises ValueError if no assistant response."""
    thread_id = "thread789"
    message = "No assistant"
    registration_id = 9

    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.message_handler.openai_client.beta.threads.messages.create",
        AsyncMock(),
    )

    run_mock = MagicMock()
    run_mock.status = "completed"
    run_mock.required_action = None
    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.message_handler.openai_client.beta.threads.runs.create_and_poll",
        AsyncMock(return_value=run_mock),
    )

    # Patch get_settings
    settings_mock = MagicMock()
    settings_mock.chatgpt_assistant_id = "assistant_id"
    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.message_handler.get_settings",
        lambda: settings_mock,
    )

    # Patch ToolCallService
    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.message_handler.ToolCallService.handle_tool_calls",
        AsyncMock(return_value=run_mock),
    )

    # No assistant message in data
    messages_response_mock = MagicMock()
    messages_response_mock.data = []
    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.message_handler.openai_client.beta.threads.messages.list",
        AsyncMock(return_value=messages_response_mock),
    )

    response = await MessageHandler.process_message(thread_id, message, registration_id)
    assert response == "Erro ao processar mensagem, tente novamente mais tarde..."


@pytest.mark.asyncio
async def test_process_message_exception(monkeypatch):
    """Test process_message returns error message on exception."""
    thread_id = "thread999"
    message = "error"
    registration_id = 10

    # Patch messages.create to raise exception
    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.message_handler.openai_client.beta.threads.messages.create",
        AsyncMock(side_effect=Exception("Some error")),
    )

    response = await MessageHandler.process_message(thread_id, message, registration_id)
    assert response == "Erro ao processar mensagem, tente novamente mais tarde..."

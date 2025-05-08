"""Tests for the tool_calls_handler module"""

import json
from types import SimpleNamespace

import pytest

from people_api.services.whatsapp_service.chatbot.tool_calls_handler import (
    FunctionCall,
    ToolCallService,
)


@pytest.mark.asyncio
async def test_handle_create_email(monkeypatch):
    """Test if the ToolCallService.handle_tool_calls processes a CREATE_EMAIL call correctly."""

    tool_call = SimpleNamespace(
        id="1", function=SimpleNamespace(name=FunctionCall.CREATE_EMAIL, arguments="{}")
    )

    run = SimpleNamespace(
        id="r",
        thread_id="t",
        required_action=SimpleNamespace(
            submit_tool_outputs=SimpleNamespace(tool_calls=[tool_call])
        ),
    )

    registration_id = 99

    async def fake_create_email_request(registration_id: int):
        return {
            "message": "Mensa email created successfully",
            "user_data": {"email": "x@dominio", "password": "senha123"},
            "information": "User will be prompted to change the password at the first login.",
        }

    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.tool_calls_handler.create_email_request",
        fake_create_email_request,
    )

    called = {}

    async def fake_submit(thread_id: str, run_id: str, tool_outputs: list):
        called["args"] = (thread_id, run_id, tool_outputs)
        return run

    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.tool_calls_handler.openai_client.beta.threads.runs.submit_tool_outputs",
        fake_submit,
    )

    result = await ToolCallService.handle_tool_calls(
        run,  # type: ignore
        registration_id,
    )

    assert result is run
    thread_id, run_id, tool_outputs = called["args"]
    assert thread_id == "t"
    assert run_id == "r"
    assert len(tool_outputs) == 1

    to = tool_outputs[0]
    assert isinstance(to, dict)
    assert to["tool_call_id"] == "1"
    assert json.loads(to["output"]) == {
        "message": "Mensa email created successfully",
        "user_data": {"email": "x@dominio", "password": "senha123"},
        "information": "User will be prompted to change the password at the first login.",
    }


@pytest.mark.asyncio
async def test_handle_recover_email_password(monkeypatch):
    """Test if the ToolCallService.handle_tool_calls processes a RECOVER_EMAIL_PASSWORD call correctly."""

    tool_call = SimpleNamespace(
        id="2", function=SimpleNamespace(name=FunctionCall.RECOVER_EMAIL_PASSWORD, arguments="{}")
    )

    run = SimpleNamespace(
        id="r2",
        thread_id="t2",
        required_action=SimpleNamespace(
            submit_tool_outputs=SimpleNamespace(tool_calls=[tool_call])
        ),
    )

    registration_id = 123

    async def fake_recover_email_password_request(registration_id: int):
        return {
            "message": "Password reset successfully",
            "user_data": {"email": "x@dominio", "password": "nova_senha"},
            "information": "User will be prompted to change the password at the first login.",
        }

    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.tool_calls_handler.recover_email_password_request",
        fake_recover_email_password_request,
    )

    called = {}

    async def fake_submit(thread_id: str, run_id: str, tool_outputs: list):
        called["args"] = (thread_id, run_id, tool_outputs)
        return run

    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.tool_calls_handler.openai_client.beta.threads.runs.submit_tool_outputs",
        fake_submit,
    )

    result = await ToolCallService.handle_tool_calls(
        run,  # type: ignore
        registration_id,
    )

    assert result is run
    thread_id, run_id, tool_outputs = called["args"]
    assert thread_id == "t2"
    assert run_id == "r2"
    assert len(tool_outputs) == 1

    to = tool_outputs[0]
    assert isinstance(to, dict)
    assert to["tool_call_id"] == "2"
    assert json.loads(to["output"]) == {
        "message": "Password reset successfully",
        "user_data": {"email": "x@dominio", "password": "nova_senha"},
        "information": "User will be prompted to change the password at the first login.",
    }


@pytest.mark.asyncio
async def test_handle_get_member_addresses(monkeypatch):
    """Test if the ToolCallService.handle_tool_calls processes a GET_MEMBER_ADDRESSES call correctly."""

    tool_call = SimpleNamespace(
        id="3", function=SimpleNamespace(name=FunctionCall.GET_MEMBER_ADDRESSES, arguments="{}")
    )

    run = SimpleNamespace(
        id="r3",
        thread_id="t3",
        required_action=SimpleNamespace(
            submit_tool_outputs=SimpleNamespace(tool_calls=[tool_call])
        ),
    )

    registration_id = 5

    async def fake_get_member_addresses_request(registration_id: int):
        return [
            {
                "registration_id": 5,
                "state": "RJ",
                "city": "Rio de Janeiro",
                "address": "Rua das Laranjeiras, 123",
                "neighborhood": "Laranjeiras",
                "zip": "22240003",
                "country": "Brasil",
                "latlong": "-22.9361,-43.1782",
            }
        ]

    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.tool_calls_handler.get_member_addresses_request",
        fake_get_member_addresses_request,
    )

    called = {}

    async def fake_submit(thread_id: str, run_id: str, tool_outputs: list):
        called["args"] = (thread_id, run_id, tool_outputs)
        return run

    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.tool_calls_handler.openai_client.beta.threads.runs.submit_tool_outputs",
        fake_submit,
    )

    result = await ToolCallService.handle_tool_calls(
        run,  # type: ignore
        registration_id,
    )

    assert result is run
    thread_id, run_id, tool_outputs = called["args"]
    assert thread_id == "t3"
    assert run_id == "r3"
    assert len(tool_outputs) == 1

    to = tool_outputs[0]
    assert isinstance(to, dict)
    assert to["tool_call_id"] == "3"
    assert json.loads(to["output"]) == [
        {
            "registration_id": 5,
            "state": "RJ",
            "city": "Rio de Janeiro",
            "address": "Rua das Laranjeiras, 123",
            "neighborhood": "Laranjeiras",
            "zip": "22240003",
            "country": "Brasil",
            "latlong": "-22.9361,-43.1782",
        }
    ]


@pytest.mark.asyncio
async def test_handle_update_address(monkeypatch):
    """Test if the ToolCallService.handle_tool_calls processes a UPDATE_ADDRESS call correctly."""

    updated_address = {
        "state": "RJ",
        "city": "Rio de Janeiro",
        "address": "Rua das Laranjeiras, 456",
        "neighborhood": "Laranjeiras",
        "zip": "22240003",
        "country": "Brasil",
        "latlong": "-22.9361,-43.1782",
    }
    tool_call = SimpleNamespace(
        id="4",
        function=SimpleNamespace(
            name=FunctionCall.UPDATE_ADDRESS,
            arguments=json.dumps({"address_id": 1, "updated_address": updated_address}),
        ),
    )

    run = SimpleNamespace(
        id="r4",
        thread_id="t4",
        required_action=SimpleNamespace(
            submit_tool_outputs=SimpleNamespace(tool_calls=[tool_call])
        ),
    )

    registration_id = 5

    async def fake_update_address_request(registration_id: int, address: dict, address_id: int):
        return {
            "message": "Address updated successfully",
            "address_id": address_id,
            "updated_address": address,
        }

    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.tool_calls_handler.update_address_request",
        fake_update_address_request,
    )

    called = {}

    async def fake_submit(thread_id: str, run_id: str, tool_outputs: list):
        called["args"] = (thread_id, run_id, tool_outputs)
        return run

    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.tool_calls_handler.openai_client.beta.threads.runs.submit_tool_outputs",
        fake_submit,
    )

    result = await ToolCallService.handle_tool_calls(
        run,  # type: ignore
        registration_id,
    )

    assert result is run
    thread_id, run_id, tool_outputs = called["args"]
    assert thread_id == "t4"
    assert run_id == "r4"
    assert len(tool_outputs) == 1

    to = tool_outputs[0]
    assert isinstance(to, dict)
    assert to["tool_call_id"] == "4"
    assert json.loads(to["output"]) == {
        "message": "Address updated successfully",
        "address_id": 1,
        "updated_address": updated_address,
    }


@pytest.mark.asyncio
async def test_handle_get_member_legal_reps(monkeypatch):
    """Test if the ToolCallService.handle_tool_calls processes a GET_MEMBER_LEGAL_REPS call correctly."""

    tool_call = SimpleNamespace(
        id="5", function=SimpleNamespace(name=FunctionCall.GET_MEMBER_LEGAL_REPS, arguments="{}")
    )

    run = SimpleNamespace(
        id="r5",
        thread_id="t5",
        required_action=SimpleNamespace(
            submit_tool_outputs=SimpleNamespace(tool_calls=[tool_call])
        ),
    )

    registration_id = 7  # Ana Silva Junior (menor de idade)

    async def fake_get_member_legal_reps(registration_id: int):
        return [
            {
                "id": 1,
                "registration_id": registration_id,
                "name": "Maria Silva",
                "cpf": "11122233344",
                "relationship": "Mãe",
                "phone": "+5521999999999",
                "email": "maria.silva@example.com",
            }
        ]

    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.tool_calls_handler.get_member_legal_reps",
        fake_get_member_legal_reps,
    )

    called = {}

    async def fake_submit(thread_id: str, run_id: str, tool_outputs: list):
        called["args"] = (thread_id, run_id, tool_outputs)
        return run

    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.tool_calls_handler.openai_client.beta.threads.runs.submit_tool_outputs",
        fake_submit,
    )

    result = await ToolCallService.handle_tool_calls(run, registration_id)  # type: ignore
    assert result is run
    thread_id, run_id, tool_outputs = called["args"]
    assert thread_id == "t5"
    assert run_id == "r5"
    assert len(tool_outputs) == 1

    to = tool_outputs[0]
    assert isinstance(to, dict)
    assert to["tool_call_id"] == "5"
    assert json.loads(to["output"]) == [
        {
            "id": 1,
            "registration_id": registration_id,
            "name": "Maria Silva",
            "cpf": "11122233344",
            "relationship": "Mãe",
            "phone": "+5521999999999",
            "email": "maria.silva@example.com",
        }
    ]


@pytest.mark.asyncio
async def test_handle_add_member_legal_reps(monkeypatch):
    """Test if the ToolCallService.handle_tool_calls processes a ADD_MEMBER_LEGAL_REPS call correctly."""

    legal_representative = {
        "name": "João Silva",
        "cpf": "22233344455",
        "relationship": "Pai",
        "phone": "+5521988888888",
        "email": "joao.silva@example.com",
    }
    tool_call = SimpleNamespace(
        id="6",
        function=SimpleNamespace(
            name=FunctionCall.ADD_MEMBER_LEGAL_REPS,
            arguments=json.dumps({"legal_representative": legal_representative}),
        ),
    )

    run = SimpleNamespace(
        id="r6",
        thread_id="t6",
        required_action=SimpleNamespace(
            submit_tool_outputs=SimpleNamespace(tool_calls=[tool_call])
        ),
    )

    registration_id = 7

    async def fake_add_member_legal_reps(registration_id: int, legal_representative: dict):
        return {
            "message": "Legal representative added successfully",
            "registration_id": registration_id,
            "legal_representative": legal_representative,
        }

    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.tool_calls_handler.add_member_legal_reps",
        fake_add_member_legal_reps,
    )

    called = {}

    async def fake_submit(thread_id: str, run_id: str, tool_outputs: list):
        called["args"] = (thread_id, run_id, tool_outputs)
        return run

    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.tool_calls_handler.openai_client.beta.threads.runs.submit_tool_outputs",
        fake_submit,
    )

    result = await ToolCallService.handle_tool_calls(run, registration_id)  # type: ignore
    assert result is run
    thread_id, run_id, tool_outputs = called["args"]
    assert thread_id == "t6"
    assert run_id == "r6"
    assert len(tool_outputs) == 1

    to = tool_outputs[0]
    assert isinstance(to, dict)
    assert to["tool_call_id"] == "6"
    assert json.loads(to["output"]) == {
        "message": "Legal representative added successfully",
        "registration_id": registration_id,
        "legal_representative": legal_representative,
    }


@pytest.mark.asyncio
async def test_handle_update_member_legal_reps(monkeypatch):
    """Test if the ToolCallService.handle_tool_calls processes a UPDATE_MEMBER_LEGAL_REPS call correctly."""

    updated_legal_representative = {
        "name": "João Silva",
        "cpf": "22233344455",
        "relationship": "Pai",
        "phone": "+5521988888888",
        "email": "joao.silva@novoemail.com",
    }
    tool_call = SimpleNamespace(
        id="7",
        function=SimpleNamespace(
            name=FunctionCall.UPDATE_MEMBER_LEGAL_REPS,
            arguments=json.dumps(
                {
                    "legal_representative_id": 2,
                    "legal_representative": updated_legal_representative,
                }
            ),
        ),
    )

    run = SimpleNamespace(
        id="r7",
        thread_id="t7",
        required_action=SimpleNamespace(
            submit_tool_outputs=SimpleNamespace(tool_calls=[tool_call])
        ),
    )

    registration_id = 7

    async def fake_update_member_legal_reps(
        registration_id: int, legal_representative_id: int, legal_representative: dict
    ):
        return {
            "message": "Legal representative updated successfully",
            "registration_id": registration_id,
            "legal_representative_id": legal_representative_id,
            "updated_legal_representative": legal_representative,
        }

    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.tool_calls_handler.update_member_legal_reps",
        fake_update_member_legal_reps,
    )

    called = {}

    async def fake_submit(thread_id: str, run_id: str, tool_outputs: list):
        called["args"] = (thread_id, run_id, tool_outputs)
        return run

    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.tool_calls_handler.openai_client.beta.threads.runs.submit_tool_outputs",
        fake_submit,
    )

    result = await ToolCallService.handle_tool_calls(run, registration_id)  # type: ignore
    assert result is run
    thread_id, run_id, tool_outputs = called["args"]
    assert thread_id == "t7"
    assert run_id == "r7"
    assert len(tool_outputs) == 1

    to = tool_outputs[0]
    assert isinstance(to, dict)
    assert to["tool_call_id"] == "7"
    assert json.loads(to["output"]) == {
        "message": "Legal representative updated successfully",
        "registration_id": registration_id,
        "legal_representative_id": 2,
        "updated_legal_representative": updated_legal_representative,
    }


@pytest.mark.asyncio
async def test_handle_delete_member_legal_reps(monkeypatch):
    """Test if the ToolCallService.handle_tool_calls processes a DELETE_MEMBER_LEGAL_REPS call correctly."""

    tool_call = SimpleNamespace(
        id="8",
        function=SimpleNamespace(
            name=FunctionCall.DELETE_MEMBER_LEGAL_REPS,
            arguments=json.dumps({"legal_representative_id": 3}),
        ),
    )

    run = SimpleNamespace(
        id="r8",
        thread_id="t8",
        required_action=SimpleNamespace(
            submit_tool_outputs=SimpleNamespace(tool_calls=[tool_call])
        ),
    )

    registration_id = 7

    async def fake_delete_member_legal_reps(registration_id: int, legal_representative_id: int):
        return {
            "message": "Legal representative deleted successfully",
            "registration_id": registration_id,
            "legal_representative_id": legal_representative_id,
        }

    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.tool_calls_handler.delete_member_legal_reps",
        fake_delete_member_legal_reps,
    )

    called = {}

    async def fake_submit(thread_id: str, run_id: str, tool_outputs: list):
        called["args"] = (thread_id, run_id, tool_outputs)
        return run

    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.tool_calls_handler.openai_client.beta.threads.runs.submit_tool_outputs",
        fake_submit,
    )

    result = await ToolCallService.handle_tool_calls(run, registration_id)  # type: ignore
    assert result is run
    thread_id, run_id, tool_outputs = called["args"]
    assert thread_id == "t8"
    assert run_id == "r8"
    assert len(tool_outputs) == 1

    to = tool_outputs[0]
    assert isinstance(to, dict)
    assert to["tool_call_id"] == "8"
    assert json.loads(to["output"]) == {
        "message": "Legal representative deleted successfully",
        "registration_id": registration_id,
        "legal_representative_id": 3,
    }


@pytest.mark.asyncio
async def test_handle_get_all_whatsapp_groups(monkeypatch):
    """Test if the ToolCallService.handle_tool_calls processes a GET_ALL_WHATSAPP_GROUPS call correctly."""
    tool_call = SimpleNamespace(
        id="9",
        function=SimpleNamespace(
            name=FunctionCall.GET_ALL_WHATSAPP_GROUPS,
            arguments="{}",
        ),
    )
    run = SimpleNamespace(
        id="r9",
        thread_id="t9",
        required_action=SimpleNamespace(
            submit_tool_outputs=SimpleNamespace(tool_calls=[tool_call])
        ),
    )
    registration_id = 5

    async def fake_get_all_whatsapp_groups(registration_id: int):
        return [
            {
                "group_id": "120363045725875023@g.us",
                "group_name": "Grupos Regionais Mensa Brasil",
                "region": "RJ",
                "member": True,
            },
            {
                "group_id": "120363025301625134@g.us",
                "group_name": "MB | Mulheres",
                "region": None,
                "member": False,
            },
        ]

    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.tool_calls_handler.get_all_whatsapp_groups",
        fake_get_all_whatsapp_groups,
    )

    called = {}

    async def fake_submit(thread_id: str, run_id: str, tool_outputs: list):
        called["args"] = (thread_id, run_id, tool_outputs)
        return run

    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.tool_calls_handler.openai_client.beta.threads.runs.submit_tool_outputs",
        fake_submit,
    )

    result = await ToolCallService.handle_tool_calls(run, registration_id)  # type: ignore
    assert result is run
    thread_id, run_id, tool_outputs = called["args"]
    assert thread_id == "t9"
    assert run_id == "r9"
    assert len(tool_outputs) == 1
    to = tool_outputs[0]
    assert isinstance(to, dict)
    assert to["tool_call_id"] == "9"
    assert json.loads(to["output"]) == [
        {
            "group_id": "120363045725875023@g.us",
            "group_name": "Grupos Regionais Mensa Brasil",
            "region": "RJ",
            "member": True,
        },
        {
            "group_id": "120363025301625134@g.us",
            "group_name": "MB | Mulheres",
            "region": None,
            "member": False,
        },
    ]


@pytest.mark.asyncio
async def test_handle_request_whatsapp_group_join(monkeypatch):
    """Test if the ToolCallService.handle_tool_calls processes a REQUEST_WHATSAPP_GROUP_JOIN call correctly."""
    tool_call = SimpleNamespace(
        id="10",
        function=SimpleNamespace(
            name=FunctionCall.REQUEST_WHATSAPP_GROUP_JOIN,
            arguments=json.dumps({"group_id": "120363025301625134@g.us"}),
        ),
    )
    run = SimpleNamespace(
        id="r10",
        thread_id="t10",
        required_action=SimpleNamespace(
            submit_tool_outputs=SimpleNamespace(tool_calls=[tool_call])
        ),
    )
    registration_id = 11

    async def fake_request_whatsapp_group_join(registration_id: int, group_id: str):
        return {
            "message": "Request to join group sent successfully",
            "registration_id": registration_id,
            "group_id": group_id,
        }

    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.tool_calls_handler.request_whatsapp_group_join",
        fake_request_whatsapp_group_join,
    )

    called = {}

    async def fake_submit(thread_id: str, run_id: str, tool_outputs: list):
        called["args"] = (thread_id, run_id, tool_outputs)
        return run

    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.tool_calls_handler.openai_client.beta.threads.runs.submit_tool_outputs",
        fake_submit,
    )

    result = await ToolCallService.handle_tool_calls(run, registration_id)  # type: ignore
    assert result is run
    thread_id, run_id, tool_outputs = called["args"]
    assert thread_id == "t10"
    assert run_id == "r10"
    assert len(tool_outputs) == 1
    to = tool_outputs[0]
    assert isinstance(to, dict)
    assert to["tool_call_id"] == "10"
    assert json.loads(to["output"]) == {
        "message": "Request to join group sent successfully",
        "registration_id": registration_id,
        "group_id": "120363025301625134@g.us",
    }


@pytest.mark.asyncio
async def test_handle_get_pending_whatsapp_group_join_requests(monkeypatch):
    """Test if the ToolCallService.handle_tool_calls processes a GET_PENDING_WHATSAPP_GROUP_JOIN_REQUESTS call correctly."""
    tool_call = SimpleNamespace(
        id="11",
        function=SimpleNamespace(
            name=FunctionCall.GET_PENDING_WHATSAPP_GROUP_JOIN_REQUESTS,
            arguments="{}",
        ),
    )
    run = SimpleNamespace(
        id="r11",
        thread_id="t11",
        required_action=SimpleNamespace(
            submit_tool_outputs=SimpleNamespace(tool_calls=[tool_call])
        ),
    )
    registration_id = 5

    async def fake_get_pending_whatsapp_group_join_requests(registration_id: int):
        return [
            {
                "group_id": "120363150360123420@g.us",
                "group_name": "Grupos Regionais Mensa Brasil",
                "no_of_attempts": 3,
                "last_attempt": "2023-10-01",
                "fulfilled": False,
            }
        ]

    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.tool_calls_handler.get_pending_whatsapp_group_join_requests",
        fake_get_pending_whatsapp_group_join_requests,
    )

    called = {}

    async def fake_submit(thread_id: str, run_id: str, tool_outputs: list):
        called["args"] = (thread_id, run_id, tool_outputs)
        return run

    monkeypatch.setattr(
        "people_api.services.whatsapp_service.chatbot.tool_calls_handler.openai_client.beta.threads.runs.submit_tool_outputs",
        fake_submit,
    )

    result = await ToolCallService.handle_tool_calls(run, registration_id)  # type: ignore
    assert result is run
    thread_id, run_id, tool_outputs = called["args"]
    assert thread_id == "t11"
    assert run_id == "r11"
    assert len(tool_outputs) == 1
    to = tool_outputs[0]
    assert isinstance(to, dict)
    assert to["tool_call_id"] == "11"
    assert json.loads(to["output"]) == [
        {
            "group_id": "120363150360123420@g.us",
            "group_name": "Grupos Regionais Mensa Brasil",
            "no_of_attempts": 3,
            "last_attempt": "2023-10-01",
            "fulfilled": False,
        }
    ]

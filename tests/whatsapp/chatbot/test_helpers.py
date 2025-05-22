"""Unit tests for the WhatsApp client helpers."""

from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

import people_api.services.whatsapp_service.chatbot.wpp_client_helpers as helpers


@pytest.mark.asyncio
async def test_get_member_info_by_phone_number_found(monkeypatch):
    """Test the get_member_info_by_phone_number function when a member is found."""
    registration = MagicMock()
    registration.name = "JOAO DA SILVA"
    registration.registration_id = 123
    registration.birth_date = date(2000, 1, 1)

    session = MagicMock()
    session.exec = AsyncMock()
    registration_result_mock = MagicMock()
    registration_result_mock.first.return_value = registration

    email_obj = MagicMock()
    email_obj.email_address = "joao@mensa.org.br"
    email_result_mock = MagicMock()
    email_result_mock.all.return_value = [email_obj]

    session.exec.side_effect = [registration_result_mock, email_result_mock]

    payment = MagicMock()
    payment.expiration_date = date(2025, 1, 1)
    monkeypatch.setattr(
        helpers.MembershipPaymentService, "get_last_payment", AsyncMock(return_value=payment)
    )

    result = await helpers.get_member_info_by_phone_number("99999999", session)
    assert result.name == "Joao Da Silva"
    assert result.registration_id == 123
    assert result.birth_date == date(2000, 1, 1)
    assert result.expiration_date == date(2025, 1, 1)
    assert result.email_mensa == "joao@mensa.org.br"


@pytest.mark.asyncio
async def test_get_member_info_by_phone_number_not_found(monkeypatch):
    session = MagicMock()
    session.exec = AsyncMock()
    result_mock = MagicMock()
    result_mock.first.return_value = None
    session.exec.return_value = result_mock

    with pytest.raises(ValueError):
        await helpers.get_member_info_by_phone_number("99999999", session)


@pytest.mark.asyncio
async def test_create_email_request(monkeypatch):
    """Test the create_email_request function."""
    monkeypatch.setattr(helpers, "create_token", lambda registration_id: "token")
    mock_response = MagicMock()
    mock_response.json.return_value = {"message": "ok"}
    mock_response.status_code = 200

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    monkeypatch.setattr(
        helpers, "httpx", MagicMock(AsyncClient=MagicMock(return_value=mock_client))
    )
    monkeypatch.setattr(helpers, "get_settings", lambda: MagicMock(api_port=8000))

    result = await helpers.create_email_request(1)
    assert result == {"message": "ok"}


@pytest.mark.asyncio
async def test_recover_email_password_request(monkeypatch):
    """Test the recover_email_password_request function."""
    monkeypatch.setattr(helpers, "create_token", lambda registration_id: "token")
    mock_response = MagicMock()
    mock_response.json.return_value = {"message": "reset"}
    mock_response.status_code = 200

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    monkeypatch.setattr(
        helpers, "httpx", MagicMock(AsyncClient=MagicMock(return_value=mock_client))
    )
    monkeypatch.setattr(helpers, "get_settings", lambda: MagicMock(api_port=8000))

    result = await helpers.recover_email_password_request(2)
    assert result == {"message": "reset"}


@pytest.mark.asyncio
async def test_get_member_addresses_request_empty(monkeypatch):
    """Test the get_member_addresses_request function when no addresses are registered."""
    monkeypatch.setattr(helpers, "create_token", lambda registration_id: "token")
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.status_code = 200

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    monkeypatch.setattr(
        helpers, "httpx", MagicMock(AsyncClient=MagicMock(return_value=mock_client))
    )
    monkeypatch.setattr(helpers, "get_settings", lambda: MagicMock(api_port=8000))

    result = await helpers.get_member_addresses_request(3)
    assert result == {"message": "No addresses registered for this member."}


@pytest.mark.asyncio
async def test_update_address_request(monkeypatch):
    """Test the update_address_request function."""
    monkeypatch.setattr(helpers, "create_token", lambda registration_id: "token")
    mock_response = MagicMock()
    mock_response.json.return_value = {"message": "updated"}
    mock_response.status_code = 200

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    mock_client.put = AsyncMock(return_value=mock_response)

    monkeypatch.setattr(
        helpers, "httpx", MagicMock(AsyncClient=MagicMock(return_value=mock_client))
    )
    monkeypatch.setattr(helpers, "get_settings", lambda: MagicMock(api_port=8000))

    result = await helpers.update_address_request(4, 10, {"address": "new address"})
    assert result == {"message": "updated"}


@pytest.mark.asyncio
async def test_get_member_legal_reps_empty(monkeypatch):
    """Test get_member_legal_reps when no legal representatives are registered."""
    monkeypatch.setattr(helpers, "create_token", lambda registration_id: "token")
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.status_code = 200

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    monkeypatch.setattr(
        helpers, "httpx", MagicMock(AsyncClient=MagicMock(return_value=mock_client))
    )
    monkeypatch.setattr(helpers, "get_settings", lambda: MagicMock(api_port=8000))

    result = await helpers.get_member_legal_reps(5)
    assert result == {"message": "No legal representatives registered for this member."}


@pytest.mark.asyncio
async def test_get_member_legal_reps_found(monkeypatch):
    """Test get_member_legal_reps when legal representatives are found."""
    monkeypatch.setattr(helpers, "create_token", lambda registration_id: "token")
    mock_response = MagicMock()
    mock_response.json.return_value = [{"id": 1, "name": "Rep"}]
    mock_response.status_code = 200

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    monkeypatch.setattr(
        helpers, "httpx", MagicMock(AsyncClient=MagicMock(return_value=mock_client))
    )
    monkeypatch.setattr(helpers, "get_settings", lambda: MagicMock(api_port=8000))

    result = await helpers.get_member_legal_reps(6)
    assert result == [{"id": 1, "name": "Rep"}]


@pytest.mark.asyncio
async def test_add_member_legal_reps(monkeypatch):
    """Test add_member_legal_reps function."""
    monkeypatch.setattr(helpers, "create_token", lambda registration_id: "token")
    mock_response = MagicMock()
    mock_response.json.return_value = {"message": "added"}
    mock_response.status_code = 201

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    monkeypatch.setattr(
        helpers, "httpx", MagicMock(AsyncClient=MagicMock(return_value=mock_client))
    )
    monkeypatch.setattr(helpers, "get_settings", lambda: MagicMock(api_port=8000))

    result = await helpers.add_member_legal_reps(7, {"name": "Rep"})
    assert result == {"message": "added"}


@pytest.mark.asyncio
async def test_update_member_legal_reps(monkeypatch):
    """Test update_member_legal_reps function."""
    monkeypatch.setattr(helpers, "create_token", lambda registration_id: "token")
    mock_response = MagicMock()
    mock_response.json.return_value = {"message": "updated"}
    mock_response.status_code = 200

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    mock_client.put = AsyncMock(return_value=mock_response)

    monkeypatch.setattr(
        helpers, "httpx", MagicMock(AsyncClient=MagicMock(return_value=mock_client))
    )
    monkeypatch.setattr(helpers, "get_settings", lambda: MagicMock(api_port=8000))

    result = await helpers.update_member_legal_reps(8, 2, {"name": "Rep"})
    assert result == {"message": "updated"}


@pytest.mark.asyncio
async def test_delete_member_legal_reps(monkeypatch):
    """Test delete_member_legal_reps function."""
    monkeypatch.setattr(helpers, "create_token", lambda registration_id: "token")
    mock_response = MagicMock()
    mock_response.json.return_value = {"message": "deleted"}
    mock_response.status_code = 200

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    mock_client.delete = AsyncMock(return_value=mock_response)

    monkeypatch.setattr(
        helpers, "httpx", MagicMock(AsyncClient=MagicMock(return_value=mock_client))
    )
    monkeypatch.setattr(helpers, "get_settings", lambda: MagicMock(api_port=8000))

    result = await helpers.delete_member_legal_reps(9, 3)
    assert result == {"message": "deleted"}


@pytest.mark.asyncio
async def test_get_all_whatsapp_groups_empty(monkeypatch):
    """Test get_all_whatsapp_groups when no groups are found."""
    monkeypatch.setattr(helpers, "create_token", lambda registration_id: "token")
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.status_code = 200

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    monkeypatch.setattr(
        helpers, "httpx", MagicMock(AsyncClient=MagicMock(return_value=mock_client))
    )
    monkeypatch.setattr(helpers, "get_settings", lambda: MagicMock(api_port=8000))

    result = await helpers.get_all_whatsapp_groups(10)
    assert result == {"message": "No WhatsApp groups found."}


@pytest.mark.asyncio
async def test_get_all_whatsapp_groups_found(monkeypatch):
    """Test get_all_whatsapp_groups when groups are found."""
    monkeypatch.setattr(helpers, "create_token", lambda registration_id: "token")
    mock_response = MagicMock()
    mock_response.json.return_value = [{"id": "g1", "name": "Group 1"}]
    mock_response.status_code = 200

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    monkeypatch.setattr(
        helpers, "httpx", MagicMock(AsyncClient=MagicMock(return_value=mock_client))
    )
    monkeypatch.setattr(helpers, "get_settings", lambda: MagicMock(api_port=8000))

    result = await helpers.get_all_whatsapp_groups(11)
    assert result == [{"id": "g1", "name": "Group 1"}]


@pytest.mark.asyncio
async def test_request_whatsapp_group_join(monkeypatch):
    """Test request_whatsapp_group_join function."""
    monkeypatch.setattr(helpers, "create_token", lambda registration_id: "token")
    mock_response = MagicMock()
    mock_response.json.return_value = {"message": "requested"}
    mock_response.status_code = 200

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    monkeypatch.setattr(
        helpers, "httpx", MagicMock(AsyncClient=MagicMock(return_value=mock_client))
    )
    monkeypatch.setattr(helpers, "get_settings", lambda: MagicMock(api_port=8000))

    result = await helpers.request_whatsapp_group_join(12, "g2")
    assert result == {"message": "requested"}


@pytest.mark.asyncio
async def test_get_pending_whatsapp_group_join_requests_empty(monkeypatch):
    """Test get_pending_whatsapp_group_join_requests when no requests are found."""
    monkeypatch.setattr(helpers, "create_token", lambda registration_id: "token")
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.status_code = 200

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    monkeypatch.setattr(
        helpers, "httpx", MagicMock(AsyncClient=MagicMock(return_value=mock_client))
    )
    monkeypatch.setattr(helpers, "get_settings", lambda: MagicMock(api_port=8000))

    result = await helpers.get_pending_whatsapp_group_join_requests(13)
    assert result == {"message": "No pending WhatsApp group join requests found."}


@pytest.mark.asyncio
async def test_get_pending_whatsapp_group_join_requests_found(monkeypatch):
    """Test get_pending_whatsapp_group_join_requests when requests are found."""
    monkeypatch.setattr(helpers, "create_token", lambda registration_id: "token")
    mock_response = MagicMock()
    mock_response.json.return_value = [{"group_id": "g3", "status": "pending"}]
    mock_response.status_code = 200

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    monkeypatch.setattr(
        helpers, "httpx", MagicMock(AsyncClient=MagicMock(return_value=mock_client))
    )
    monkeypatch.setattr(helpers, "get_settings", lambda: MagicMock(api_port=8000))

    result = await helpers.get_pending_whatsapp_group_join_requests(14)
    assert result == [{"group_id": "g3", "status": "pending"}]


@pytest.mark.asyncio
async def test_get_failed_whatsapp_group_join_requests_empty(monkeypatch):
    """Test get_failed_whatsapp_group_join_requests when no requests are found."""
    monkeypatch.setattr(helpers, "create_token", lambda registration_id: "token")
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.status_code = 200

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    monkeypatch.setattr(
        helpers, "httpx", MagicMock(AsyncClient=MagicMock(return_value=mock_client))
    )
    monkeypatch.setattr(helpers, "get_settings", lambda: MagicMock(api_port=8000))

    result = await helpers.get_failed_whatsapp_group_join_requests(15)
    assert result == {"message": "No failed WhatsApp group join requests found."}


@pytest.mark.asyncio
async def test_get_failed_whatsapp_group_join_requests_found(monkeypatch):
    """Test get_failed_whatsapp_group_join_requests when requests are found."""
    monkeypatch.setattr(helpers, "create_token", lambda registration_id: "token")
    mock_response = MagicMock()
    mock_response.json.return_value = [{"group_id": "g4", "status": "failed"}]
    mock_response.status_code = 200

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    monkeypatch.setattr(
        helpers, "httpx", MagicMock(AsyncClient=MagicMock(return_value=mock_client))
    )
    monkeypatch.setattr(helpers, "get_settings", lambda: MagicMock(api_port=8000))

    result = await helpers.get_failed_whatsapp_group_join_requests(16)
    assert result == [{"group_id": "g4", "status": "failed"}]


@pytest.mark.asyncio
async def test_send_feedback_to_api(monkeypatch):
    """Test send_feedback_to_api function."""
    monkeypatch.setattr(helpers, "create_token", lambda registration_id: "token")
    mock_response = MagicMock()
    mock_response.json.return_value = {"message": "feedback received"}
    mock_response.status_code = 200

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    monkeypatch.setattr(
        helpers, "httpx", MagicMock(AsyncClient=MagicMock(return_value=mock_client))
    )
    monkeypatch.setattr(helpers, "get_settings", lambda: MagicMock(api_port=8000))

    result = await helpers.send_feedback_to_api(17, "Great bot!", "positive", "chatbot")
    assert result == {"message": "feedback received"}

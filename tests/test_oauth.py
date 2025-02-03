import pytest
import respx
from sqlmodel import select

from people_api.database.models.models import Registration
from people_api.dbs import get_redis_client, get_session
from people_api.settings import get_settings

DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
DISCORD_USER_URL = "https://discord.com/api/users/@me"


@pytest.fixture(autouse=True)
def mock_discord_env_vars(monkeypatch):
    # Instead of setting environment variables, override attributes on the settings object.
    settings = get_settings()
    monkeypatch.setattr(settings, "discord_client_id", "fake_client_id")
    monkeypatch.setattr(settings, "discord_client_secret", "fake_client_secret")
    monkeypatch.setattr(
        settings, "discord_redirect_uri", "http://testserver/oauth/discord/callback"
    )


@pytest.mark.asyncio
async def test_discord_callback_success(test_client, mock_valid_token):
    """
    Test the Discord callback endpoint:
    1. Use the /oauth/state endpoint to get a valid state.
    2. Simulate a Discord callback with a fake code.
    3. Verify that the registration is updated with the fake Discord id.
    4. Verify that an HTML response is returned to close the browser tab.
    """
    # Obtain a valid state via the /oauth/state endpoint.
    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    state_response = test_client.get("/oauth/state", headers=headers)
    assert state_response.status_code == 200
    state_json = state_response.json()
    state = state_json["state"]
    assert isinstance(state, str)

    # Confirm that the state is stored in Redis.
    redis_key = f"state:{state}"
    redis_client = await anext(get_redis_client())
    try:
        stored_email = await redis_client.get(redis_key)
    finally:
        await redis_client.close()
    expected_email = "fernando.filho@mensa.org.br"
    assert stored_email == expected_email

    # Mock Discord endpoints.
    with respx.mock(assert_all_called=True) as mock_respx:
        mock_respx.post(DISCORD_TOKEN_URL).respond(
            status_code=200,
            json={
                "access_token": "fake_access_token",
                "token_type": "Bearer",
                "expires_in": 3600,
                "scope": "identify",
            },
        )
        mock_respx.get(DISCORD_USER_URL).respond(status_code=200, json={"id": "fake_discord_id"})

        # Call the discord callback endpoint.
        params = {"code": "fake_code", "state": state}
        callback_response = test_client.get(
            "/oauth/discord/callback", params=params, headers=headers
        )
        assert callback_response.status_code == 200
        # Check that an HTML response is returned.
        content = callback_response.text
        assert "Integração com o Discord realizada com sucesso." in content

    # Verify that the Registration was updated with the fake discord id.
    # Use next() to extract the session from the generator fixture.
    session = next(get_session())
    try:
        statement = select(Registration).where(Registration.discord_id == "fake_discord_id")
        result = session.exec(statement).first()
        assert result is not None
    finally:
        session.close()

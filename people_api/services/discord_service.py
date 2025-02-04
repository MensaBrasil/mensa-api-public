"""Discord service module."""

import httpx
from fastapi import HTTPException
from sqlmodel import Session

from ..settings import get_settings
from .registration_service import RegistrationService

settings = get_settings()


async def process_discord_callback(
    code: str,
    state: str,
    redis_client,
    session: Session,
) -> str:
    """Process the Discord OAuth callback."""
    key = f"state:{state}"
    stored_email = await redis_client.get(key)
    if stored_email is None:
        raise HTTPException(status_code=400, detail="Invalid or expired state")
    await redis_client.delete(key)

    registration = RegistrationService.get_by_email(stored_email, session)
    if not registration or not registration.registration_id:
        raise HTTPException(
            status_code=404, detail="Registration not found or invalid for the provided email"
        )

    token_url = "https://discord.com/api/oauth2/token"
    data = {
        "client_id": settings.discord_client_id,
        "client_secret": settings.discord_client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.discord_redirect_uri,
        "scope": "identify",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, data=data, headers=headers)
    if token_response.status_code != 200:
        raise HTTPException(
            status_code=token_response.status_code,
            detail="Error fetching Discord token",
        )
    token_json = token_response.json()
    access_token = token_json.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Invalid token response from Discord")

    user_url = "https://discord.com/api/users/@me"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        user_response = await client.get(user_url, headers=headers)
    if user_response.status_code != 200:
        raise HTTPException(
            status_code=user_response.status_code,
            detail="Error fetching user info from Discord",
        )
    user_json = user_response.json()
    discord_user_id = user_json.get("id")
    if not discord_user_id:
        raise HTTPException(status_code=400, detail="Discord user id not found")

    RegistrationService.update_discord_id(registration.registration_id, discord_user_id, session)

    html_content = """
    <html>
    <head>
        <title>Integração com Discord Bem-Sucedida</title>
    </head>
    <body>
        <h1>Integração com o Discord realizada com sucesso.</h1>
        <p>Você pode fechar esta janela.</p>
    </body>
    </html>
    """
    return html_content

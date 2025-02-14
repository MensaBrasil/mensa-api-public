"""OAuth endpoints for authentication"""

import secrets

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse

from ..auth import verify_firebase_token
from ..dbs import get_redis_client, get_async_sessions, AsyncSessionsTuple
from ..schemas import OAuthStateResponse
from ..services.discord_service import process_discord_callback
from ..settings import get_settings

settings = get_settings()

oauth_router = APIRouter(prefix="/oauth", tags=["oauth"])


@oauth_router.get(
    "/state",
    response_model=OAuthStateResponse,
)
async def get_state(
    token_data: dict = Depends(verify_firebase_token), redis_client=Depends(get_redis_client)
) -> OAuthStateResponse:
    """Get state for OAuth"""
    state = secrets.token_urlsafe(32)
    key = f"state:{state}"
    await redis_client.set(key, token_data["email"], ex=300)

    return OAuthStateResponse(state=state)


@oauth_router.get(
    "/discord/callback",
    response_class=HTMLResponse,
)
async def discord_callback(
    code: str = Query(...),
    state: str = Query(...),
    redis_client=Depends(get_redis_client),
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
) -> HTMLResponse:
    """Discord OAuth callback endpoint that upserts the discord id and triggers the browser tab close."""
    html_content = await process_discord_callback(code, state, redis_client, session=sessions.rw)
    return HTMLResponse(content=html_content)

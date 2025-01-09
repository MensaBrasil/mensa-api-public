"""Endpoints for managing member WhatsApp groups and group join requests."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import verify_firebase_token
from ..dbs import get_session
from ..models.member import GroupJoinRequest
from ..services import GroupService

group_router = APIRouter()


@group_router.get(
    "/get_can_participate",
    description="Get groups that the member can participate in",
    tags=["member"],
)
async def _get_can_participate(
    token_data=Depends(verify_firebase_token), session: Session = Depends(get_session)
):
    return GroupService.get_can_participate(token_data, session)


@group_router.get(
    "/get_participate_in",
    description="Get groups that the member is participating in",
    tags=["member"],
)
async def _get_participate_in(
    token_data=Depends(verify_firebase_token), session: Session = Depends(get_session)
):
    return GroupService.get_participate_in(token_data, session)


@group_router.get(
    "/get_pending_requests", description="Get pending group join requests", tags=["member"]
)
async def _get_pending_requests(
    token_data=Depends(verify_firebase_token), session: Session = Depends(get_session)
):
    return GroupService.get_pending_requests(token_data, session)


@group_router.get(
    "/get_failed_requests", description="Get failed group join requests", tags=["member"]
)
async def _get_failed_requests(
    token_data=Depends(verify_firebase_token), session: Session = Depends(get_session)
):
    return GroupService.get_failed_requests(token_data, session)


@group_router.post("/request_join_group", tags=["member"], description="Request to join a group")
async def _request_join_group(
    join_request: GroupJoinRequest,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    return GroupService.request_join_group(join_request, token_data, session)

"""Endpoints for managing member WhatsApp groups and group join requests."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import verify_firebase_token
from ..dbs import get_session
from ..models.member import GroupJoinRequest
from ..services import GroupService

group_router = APIRouter()


@group_router.get("/get_member_groups", description="Get member groups", tags=["member"])
async def _get_member_groups(
    token_data=Depends(verify_firebase_token), session: Session = Depends(get_session)
):
    return GroupService.get_member_groups_info(token_data, session)


@group_router.post("/request_join_group", tags=["member"], description="Request to join a group")
async def _request_join_group(
    join_request: GroupJoinRequest,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    return GroupService.request_join_group(join_request, token_data, session)

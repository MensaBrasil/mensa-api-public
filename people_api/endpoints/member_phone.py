"""Endpoints for managing members phone numbers."""

from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..auth import verify_firebase_token
from ..dbs import get_session
from ..models.member_data import (
    PhoneCreate,
    PhoneUpdate,
)
from ..services import PhoneService

member_phone_router = APIRouter()


# add phone to member
@member_phone_router.post("/phone/{mb}", description="Add phone to member", tags=["phone"])
async def _add_phone(
    mb: int,
    phone: PhoneCreate,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    return PhoneService.add_phone(mb, phone, token_data, session)


# update phone from member
@member_phone_router.put(
    "/phone/{mb}/{phone_id}", description="Update phone for member", tags=["phone"]
)
async def update_phone(
    mb: int,
    phone_id: int,
    updated_phone: PhoneUpdate,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    return PhoneService.update_phone(mb, phone_id, updated_phone, token_data, session)


# delete phone from member
@member_phone_router.delete(
    "/phone/{mb}/{phone_id}", description="Delete phone from member", tags=["phone"]
)
async def delete_phone(
    mb: int,
    phone_id: int,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    return PhoneService.delete_phone(mb, phone_id, token_data, session)

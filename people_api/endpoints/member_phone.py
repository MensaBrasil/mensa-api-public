"""
Endpoints for managing members phone numbers.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from people_api.auth import verify_firebase_token
from people_api.dbs import get_session
from people_api.models.member_data import (
    PhoneCreate,
    PhoneUpdate,
)
from people_api.repositories import MemberRepository

member_phone_router = APIRouter()


# add phone to member
@member_phone_router.post("/phone/{mb}", description="Add phone to member", tags=["phone"])
async def _add_phone(
    mb: int,
    phone: PhoneCreate,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    if MB != mb:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # user can just have one phone
    member_data = MemberRepository.getPhonesFromPostgres(mb, session)
    if len(member_data) > 0:
        raise HTTPException(status_code=400, detail="User already has a phone")
    MemberRepository.addPhoneToPostgres(mb, phone, session)
    return {"message": "Phone added successfully"}


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
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    if MB != mb:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Call the update method to modify the phone
    success = MemberRepository.updatePhoneInPostgres(mb, phone_id, updated_phone, session)
    if not success:
        raise HTTPException(status_code=404, detail="Phone not found")

    return {"message": "Phone updated successfully"}


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
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    if MB != mb:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Call the delete method to remove the phone
    success = MemberRepository.deletePhoneFromPostgres(mb, phone_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="Phone not found")

    return {"message": "Phone deleted successfully"}

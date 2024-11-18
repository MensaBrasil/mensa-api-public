"""Endpoints for managing members addresses."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import verify_firebase_token
from ..dbs import get_session
from ..models.member_data import (
    AddressCreate,
    AddressUpdate,
)
from ..services import AddressService

member_address_router = APIRouter()


# add address to member
@member_address_router.post("/address/{mb}", description="Add address to member", tags=["address"])
async def _add_address(
    mb: int,
    address: AddressCreate,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    return AddressService.add_address(mb, address, token_data["email"], session)


# update address from member
@member_address_router.put(
    "/address/{mb}/{address_id}",
    description="Update address for member",
    tags=["address"],
)
async def update_address(
    mb: int,
    address_id: int,
    updated_address: AddressUpdate,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    return AddressService.update_address(
        mb, address_id, updated_address, token_data["email"], session
    )


# delete address from member
@member_address_router.delete(
    "/address/{mb}/{address_id}",
    description="Delete address from member",
    tags=["address"],
)
async def delete_address(
    mb: int,
    address_id: int,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    return AddressService.delete_address(mb, address_id, token_data["email"], session)

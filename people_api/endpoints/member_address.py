"""Endpoints for managing members addresses."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from people_api.database.models.models import Addresses
from people_api.schemas import InternalToken, UserToken

from ..auth import verify_firebase_token
from ..dbs import get_session
from ..services import AddressService

member_address_router = APIRouter()


@member_address_router.get(
    "/address/",
    description="Get addresses for member",
    tags=["address"],
)
async def get_addresses(
    token_data: UserToken | InternalToken = Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    """Get addresses for member."""
    if not token_data.email or not token_data.registration_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return AddressService.get_addresses(token_data, session)


@member_address_router.post("/address/{mb}", description="Add address to member", tags=["address"])
async def _add_address(
    mb: int,
    address: Addresses,
    token_data: UserToken = Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    """Add address to member."""
    if not token_data.email:
        return {"message": "Unauthorized"}
    return AddressService.add_address(mb, address, token_data.email, session)


@member_address_router.put(
    "/address/{mb}/{address_id}",
    description="Update address for member",
    tags=["address"],
)
async def update_address(
    mb: int,
    address_id: int,
    updated_address: Addresses,
    token_data: UserToken | InternalToken = Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    """Update address for member."""
    if not token_data.email:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return AddressService.update_address(mb, address_id, updated_address, token_data.email, session)


@member_address_router.delete(
    "/address/{mb}/{address_id}",
    description="Delete address from member",
    tags=["address"],
)
async def delete_address(
    mb: int,
    address_id: int,
    token_data: UserToken = Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    """Delete address from member."""
    if not token_data.email:
        return {"message": "Unauthorized"}
    return AddressService.delete_address(mb, address_id, token_data.email, session)

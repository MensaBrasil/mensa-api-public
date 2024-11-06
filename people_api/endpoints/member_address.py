"""
Endpoints for managing members addresses.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from people_api.auth import verify_firebase_token
from people_api.dbs import get_session
from people_api.models.member_data import (
    AddressCreate,
    AddressUpdate,
)
from people_api.repositories import MemberRepository

member_address_router = APIRouter()


# add address to member
@member_address_router.post("/address/{mb}", description="Add address to member", tags=["address"])
async def _add_address(
    mb: int,
    address: AddressCreate,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    if MB != mb:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # user can just have one address
    member_data = MemberRepository.getAddressesFromPostgres(mb, session)
    if len(member_data) > 0:
        raise HTTPException(status_code=400, detail="User already has an address")

    MemberRepository.addAddressToPostgres(mb, address, session)
    return {"message": "Address added successfully"}


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
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    if MB != mb:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Call the update method to modify the address
    success = MemberRepository.updateAddressInPostgres(mb, address_id, updated_address, session)
    if not success:
        raise HTTPException(status_code=404, detail="Address not found")

    return {"message": "Address updated successfully"}


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
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    if MB != mb:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Call the delete method to remove the address
    success = MemberRepository.deleteAddressFromPostgres(mb, address_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="Address not found")

    return {"message": "Address deleted successfully"}

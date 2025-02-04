# mypy: ignore-errors

"""Service for managing members addresses."""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models.member_data import AddressCreate, AddressUpdate
from ..repositories import MemberRepository


class AddressService:
    @staticmethod
    def add_address(mb: int, address: AddressCreate, token_email: str, session: Session):
        MB = MemberRepository.getMBByEmail(token_email, session)
        if MB != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")
        # user can just have one address
        member_data = MemberRepository.getAddressesFromPostgres(mb, session)
        if len(member_data) > 0:
            raise HTTPException(status_code=400, detail="User already has an address")

        MemberRepository.addAddressToPostgres(mb, address, session)
        return {"message": "Address added successfully"}

    @staticmethod
    def update_address(
        mb: int,
        address_id: int,
        updated_address: AddressUpdate,
        token_email: str,
        session: Session,
    ):
        MB = MemberRepository.getMBByEmail(token_email, session)
        if MB != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")
        # Call the update method to modify the address
        success = MemberRepository.updateAddressInPostgres(mb, address_id, updated_address, session)
        if not success:
            raise HTTPException(status_code=404, detail="Address not found")
        return {"message": "Address updated successfully"}

    @staticmethod
    def delete_address(mb: int, address_id: int, token_email: str, session: Session):
        MB = MemberRepository.getMBByEmail(token_email, session)
        if MB != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")
        # Call the delete method to remove the address
        success = MemberRepository.deleteAddressFromPostgres(mb, address_id, session)
        if not success:
            raise HTTPException(status_code=404, detail="Address not found")
        return {"message": "Address deleted successfully"}

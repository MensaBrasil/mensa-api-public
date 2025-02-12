# mypy: ignore-errors

"""Service for managing members addresses."""

from fastapi import HTTPException
from sqlmodel import Session

from people_api.database.models.models import Addresses, Registration


class AddressService:
    @staticmethod
    def add_address(mb: int, address: Addresses, token_email: str, session: Session):
        reg_stmt = Registration.select_stmt_by_email(token_email)
        reg = session.exec(reg_stmt).first()
        if not reg or reg.registration_id != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")
        addr_stmt = Addresses.get_address_for_member(mb)
        existing_addresses = session.exec(addr_stmt).all()
        if existing_addresses:
            raise HTTPException(status_code=400, detail="User already has an address")
        insert_stmt = Addresses.insert_stmt_for_address(mb, address)
        session.exec(insert_stmt)
        return {"message": "Address added successfully"}

    @staticmethod
    def update_address(
        mb: int, address_id: int, updated_address: Addresses, token_email: str, session: Session
    ):
        reg_stmt = Registration.select_stmt_by_email(token_email)
        reg = session.exec(reg_stmt).first()
        if not reg or reg.registration_id != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")
        update_stmt = Addresses.update_stmt_for_address(mb, address_id, updated_address)
        result = session.exec(update_stmt)
        if result.rowcount is None or result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Address not found")
        return {"message": "Address updated successfully"}

    @staticmethod
    def delete_address(mb: int, address_id: int, token_email: str, session: Session):
        reg_stmt = Registration.select_stmt_by_email(token_email)
        reg = session.exec(reg_stmt).first()

        if not reg or reg.registration_id != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")

        delete_stmt = Addresses.delete_stmt_for_address(mb, address_id)
        result = session.exec(delete_stmt)

        if result.rowcount == 0:  
            raise HTTPException(status_code=404, detail="Address not found")

        return {"message": "Address deleted successfully"}

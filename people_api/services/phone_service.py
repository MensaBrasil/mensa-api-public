"""Service for managing members phone numbers."""

from fastapi import HTTPException
from sqlmodel import Session

from people_api.database.models.models import PhoneInput, Phones, Registration
from people_api.schemas import UserToken


class PhoneService:
    @staticmethod
    def add_phone(mb: int, phone_input: PhoneInput, token_data: UserToken, session: Session):
        """Add phone to member."""
        phone = phone_input.phone
        if not token_data.email:
            raise HTTPException(status_code=401, detail="Unauthorized")
        reg_stmt = Registration.select_stmt_by_email(token_data.email)
        reg = session.exec(reg_stmt).first()
        if not reg or reg.registration_id != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")
        phones_stmt = Phones.get_phones_for_member(mb)
        existing_phones = session.exec(phones_stmt).all()
        if len(existing_phones) > 0:
            raise HTTPException(status_code=400, detail="User already has a phone")
        insert_stmt = Phones.insert_stmt_for_phone(mb, phone)
        session.exec(insert_stmt)
        return {"message": "Phone added successfully"}

    @staticmethod
    def update_phone(
        mb: int,
        phone_id: int,
        phone_input: PhoneInput,
        token_data: UserToken,
        session: Session,
    ):
        """Update phone for member."""
        phone = phone_input.phone
        if not token_data.email:
            raise HTTPException(status_code=401, detail="Unauthorized")
        reg_stmt = Registration.select_stmt_by_email(token_data.email)
        reg = session.exec(reg_stmt).first()
        if not reg or reg.registration_id != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")
        update_stmt = Phones.update_stmt_for_phone(mb, phone_id, phone)
        result = session.exec(update_stmt)
        if result.rowcount is None or result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Phone not found")
        return {"message": "Phone updated successfully"}

    @staticmethod
    def delete_phone(mb: int, phone_id: int, token_data: UserToken, session: Session):
        """Delete phone from member."""
        if not token_data.email:
            raise HTTPException(status_code=401, detail="Unauthorized")
        reg_stmt = Registration.select_stmt_by_email(token_data.email)
        reg = session.exec(reg_stmt).first()
        if not reg or reg.registration_id != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")
        delete_stmt = Phones.delete_stmt_for_phone(mb, phone_id)
        result = session.exec(delete_stmt)
        if result.rowcount is None or result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Phone not found")
        return {"message": "Phone deleted successfully"}

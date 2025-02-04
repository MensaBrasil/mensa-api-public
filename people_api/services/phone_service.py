"""Service for managing members phone numbers."""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models.member_data import PhoneCreate, PhoneUpdate
from ..repositories import MemberRepository


class PhoneService:
    @staticmethod
    def add_phone(mb: int, phone: PhoneCreate, token_data: dict, session: Session):
        MB = MemberRepository.getMBByEmail(token_data["email"], session)
        if MB != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")

        # user can just have one phone
        member_data = MemberRepository.getPhonesFromPostgres(mb, session)
        if len(member_data) > 0:
            raise HTTPException(status_code=400, detail="User already has a phone")
        MemberRepository.addPhoneToPostgres(mb, phone, session)  # type: ignore
        return {"message": "Phone added successfully"}

    @staticmethod
    def update_phone(
        mb: int,
        phone_id: int,
        updated_phone: PhoneUpdate,
        token_data: dict,
        session: Session,
    ):
        MB = MemberRepository.getMBByEmail(token_data["email"], session)
        if MB != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")

        # Call the update method to modify the phone
        success = MemberRepository.updatePhoneInPostgres(mb, phone_id, updated_phone, session)  # type: ignore
        if not success:
            raise HTTPException(status_code=404, detail="Phone not found")

        return {"message": "Phone updated successfully"}

    @staticmethod
    def delete_phone(mb: int, phone_id: int, token_data: dict, session: Session):
        MB = MemberRepository.getMBByEmail(token_data["email"], session)
        if MB != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")

        # Call the delete method to remove the phone
        success = MemberRepository.deletePhoneFromPostgres(mb, phone_id, session)
        if not success:
            raise HTTPException(status_code=404, detail="Phone not found")

        return {"message": "Phone deleted successfully"}

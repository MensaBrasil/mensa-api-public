"""Service for legal representative operations."""

from datetime import datetime
from typing import Any

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..models.member_data import LegalRepresentativeCreate, LegalRepresentativeUpdate
from ..repositories import MemberRepository
from ..settings import Settings

SETTINGS=Settings()
# Model for request to add legal representative using API key
class LegalRepresentativeRequest(BaseModel):
    token: str
    mb: str
    birth_date: str
    cpf: str
    legal_representative: LegalRepresentativeCreate


class LegalRepresentativeService:
    @staticmethod
    def add_legal_representative_api_key(request: LegalRepresentativeRequest, session: Session):
        if request.token != SETTINGS.WHATSAPP_ROUTE_API_KEY:
            raise HTTPException(status_code=401, detail="Unauthorized")

        request.mb = int(request.mb)
        member_data = MemberRepository.getFromPostgres(request.mb, session)

        try:
            request.birth_date = datetime.strptime(request.birth_date, "%d/%m/%Y").date()
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid birth date format. Use dd/mm/YYYY."
            )

        # check birth matches
        if member_data.birth_date != request.birth_date:
            raise HTTPException(status_code=400, detail="Birth date does not match")

        if member_data.cpf != request.cpf:
            raise HTTPException(status_code=400, detail="CPF does not match")

        legal_representative = request.legal_representative

        member_data = MemberRepository.getFromPostgres(request.mb, session)
        if member_data.birth_date is None:
            raise HTTPException(
                status_code=400,
                detail="User must have birth date to add legal representative",
            )

        MemberRepository.addLegalRepresentativeToPostgres(request.mb, legal_representative, session)
        return {"message": "Legal representative added successfully"}

    @staticmethod
    def add_legal_representative(
        mb: int,
        legal_representative: LegalRepresentativeCreate,
        token_data: Any,
        session: Session,
    ):
        MB = MemberRepository.getMBByEmail(token_data["email"], session)
        if MB != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")
        # user must be under 18 to add legal representative
        member_data = MemberRepository.getFromPostgres(mb, session)
        if member_data.birth_date is None:
            raise HTTPException(
                status_code=400,
                detail="User must have birth date to add legal representative",
            )
        birth_date = member_data.birth_date
        current_date = datetime.now().date()
        age = (
            current_date.year
            - birth_date.year
            - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))
        )

        if age > 18:
            raise HTTPException(
                status_code=400,
                detail="User must be under 18 to add legal representative",
            )
        # user can only have two legal representatives
        member_data = MemberRepository.getLegalRepresentativesFromPostgres(mb, session)
        if len(member_data) > 1:
            raise HTTPException(
                status_code=400, detail="User already has two legal representatives"
            )
        MemberRepository.addLegalRepresentativeToPostgres(mb, legal_representative, session)
        return {"message": "Legal representative added successfully"}

    @staticmethod
    def update_legal_representative(
        mb: int,
        legal_rep_id: int,
        updated_legal_rep: LegalRepresentativeUpdate,
        token_data: Any,
        session: Session,
    ):
        MB = MemberRepository.getMBByEmail(token_data["email"], session)
        if MB != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")

        # Call the update method to modify the legal representative
        success = MemberRepository.updateLegalRepresentativeInPostgres(
            mb, legal_rep_id, updated_legal_rep, session
        )
        if not success:
            raise HTTPException(status_code=404, detail="Legal representative not found")

        return {"message": "Legal representative updated successfully"}

    @staticmethod
    def delete_legal_representative(mb: int, legal_rep_id: int, token_data: Any, session: Session):
        MB = MemberRepository.getMBByEmail(token_data["email"], session)
        if MB != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")

        # Call the delete method to remove the legal representative
        success = MemberRepository.deleteLegalRepresentativeFromPostgres(mb, legal_rep_id, session)
        if not success:
            raise HTTPException(status_code=404, detail="Legal representative not found")

        return {"message": "Legal representative deleted successfully"}

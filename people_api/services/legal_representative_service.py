# mypy: ignore-errors

"""Service for legal representative operations."""

from datetime import datetime

from fastapi import HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from people_api.database.models.models import LegalRepresentatives, Registration
from people_api.schemas import UserToken

from ..settings import Settings

SETTINGS = Settings()


class LegalRepresentativeRequest(BaseModel):
    """Request model for adding legal representative with API key."""

    token: str
    mb: str
    birth_date: str
    cpf: str
    legal_representative: LegalRepresentatives


class LegalRepresentativeService:
    @staticmethod
    def add_legal_representative_api_key(request: LegalRepresentativeRequest, session: Session):
        """Add legal representative to member using API key."""
        if request.token != SETTINGS.whatsapp_route_api_key:
            raise HTTPException(status_code=401, detail="Unauthorized")
        request.mb = int(request.mb)
        reg_stmt = Registration.select_stmt_by_id(request.mb)
        member_data = session.exec(reg_stmt).first()
        if not member_data:
            raise HTTPException(status_code=404, detail="Member not found")

        request.birth_date = datetime.strptime(request.birth_date, "%d/%m/%Y").date()

        if member_data.birth_date != request.birth_date:
            raise HTTPException(status_code=400, detail="Birth date does not match")

        if member_data.cpf != request.cpf:
            raise HTTPException(status_code=400, detail="CPF does not match")

        if member_data.birth_date is None:
            raise HTTPException(
                status_code=400,
                detail="must have birth date to add legal representative",
            )

        stmt = LegalRepresentatives.insert_stmt_for_legal_representative(
            request.mb, request.legal_representative
        )
        session.exec(stmt)
        return {"message": "Legal representative added successfully"}

    @staticmethod
    def add_legal_representative(
        mb: int,
        legal_representative: LegalRepresentatives,
        token_data: UserToken,
        session: Session,
    ):
        """Add legal representative to member."""
        reg_stmt = Registration.select_stmt_by_email(token_data.email)
        member_data = session.exec(reg_stmt).first()
        if not member_data or member_data.registration_id != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")
        reg_stmt_by_id = Registration.select_stmt_by_id(mb)
        member_data = session.exec(reg_stmt_by_id).first()
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
        stmt_get_lr = LegalRepresentatives.get_legal_representatives_for_member(mb)
        existing_legal_reps = session.exec(stmt_get_lr).all()
        if len(existing_legal_reps) > 1:
            raise HTTPException(
                status_code=400, detail="User already has two legal representatives"
            )
        stmt_insert = LegalRepresentatives.insert_stmt_for_legal_representative(
            mb, legal_representative
        )
        session.exec(stmt_insert)
        return {"message": "Legal representative added successfully"}

    @staticmethod
    def update_legal_representative(
        mb: int,
        legal_rep_id: int,
        updated_legal_rep: LegalRepresentatives,
        token_data: UserToken,
        session: Session,
    ):
        """Update legal representative for member."""
        reg_stmt = Registration.select_stmt_by_email(token_data.email)
        member_data = session.exec(reg_stmt).first()
        if not member_data or member_data.registration_id != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")

        update_stmt = LegalRepresentatives.update_stmt_for_legal_representative(
            mb, legal_rep_id, updated_legal_rep
        )
        result = session.exec(update_stmt)
        if result.rowcount is None or result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Legal representative not found")
        return {"message": "Legal representative updated successfully"}

    @staticmethod
    def delete_legal_representative(
        mb: int, legal_rep_id: int, token_data: UserToken, session: Session
    ):
        """Delete legal representative from member."""
        reg_stmt = Registration.select_stmt_by_email(token_data.email)
        member_data = session.exec(reg_stmt).first()

        if not member_data or member_data.registration_id != mb:
            raise HTTPException(status_code=401, detail="Unauthorized")

        delete_stmt = LegalRepresentatives.delete_stmt_for_legal_representative(mb, legal_rep_id)
        result = session.exec(delete_stmt)

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Legal representative not found")

        return {"message": "Legal representative deleted successfully"}

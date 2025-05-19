"""Service for managing missing fields of members."""

from datetime import datetime

from fastapi import HTTPException
from pycpfcnpj.cpf import validate as validate_cpf
from sqlmodel import Session

from people_api.schemas import UserToken

from ..models.member_data import MissingFieldsCreate
from ..repositories import MemberRepository


class MissingFieldsService:
    """Service for managing missing fields of members."""

    @staticmethod
    def get_missing_fields(token_data: UserToken, session: Session):
        """Get missing fields for a member."""
        missing_fields = MemberRepository.getMissingFieldsFromPostgres(
            token_data.registration_id, session
        )
        return missing_fields

    @staticmethod
    def set_missing_fields(
        token_data: UserToken, missing_fields: MissingFieldsCreate, session: Session
    ):
        """Set missing fields for a member."""
        missing_fields_list = MemberRepository.getMissingFieldsFromPostgres(
            token_data.registration_id, session
        )

        if missing_fields.cpf is not None:
            if "cpf" in missing_fields_list:
                if not validate_cpf(missing_fields.cpf):
                    raise HTTPException(status_code=422, detail="Invalid CPF")

                MemberRepository.setCPFOnPostgres(
                    token_data.registration_id, missing_fields.cpf, session
                )
        if missing_fields.birth_date is not None:
            if "birth_date" in missing_fields_list:
                try:
                    birth_date = datetime.strptime(missing_fields.birth_date, "%Y-%m-%d").date()
                except ValueError:
                    try:
                        birth_date = datetime.strptime(
                            missing_fields.birth_date, "%Y-%m-%d %H:%M:%S.%f"
                        ).date()
                    except ValueError as e:
                        raise HTTPException(
                            status_code=422, detail="Invalid birth_date format"
                        ) from e
                MemberRepository.setBirthDateOnPostgres(
                    token_data.registration_id, birth_date, session
                )

        return {"message": "Missing fields set successfully"}

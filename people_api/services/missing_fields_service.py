"""Service for managing missing fields of members."""

from sqlalchemy.orm import Session

from ..models.member_data import MissingFieldsCreate
from ..repositories import MemberRepository


class MissingFieldsService:
    @staticmethod
    def get_missing_fields(token_data, session: Session):
        MB = MemberRepository.getMBByEmail(token_data["email"], session)
        missing_fields = MemberRepository.getMissingFieldsFromPostgres(MB, session)
        return missing_fields

    @staticmethod
    def set_missing_fields(token_data, missing_fields: MissingFieldsCreate, session: Session):
        MB = MemberRepository.getMBByEmail(token_data["email"], session)
        # check if user really has those fields missing, if not, deny
        missing_fields_list = MemberRepository.getMissingFieldsFromPostgres(MB, session)
        # set only fields that are missing
        if missing_fields.cpf is not None:
            if "cpf" in missing_fields_list:
                print("cpf")
                MemberRepository.setCPFOnPostgres(MB, missing_fields.cpf, session)
        if missing_fields.birth_date is not None:
            if "birth_date" in missing_fields_list:
                print("birth_date")
                MemberRepository.setBirthDateOnPostgres(MB, missing_fields.birth_date, session)
        return {"message": "Missing fields set successfully"}

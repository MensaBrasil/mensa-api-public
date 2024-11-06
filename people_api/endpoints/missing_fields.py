"""
Endpoints for managing missing fields of members.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from people_api.auth import verify_firebase_token
from people_api.dbs import get_session
from people_api.models.member_data import MissingFieldsCreate
from people_api.repositories import MemberRepository

missing_fields_router = APIRouter()


# every user must have cpf, birth_date. if it doesnt have one of these, return the list of the missing fields
@missing_fields_router.get(
    "/missing_fields",
    description="Get missing fields from member",
    tags=["missing_fields"],
)
async def _get_missing_fields(
    token_data=Depends(verify_firebase_token), session: Session = Depends(get_session)
):
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    missing_fields = MemberRepository.getMissingFieldsFromPostgres(MB, session)
    return missing_fields


# set the missing fields of a member
@missing_fields_router.post(
    "/missing_fields",
    description="Set missing fields from member",
    tags=["missing_fields"],
)
async def _set_missing_fields(
    missing_fields: MissingFieldsCreate,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
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

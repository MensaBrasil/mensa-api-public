"""Endpoints for managing missing fields of members."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import verify_firebase_token
from ..dbs import get_session
from ..models.member_data import MissingFieldsCreate
from ..services import MissingFieldsService

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
    return MissingFieldsService.get_missing_fields(token_data, session)


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
    return MissingFieldsService.set_missing_fields(token_data, missing_fields, session)

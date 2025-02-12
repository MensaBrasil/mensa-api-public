"""Endpoints for managing members emails."""

from fastapi import APIRouter, Depends
from sqlmodel import Session

from people_api.database.models.models import EmailInput

from ..auth import verify_firebase_token
from ..dbs import get_session
from ..services import EmailService

member_email_router = APIRouter()


# add email to member
@member_email_router.post("/email/{mb}", description="Add email to member", tags=["email"])
async def _add_email(
    mb: int,
    email: EmailInput,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    return EmailService.add_email(mb, email, token_data, session)


# update email from member
@member_email_router.put(
    "/email/{mb}/{email_id}", description="Update email for member", tags=["email"]
)
async def update_email(
    mb: int,
    email_id: int,
    updated_email: EmailInput,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    return EmailService.update_email(mb, email_id, updated_email, token_data, session)


# delete email from member
@member_email_router.delete(
    "/email/{mb}/{email_id}", description="Delete email from member", tags=["email"]
)
async def delete_email(
    mb: int,
    email_id: int,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    return EmailService.delete_email(mb, email_id, token_data, session)

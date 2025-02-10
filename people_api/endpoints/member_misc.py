"""Endpoints for managing miscellaneous member-related operations in the .."""

from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..auth import verify_firebase_token
from ..dbs import get_session
from ..exceptions import PersonNotFoundException, get_exception_responses
from ..models.member import PostgresMemberRead, PronounsCreate
from ..models.member_data import MemberProfessionFacebookUpdate
from ..services import MiscService

member_misc_router = APIRouter()


@member_misc_router.get(
    "/get_member/{mb}",
    response_model=PostgresMemberRead,
    description="Get a single member by its unique ID",
    responses=get_exception_responses(PersonNotFoundException),
    tags=["member"],
)
async def _get_member(
    mb: int,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    return MiscService.get_member(mb, token_data, session)


@member_misc_router.patch("/pronouns", description="Set pronouns for member", tags=["member"])
async def _set_pronouns(
    pronouns: PronounsCreate,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    return MiscService.set_pronouns(pronouns, token_data, session)


@member_misc_router.put(
    "/update_fb_profession/{mb}",
    description="Update profession and facebook url for member",
    tags=["member"],
)
async def update_fb_profession(
    mb: int,
    updated_member: MemberProfessionFacebookUpdate,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    return MiscService.update_fb_profession(mb, updated_member, token_data, session)

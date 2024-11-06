"""
Endpoints for managing member-related operations in the people_api.

Endpoints:
- /get_member/{mb}: Get a single member by its unique ID.
- /pronouns: Set pronouns for a member.
- /update_fb_profession/{mb}: Update profession and Facebook URL for a member.
"""

import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from people_api.auth import verify_firebase_token
from people_api.dbs import get_session
from people_api.exceptions import PersonNotFoundException, get_exception_responses
from people_api.models.member import PostgresMemberRead, PronounsCreate
from people_api.models.member_data import (
    MemberProfessionFacebookUpdate,
)
from people_api.repositories import MemberRepository

member_misc_router = APIRouter()


@member_misc_router.get(
    "/get_member/{mb}",
    response_model=PostgresMemberRead,
    description="Get a single member by its unique ID",
    responses=get_exception_responses(PersonNotFoundException),
    tags=["member"],
)
# , token: string = Depends(verify_firebase_token)
async def _get_member(
    mb: int,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    MB = MemberRepository.getMBByEmail(token_data["email"], session)

    member_data = MemberRepository.getAllMemberDataFromPostgres(MB, session)

    try:
        # Parse the JSON string into a Python dictionary
        member_data_dict = json.loads(member_data)
    except json.JSONDecodeError:
        # Handle JSON decoding errors
        raise HTTPException(status_code=400, detail="Invalid JSON format")

    try:
        # Validate the data with your Pydantic model
        validated_data = PostgresMemberRead(**member_data_dict)
    except ValidationError as e:
        # If validation fails, print the error details
        print(e.json())
        # Optionally, raise an HTTPException to notify about a failure
        raise HTTPException(status_code=400, detail="Data validation failed")

    return validated_data


# set user pronouns
@member_misc_router.patch("/pronouns", description="Set pronouns for member", tags=["member"])
async def _set_pronouns(
    pronouns: PronounsCreate,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    # should only accept Ele/dele, Ela/dela, Elu/delu
    if (
        pronouns.pronouns != "Ele/dele"
        and pronouns.pronouns != "Ela/dela"
        and pronouns.pronouns != "Elu/delu"
        and pronouns.pronouns != "Nenhuma das opções"
    ):
        raise HTTPException(
            status_code=400,
            detail="Pronouns must be Ele/dele, Ela/dela or Elu/delu or Nenhuma das opções",
        )
    MemberRepository.setPronounsOnPostgres(MB, pronouns.pronouns, session)
    return {"message": "Pronouns set successfully"}


# update Profession and Facebook url in Postgres
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
    # Get firebase user data of user token_data['uid']
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    if MB != mb:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # Call the update method to modify the member
    profession = updated_member.profession
    facebook = updated_member.facebook
    success = MemberRepository.updateProfessionAndFacebookOnPostgres(
        mb, profession, facebook, session
    )
    if not success:
        raise HTTPException(status_code=404, detail="Member not found")

    return {"message": "Member updated successfully"}

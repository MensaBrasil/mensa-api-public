"""
Endpoints for managing legal representatives of members.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from people_api.auth import verify_firebase_token
from people_api.dbs import get_session
from people_api.models.member_data import (
    LegalRepresentativeCreate,
    LegalRepresentativeUpdate,
)
from people_api.repositories import MemberRepository
from people_api.settings import DataRouteSettings

member_legal_representative_router = APIRouter()


# Model for request to add legal representative using API key
class LegalRepresentativeRequest(BaseModel):
    token: str
    mb: str
    birth_date: str
    cpf: str
    legal_representative: LegalRepresentativeCreate


# add legal representative to member using API key
@member_legal_representative_router.post(
    "/legal_representative_twilio",
    description="Add legal representative to member using API key authentication",
    tags=["legal_representative"],
)
async def add_legal_representative_api_key(
    request: LegalRepresentativeRequest,
    session: Session = Depends(get_session),
):
    if request.token != DataRouteSettings.whatsapp_api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")

    request.mb = int(request.mb)
    member_data = MemberRepository.getFromPostgres(request.mb, session)

    try:
        request.birth_date = datetime.strptime(request.birth_date, "%d/%m/%Y").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid birth date format. Use dd/mm/YYYY.")

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


# add legal representative to member
@member_legal_representative_router.post(
    "/legal_representative/{mb}",
    description="Add legal representative to member",
    tags=["legal_representative"],
)
async def _add_legal_representative(
    mb: int,
    legal_representative: LegalRepresentativeCreate,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
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
            status_code=400, detail="User must be under 18 to add legal representative"
        )
    # user can only have two legal representatives
    member_data = MemberRepository.getLegalRepresentativesFromPostgres(mb, session)
    if len(member_data) > 1:
        raise HTTPException(status_code=400, detail="User already has two legal representatives")
    MemberRepository.addLegalRepresentativeToPostgres(mb, legal_representative, session)
    return {"message": "Legal representative added successfully"}


# update legal representative from member
@member_legal_representative_router.put(
    "/legal_representative/{mb}/{legal_rep_id}",
    description="Update legal representative for member",
    tags=["legal_representative"],
)
async def update_legal_representative(
    mb: int,
    legal_rep_id: int,
    updated_legal_rep: LegalRepresentativeUpdate,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
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


# delete legal representative from member
@member_legal_representative_router.delete(
    "/legal_representative/{mb}/{legal_rep_id}",
    description="Delete legal representative from member",
    tags=["legal_representative"],
)
async def delete_legal_representative(
    mb: int,
    legal_rep_id: int,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    if MB != mb:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Call the delete method to remove the legal representative
    success = MemberRepository.deleteLegalRepresentativeFromPostgres(mb, legal_rep_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="Legal representative not found")

    return {"message": "Legal representative deleted successfully"}

"""Endpoints for managing legal representatives of members."""

from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..auth import verify_firebase_token
from ..dbs import get_session
from ..models.member_data import (
    LegalRepresentativeCreate,
    LegalRepresentativeUpdate,
)
from ..services.legal_representative_service import (
    LegalRepresentativeRequest,
    LegalRepresentativeService,
)

member_legal_representative_router = APIRouter()


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
    return LegalRepresentativeService.add_legal_representative_api_key(request, session)


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
    return LegalRepresentativeService.add_legal_representative(
        mb, legal_representative, token_data, session
    )


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
    return LegalRepresentativeService.update_legal_representative(
        mb, legal_rep_id, updated_legal_rep, token_data, session
    )


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
    return LegalRepresentativeService.delete_legal_representative(
        mb, legal_rep_id, token_data, session
    )

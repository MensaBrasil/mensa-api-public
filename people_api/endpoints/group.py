"""
Endpoints for managing member WhatsApp groups and group join requests.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from people_api.auth import verify_firebase_token
from people_api.dbs import get_session
from people_api.models.member import GroupJoinRequest
from people_api.repositories import MemberRepository

group_router = APIRouter()


@group_router.get("/get_member_groups", description="Get member groups", tags=["member"])
async def _get_member_groups(
    token_data=Depends(verify_firebase_token), session: Session = Depends(get_session)
):
    MB = MemberRepository.getMBByEmail(token_data["email"], session)
    member_groups = MemberRepository.getMemberGroupsFromPostgres(MB, session)
    return member_groups


@group_router.post("/request_join_group", tags=["member"], description="Request to join a group")
async def _request_join_group(
    join_request: GroupJoinRequest,
    token_data=Depends(verify_firebase_token),
    session: Session = Depends(get_session),
):
    registration_id = MemberRepository.getMBByEmail(token_data["email"], session)
    phones = MemberRepository.getAllMemberAndLegalRepPhonesFromPostgres(registration_id, session)

    # Raise an HTTPException if no phones are associated with the user
    if not phones:
        raise HTTPException(
            status_code=400,
            detail="Não há número de telefone registrado para o usuário.",
        )

    # for each phone, add a request
    for phone in phones:
        # check if a request exists for the phone
        if (
            MemberRepository.getGroupRequestId(phone["phone"], join_request.group_id, session)
            is None
        ):
            # check if phone is not an empty string and has more than 6 characters
            if phone["phone"] == "" or len(phone["phone"]) < 6:
                print("error: Phone is not valid")
            else:
                created_at = datetime.now()
                last_attempt = None
                fulfilled = False

                # Add request to join group in the database
                MemberRepository.addGroupRequest(
                    registration_id,
                    phone["phone"],
                    join_request.group_id,
                    created_at,
                    last_attempt,
                    fulfilled,
                    session,
                )
    return {"message": "Request to join group sent successfully"}

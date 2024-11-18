"""Service for handling requests from group endpoints."""

from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models.member import GroupJoinRequest
from ..repositories import MemberRepository


class GroupService:
    @staticmethod
    def get_member_groups(token_data, session: Session):
        MB = MemberRepository.getMBByEmail(token_data["email"], session)
        member_groups = MemberRepository.getMemberGroupsFromPostgres(MB, session)
        return member_groups

    @staticmethod
    def request_join_group(join_request: GroupJoinRequest, token_data, session: Session):
        registration_id = MemberRepository.getMBByEmail(token_data["email"], session)
        phones = MemberRepository.getAllMemberAndLegalRepPhonesFromPostgres(
            registration_id, session
        )

        # Raise an HTTPException if no phones are associated with the user
        if not phones:
            raise HTTPException(
                status_code=400, detail="Não há número de telefone registrado para o usuário."
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

"""Service for handling requests from group endpoints."""

from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models.member import GroupJoinRequest
from ..repositories import MemberRepository


class GroupService:
    @staticmethod
    def get_member_groups_info(token_data, session: Session):
        MB = MemberRepository.getMBByEmail(token_data["email"], session)
        can_participate = MemberRepository.getCanParticipate(MB, session)
        participate_in = MemberRepository.getParticipateIn(MB, session)
        pending_requests = MemberRepository.getPendingRequests(MB, session)
        failed_requests = MemberRepository.getFailedRequests(MB, session)

        response_data = {
            "can_participate": can_participate,
            "participate_in": participate_in,
            "pending_requests": pending_requests,
            "failed_requests": failed_requests,
        }

        return response_data

    @staticmethod
    def request_join_group(join_request: GroupJoinRequest, token_data, session: Session):
        registration_id = MemberRepository.getMBByEmail(token_data["email"], session)
        phones = MemberRepository.getAllMemberAndLegalRepPhonesFromPostgres(
            registration_id, session
        )
        pending_group_requests = MemberRepository.getUnfullfilledGroupRequests(
            registration_id, session
        )
        failed_group_requests = MemberRepository.getFailedGroupRequests(registration_id, session)

        # Raise an HTTPException if no phones are associated with the user
        if not phones:
            raise HTTPException(
                status_code=400,
                detail="Não há número de telefone registrado para o usuário.",
            )

        # check if a request exists for the member for the current group request
        if join_request.group_id in pending_group_requests:
            raise HTTPException(
                status_code=409, detail="Já existe uma solicitação pendente para este grupo."
            )

        if join_request.group_id in failed_group_requests:
            if MemberRepository.updateFailedGroupRequests(registration_id, session):
                return {"message": "Request to join group sent successfully"}

        else:
            created_at = datetime.now()
            last_attempt = None
            fulfilled = False

            # Add request to join group in the database
            MemberRepository.addGroupRequest(
                registration_id,
                join_request.group_id,
                created_at,
                last_attempt,
                fulfilled,
                session,
            )
        return {"message": "Request to join group sent successfully"}

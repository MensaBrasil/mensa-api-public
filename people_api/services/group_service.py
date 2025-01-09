"""Service for handling requests from group endpoints."""

from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models.member import GroupJoinRequest
from ..repositories import MemberRepository


class GroupService:
    """Service for handling requests from group endpoints."""

    @staticmethod
    def get_can_participate(token_data, session: Session):
        """Determines if a member can participate based on their email."""

        MB = MemberRepository.getMBByEmail(token_data["email"], session)
        can_participate = MemberRepository.getCanParticipate(MB, session)
        return can_participate

    @staticmethod
    def get_participate_in(token_data, session: Session):
        """Retrieves the groups that a member is participating in."""

        MB = MemberRepository.getMBByEmail(token_data["email"], session)
        participate_in = MemberRepository.getParticipateIn(MB, session)
        return participate_in

    @staticmethod
    def get_pending_requests(token_data, session: Session):
        """Retrieves the pending group join requests for a member."""

        MB = MemberRepository.getMBByEmail(token_data["email"], session)
        pending_requests = MemberRepository.getPendingRequests(MB, session)
        return pending_requests

    @staticmethod
    def get_failed_requests(token_data, session: Session):
        """Retrieves the failed group join requests for a member."""

        MB = MemberRepository.getMBByEmail(token_data["email"], session)
        failed_requests = MemberRepository.getFailedRequests(MB, session)
        return failed_requests

    @staticmethod
    def request_join_group(join_request: GroupJoinRequest, token_data, session: Session):
        """Handles a request to join a group."""

        registration_id = MemberRepository.getMBByEmail(token_data["email"], session)
        phones = MemberRepository.getAllMemberAndLegalRepPhonesFromPostgres(
            registration_id, session
        )
        pending_group_requests = MemberRepository.getUnfullfilledGroupRequests(
            registration_id, session
        )
        failed_group_requests = MemberRepository.getFailedGroupRequests(registration_id, session)

        if not phones:
            raise HTTPException(
                status_code=400,
                detail="Não há número de telefone registrado para o usuário.",
            )

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

            MemberRepository.addGroupRequest(
                registration_id,
                join_request.group_id,
                created_at,
                last_attempt,
                fulfilled,
                session,
            )
        return {"message": "Request to join group sent successfully"}

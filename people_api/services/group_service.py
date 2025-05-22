# mypy: ignore-errors

"""Service for handling requests from group endpoints."""

from datetime import datetime

from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from people_api.schemas import InternalToken, UserToken

from ..database.models import Registration
from ..enums import Gender
from ..models.member import GroupJoinRequest
from ..repositories import MemberRepository


class GroupService:
    """Service for handling requests from group endpoints."""

    @staticmethod
    async def get_can_participate(
        token_data: UserToken | InternalToken, session: AsyncSession
    ) -> list:
        """Determines if a member can participate based on their email."""
        member_reg = (
            await session.exec(
                Registration.select_stmt_by_id(registration_id=token_data.registration_id)
            )
        ).first()
        if not member_reg:
            raise HTTPException(
                status_code=404,
                detail="Member not found",
            )
        can_participate = await MemberRepository.getCanParticipate(member_reg, session)
        if member_reg.gender != Gender.FEMALE:
            can_participate = [g for g in can_participate if g.get("group_name") != "MB | Mulheres"]
        return can_participate

    @staticmethod
    async def get_participate_in(token_data: UserToken | InternalToken, session: AsyncSession):
        """Retrieves the groups that a member is participating in."""

        participate_in = await MemberRepository.getParticipateIn(
            token_data.registration_id, session
        )
        return participate_in

    @staticmethod
    async def get_pending_requests(token_data: UserToken | InternalToken, session: AsyncSession):
        """Retrieves the pending group join requests for a member."""

        pending_requests = await MemberRepository.getPendingRequests(
            token_data.registration_id, session
        )
        return pending_requests

    @staticmethod
    async def get_failed_requests(token_data: UserToken | InternalToken, session: AsyncSession):
        """Retrieves the failed group join requests for a member."""

        failed_requests = await MemberRepository.getFailedRequests(
            token_data.registration_id, session
        )
        return failed_requests

    @staticmethod
    async def request_join_group(
        join_request: GroupJoinRequest, token_data: UserToken | InternalToken, session: AsyncSession
    ):
        """Handles a request to join a group."""

        phones = await MemberRepository.getAllMemberAndLegalRepPhonesFromPostgres(
            token_data.registration_id, session
        )
        pending_group_requests = await MemberRepository.getUnfullfilledGroupRequests(
            token_data.registration_id, session
        )
        failed_group_requests = await MemberRepository.getFailedGroupRequests(
            token_data.registration_id, session
        )

        if not phones:
            raise HTTPException(
                status_code=400,
                detail="Não há número de telefone registrado para o usuário.",
            )

        if join_request.group_id in pending_group_requests:
            raise HTTPException(
                status_code=409,
                detail="Já existe uma solicitação pendente para este grupo.",
            )

        if join_request.group_id in failed_group_requests:
            if await MemberRepository.updateFailedGroupRequests(
                token_data.registration_id, session
            ):
                return {"message": "Request to join group sent successfully"}

        else:
            created_at = datetime.now()
            last_attempt = None
            fulfilled = False

            await MemberRepository.addGroupRequest(
                token_data.registration_id,
                join_request.group_id,
                created_at,
                last_attempt,
                fulfilled,
                session,
            )
        return {"message": "Request to join group sent successfully"}

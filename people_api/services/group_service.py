# mypy: ignore-errors

"""Service for handling requests from group endpoints."""

from datetime import datetime

from fastapi import HTTPException
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from people_api.database.models.models import WhatsappAuthorization
from people_api.schemas import InternalToken, UserToken

from ..database.models import (
    LegalRepresentatives,
    Phones,
    Registration,
)
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
        join_request: GroupJoinRequest,
        token_data: UserToken | InternalToken,
        session: AsyncSession,
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

    @staticmethod
    async def get_authorization_status(
        token_data: UserToken | InternalToken, session: AsyncSession
    ) -> dict:
        """Retrieves the authorization status for a member."""

        registration = (
            await session.exec(
                Registration.select_stmt_by_id(registration_id=token_data.registration_id)
            )
        ).first()

        if not registration:
            raise HTTPException(
                status_code=404,
                detail="Unauthorized, registration not found",
            )

        today = datetime.now()
        birth_date = registration.birth_date
        age = (
            today.year
            - birth_date.year
            - ((today.month, today.day) < (birth_date.month, birth_date.day))
        )

        member_phone = (
            await session.exec(
                select(Phones.phone_number).where(
                    Phones.registration_id == registration.registration_id
                )
            )
        ).first()

        member_auth = None
        if member_phone:
            member_auth = (
                await session.exec(WhatsappAuthorization.select_stmt_by_last_8_digits(member_phone))
            ).first()

        member = {
            "type": "member",
            "name": f"{' '.join(registration.name.split()[0:1] + registration.name.split()[-1:]).title()}",
            "phone_number": member_phone if member_phone else None,
            "authorization_status": member_auth.authorized if member_auth else False,
        }

        legal_representatives = []
        if age < 18:
            reps = (
                await session.exec(
                    select(
                        LegalRepresentatives.phone,
                        LegalRepresentatives.full_name,
                        WhatsappAuthorization.authorized,
                    )
                    .join(
                        WhatsappAuthorization,
                        func.right(WhatsappAuthorization.phone_number, 8)
                        == func.right(LegalRepresentatives.phone, 8),
                        isouter=True,
                    )
                    .where(LegalRepresentatives.registration_id == registration.registration_id)
                )
            ).all()
            for phone, name, authorized in reps:
                legal_representatives.append(
                    {
                        "type": "legal_representative",
                        "name": f"{' '.join(name.split()[0:1] + name.split()[-1:]).title()}",
                        "phone_number": phone,
                        "authorization_status": authorized if authorized is not None else False,
                    }
                )

        authorization_status = [member] + legal_representatives

        return authorization_status

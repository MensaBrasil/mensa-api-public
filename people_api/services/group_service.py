# mypy: ignore-errors

"""Service for handling requests from group endpoints."""

from datetime import datetime

from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from people_api.database.models.models import (
    LegalRepresentatives,
    Phones,
    Registration,
    WhatsappAuthorization,
    WhatsappWorkers,
)
from people_api.schemas import InternalToken, UserToken

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

        member_phone_records = (
            await session.exec(
                select(Phones.phone_number).where(
                    Phones.registration_id == registration.registration_id
                )
            )
        ).all()
        member_phones = list(member_phone_records)
        member_phones_map = {phone[-8:]: phone for phone in member_phones}

        legal_rep_phones = []
        legal_rep_phones_map = {}
        if age < 18:
            legal_rep_phone_records = (
                await session.exec(
                    select(LegalRepresentatives.phone).where(
                        LegalRepresentatives.registration_id == registration.registration_id
                    )
                )
            ).all()
            legal_rep_phones = list(legal_rep_phone_records)
            legal_rep_phones_map = {phone[-8:]: phone for phone in legal_rep_phones}

        workers = (await session.exec(select(WhatsappWorkers))).all()

        authorization_status = {"authorizations": {}}

        for worker in workers:
            worker_phone = worker.worker_phone

            authorization_status["authorizations"][worker_phone] = {
                "authorized_numbers": {},
                "pending_authorization": {},
            }

            authorizations = (
                await session.exec(
                    select(WhatsappAuthorization).where(
                        WhatsappAuthorization.worker_id == worker.id
                    )
                )
            ).all()

            authorized_phone_last_8_digits = {auth.phone_number[-8:] for auth in authorizations}

            for phone_last_8 in member_phones_map:
                full_phone = member_phones_map[phone_last_8]
                if phone_last_8 in authorized_phone_last_8_digits:
                    authorization_status["authorizations"][worker_phone]["authorized_numbers"][
                        full_phone
                    ] = "member"
                else:
                    authorization_status["authorizations"][worker_phone]["pending_authorization"][
                        full_phone
                    ] = "member"

            if age < 18:
                for phone_last_8 in legal_rep_phones_map:
                    full_phone = legal_rep_phones_map[phone_last_8]
                    if phone_last_8 in authorized_phone_last_8_digits:
                        authorization_status["authorizations"][worker_phone]["authorized_numbers"][
                            full_phone
                        ] = "legal_rep"
                    else:
                        authorization_status["authorizations"][worker_phone][
                            "pending_authorization"
                        ][full_phone] = "legal_rep"

        return authorization_status

    @staticmethod
    async def get_workers(session: AsyncSession) -> list:
        """Retrieves the workers in the database."""

        workers = (await session.exec(select(WhatsappWorkers))).all()
        return workers

    @staticmethod
    async def add_worker(
        worker_phone: str,
        session: AsyncSession,
    ) -> dict:
        """Adds a worker to the database."""

        if not worker_phone:
            raise HTTPException(status_code=400, detail="Worker phone number is required.")

        existing_worker = (
            await session.exec(
                select(WhatsappWorkers).where(WhatsappWorkers.worker_phone == worker_phone)
            )
        ).first()

        if existing_worker:
            raise HTTPException(status_code=409, detail="Worker already exists in the database.")

        new_worker = WhatsappWorkers(worker_phone=worker_phone)
        session.add(new_worker)

        return {"message": "Worker added successfully"}

    @staticmethod
    async def remove_worker(
        worker_phone: str,
        session: AsyncSession,
    ) -> dict:
        """Removes a worker from the database."""

        if not worker_phone:
            raise HTTPException(status_code=400, detail="Worker phone number is required.")

        existing_worker = (
            await session.exec(
                select(WhatsappWorkers).where(WhatsappWorkers.worker_phone == worker_phone)
            )
        ).first()

        if not existing_worker:
            raise HTTPException(status_code=404, detail="Worker not found in the database.")

        await session.delete(existing_worker)

        return {"message": "Worker removed successfully"}

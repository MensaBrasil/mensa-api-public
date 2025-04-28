"""Service for updating WhatsApp-related data for members and their representatives."""

import json
import re
from datetime import datetime

from fastapi import HTTPException
from pydantic import BaseModel
from sqlmodel import text
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.status import HTTP_403_FORBIDDEN

from ...database.models.models import (
    Addresses,
    Emails,
    LegalRepresentatives,
    Phones,
    Registration,
)
from ...database.models.whatsapp import UpdateInput
from ...settings import get_settings

SETTINGS = get_settings()

API_KEY = SETTINGS.whatsapp_route_api_key


class QueryResponse(BaseModel):
    """Response model for the WhatsAppService update_data method."""

    message: str | None = None


class WhatsAppService:
    """Service for updating WhatsApp-related data for members and their representatives."""

    @staticmethod
    async def get_all_member_data(member_id: int, session: AsyncSession) -> str:
        """
        Retrieve all member-related data asynchronously and return it as a JSON string.
        This mimics the logic from MemberData.get_all_member_data.
        """

        addresses_stmt = Addresses.get_address_for_member(member_id)
        addresses_result = await session.exec(addresses_stmt)
        addresses = addresses_result.all()
        addresses = [address.model_dump() for address in addresses]

        phones_stmt = Phones.get_phones_for_member(member_id)
        phones_result = await session.exec(phones_stmt)
        phones = phones_result.all()
        phones = [phone.model_dump() for phone in phones]

        emails_stmt = Emails.get_emails_for_member(member_id)
        emails_result = await session.exec(emails_stmt)
        emails = emails_result.all()
        emails = [email.model_dump() for email in emails]

        member_stmt = Registration.select_stmt_by_id(member_id)
        member_result = await session.exec(member_stmt)
        member = member_result.first()
        member = member.model_dump() if member is not None else None

        legal_reps_stmt = LegalRepresentatives.get_legal_representatives_for_member(member_id)
        legal_reps_result = await session.exec(legal_reps_stmt)
        legal_representatives = legal_reps_result.all()
        legal_representatives = [rep.model_dump() for rep in legal_representatives]

        member_info = {
            "addresses": addresses,
            "phones": phones,
            "emails": emails,
            "member": member,
            "legal_representatives": legal_representatives,
        }

        json_data = json.dumps(member_info, default=str)
        return json_data

    @staticmethod
    async def update_data(update_input: UpdateInput, session: AsyncSession) -> QueryResponse:
        """Update the phone number for a member or representative."""
        if update_input.token != API_KEY:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API Key")

        def strip_non_numeric(cpf: str) -> str:
            return re.sub(r"\D", "", cpf)

        def convert_birth_date(birth_date_str: str) -> datetime:
            try:
                return datetime.strptime(birth_date_str, "%d/%m/%Y")
            except ValueError as e:
                raise HTTPException(
                    status_code=400, detail="Invalid birth date format. Use dd/mm/YYYY."
                ) from e

        def convert_member_birth_date(birth_date_str: str) -> datetime:
            try:
                return datetime.strptime(birth_date_str, "%Y-%m-%d")
            except ValueError as e:
                raise HTTPException(
                    status_code=500, detail="Invalid birth date format in the database."
                ) from e

        clean_input_cpf = strip_non_numeric(update_input.cpf)

        member_json = await WhatsAppService.get_all_member_data(
            update_input.registration_id, session
        )

        if not member_json:
            raise HTTPException(status_code=404, detail="Member not found")

        member_data = json.loads(member_json)
        member_info = member_data.get("member")
        legal_reps = member_data.get("legal_representatives", [])

        if update_input.is_representative:
            matching_rep = next(
                (rep for rep in legal_reps if strip_non_numeric(rep.get("cpf")) == clean_input_cpf),
                None,
            )
            if not matching_rep:
                raise HTTPException(
                    status_code=400,
                    detail="Representative CPF does not match any records",
                )

            try:
                await session.execute(
                    text("UPDATE legal_representatives SET phone = :phone WHERE cpf = :cpf"),
                    {"phone": update_input.phone, "cpf": matching_rep.get("cpf")},
                )
                return QueryResponse(message="Representative's phone number updated successfully.")
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail="An error occurred while updating the representative's phone number",
                ) from e
        else:
            if not member_info:
                raise HTTPException(status_code=404, detail="Member information not found")

            if strip_non_numeric(member_info.get("cpf")) != clean_input_cpf:
                raise HTTPException(status_code=400, detail="CPF does not match")

            member_birth_date_str = member_info.get("birth_date")
            if member_birth_date_str is None:
                raise HTTPException(status_code=400, detail="Birth date is not set for this member")

            api_birth_date = convert_birth_date(update_input.birth_date)  # type: ignore
            member_birth_date = convert_member_birth_date(member_birth_date_str)

            if member_birth_date.date() != api_birth_date.date():
                raise HTTPException(status_code=400, detail="Date of birth does not match")

            try:
                await session.execute(
                    text("DELETE FROM phones WHERE registration_id = :registration_id"),
                    {"registration_id": update_input.registration_id},
                )
                await session.execute(
                    text(
                        "INSERT INTO phones (registration_id, phone_number) VALUES (:registration_id, :phone_number)"
                    ),
                    {
                        "registration_id": update_input.registration_id,
                        "phone_number": update_input.phone,
                    },
                )
                return QueryResponse(message="Phone number updated successfully.")
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"An error occurred while updating the phone number: {e}",
                ) from e

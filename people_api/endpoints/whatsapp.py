"""Whatsapp endpoint for updating phone numbers for members and their legal representatives."""

import json
import re
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.status import HTTP_403_FORBIDDEN

from ..database.models import UpdateInput
from ..dbs import get_session
from ..repositories import MemberRepository
from ..settings import DataRouteSettings


class QueryResponse(BaseModel):
    message: str | None = None


whatsapp_router = APIRouter(tags=["Whatsapp"], prefix="/whatsapp")

API_KEY = DataRouteSettings.whatsapp_api_key


@whatsapp_router.post("/update-data")
async def update_data(
    update_input: UpdateInput,
    session: Session = Depends(get_session),
):
    """
    Whatsapp endpoint for updating phone numbers for members and their legal representatives.

    Step 1: Ensure that authentication is checked first before proceeding with any CPF or phone number validation.
    """
    if update_input.token != API_KEY:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API Key")

    def strip_non_numeric(cpf: str) -> str:
        return re.sub(r"\D", "", cpf)

    # Convert birth_date from dd/mm/YYYY string to a datetime object
    def convert_birth_date(birth_date_str: str) -> datetime:
        try:
            return datetime.strptime(birth_date_str, "%d/%m/%Y")
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid birth date format. Use dd/mm/YYYY."
            )

    # Convert member_birth_date from YYYY-MM-DD string to a datetime object
    def convert_member_birth_date(birth_date_str: str) -> datetime:
        try:
            return datetime.strptime(birth_date_str, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=500, detail="Invalid birth date format in the database."
            )

    # Strip non-numeric characters from CPF inputs
    clean_input_cpf = strip_non_numeric(update_input.cpf)

    # Proceed with CPF and other validations after authentication
    member_json = MemberRepository.getAllMemberDataFromPostgres(
        update_input.registration_id, session
    )

    if not member_json:
        raise HTTPException(status_code=404, detail="Member not found")

    member_data = json.loads(member_json)
    member_info = member_data.get("member")
    legal_reps = member_data.get("legal_representatives", [])

    # Handling representative updates
    if update_input.is_representative:
        matching_rep = next(
            (rep for rep in legal_reps if strip_non_numeric(rep.get("cpf")) == clean_input_cpf),
            None,
        )
        if not matching_rep:
            raise HTTPException(
                status_code=400, detail="Representative CPF does not match any records"
            )

        try:
            session.execute(
                text("UPDATE legal_representatives SET phone = :phone WHERE cpf = :cpf"),
                {"phone": update_input.phone, "cpf": matching_rep.get("cpf")},
            )
            session.commit()
            return QueryResponse(message="Representative's phone number updated successfully.")
        except Exception as e:
            session.rollback()
            print(f"Error occurred while updating representative: {e}")  # Debugging log
            raise HTTPException(
                status_code=500,
                detail="An error occurred while updating the representative's phone number",
            ) from e
    else:
        # Handling member updates
        if not member_info:
            raise HTTPException(status_code=404, detail="Member information not found")

        if strip_non_numeric(member_info.get("cpf")) != clean_input_cpf:
            raise HTTPException(status_code=400, detail="CPF does not match")

        member_birth_date_str = member_info.get("birth_date")
        if member_birth_date_str is None:
            raise HTTPException(status_code=400, detail="Birth date is not set for this member")

        # Convert the birth date from the API and database for comparison
        api_birth_date = convert_birth_date(update_input.birth_date)
        member_birth_date = convert_member_birth_date(member_birth_date_str)

        # Compare the dates, making sure to only compare the date parts (ignoring time)
        if member_birth_date.date() != api_birth_date.date():
            raise HTTPException(status_code=400, detail="Date of birth does not match")

        try:
            session.execute(
                text("DELETE FROM phones WHERE registration_id = :registration_id"),
                {"registration_id": update_input.registration_id},
            )
            session.execute(
                text(
                    "INSERT INTO phones (registration_id, phone_number) VALUES (:registration_id, :phone_number)"
                ),
                {
                    "registration_id": update_input.registration_id,
                    "phone_number": update_input.phone,
                },
            )
            session.commit()
            return QueryResponse(message="Phone number updated successfully.")
        except Exception as e:
            session.rollback()
            print(f"Error occurred while updating member: {e}")  # Debugging log
            raise HTTPException(
                status_code=500, detail=f"An error occurred while updating the phone number: {e}"
            ) from e

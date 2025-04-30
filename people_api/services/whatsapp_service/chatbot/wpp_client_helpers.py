"""Helper functions for WhatsApp Client"""

import logging
from datetime import date

import httpx
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

from people_api.auth import create_token
from people_api.database.models.models import Emails, Registration
from people_api.services.membership_payment_service import MembershipPaymentService

from ....settings import get_settings


class MemberInfo(BaseModel):
    """Model for member information."""

    name: str
    registration_id: int
    birth_date: date
    expiration_date: date | None
    email_mensa: str


async def get_member_info_by_phone_number(phone_number: str, session: AsyncSession) -> MemberInfo:
    """Get member info by phone number."""
    registration = (
        await session.exec(Registration.get_registration_by_last_8_phone_digits(phone_number))
    ).first()

    if not registration:
        raise ValueError("Nenhum registro encontrado para o número de telefone fornecido.")

    payment = await MembershipPaymentService.get_last_payment(registration.registration_id, session)

    email_result = (
        await session.exec(Emails.get_emails_for_member(registration.registration_id))
    ).all()
    for email in email_result:
        if email.email_address.endswith("@mensa.org.br"):
            email = email.email_address
            break
    else:
        email = "N/A"

    return MemberInfo(
        name=registration.name.lower().title(),
        registration_id=registration.registration_id,
        birth_date=registration.birth_date,
        expiration_date=payment.expiration_date if payment else None,
        email_mensa=email,
    )


async def create_email_request(registration_id: int) -> httpx.Response:
    """Send a post request to an endpoint for email creation."""
    logging.info("Creating email for registration ID: %s", registration_id)
    token = create_token(registration_id=registration_id)

    logging.info("Sending request to create email...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{get_settings().api_host}:{get_settings().api_port}/emailrequest/",
            headers={"Authorization": f"Bearer {token}"},
        )
    logging.info("Response status code: %s", response.status_code)
    logging.info("Response content: %s", response.json())
    return response.json()


async def recover_email_password_request(
    registration_id: int,
) -> httpx.Response:
    """Send a post request to an endpoint for email password recovery."""
    logging.info("Recovering email password for registration ID: %s", registration_id)
    token = create_token(registration_id=registration_id)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{get_settings().api_host}:{get_settings().api_port}/emailreset/",
            headers={"Authorization": f"Bearer {token}"},
        )
    logging.info("Response status code: %s", response.status_code)
    logging.info("Response content: %s", response.json())
    return response.json()


async def get_member_addresses_request(registration_id: int) -> httpx.Response:
    """Send a GET request to retrieve member addresses."""
    logging.info("Getting addresses for registration ID: %s", registration_id)
    token = create_token(registration_id=registration_id)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{get_settings().api_host}:{get_settings().api_port}/address/",
            headers={"Authorization": f"Bearer {token}"},
        )
    if response.json() == []:
        logging.info("No addresses registered for this member.")
        return httpx.Response(
            status_code=200, json={"message": "No addresses registered for this member."}
        )
    logging.info("Response status code: %s", response.status_code)
    logging.info("Response content: %s", response.json())
    return response.json()


async def update_address_request(
    registration_id: int, address_id: int, address: dict
) -> httpx.Response:
    """Send a PUT request to update member address."""
    logging.info("Updating address for registration ID: %s", registration_id)
    token = create_token(registration_id=registration_id)

    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{get_settings().api_host}:{get_settings().api_port}/address/{registration_id}/{address_id}",
            headers={"Authorization": f"Bearer {token}"},
            json=address,
        )
    logging.info("Response status code: %s", response.status_code)
    logging.info("Response content: %s", response.json())
    return response.json()

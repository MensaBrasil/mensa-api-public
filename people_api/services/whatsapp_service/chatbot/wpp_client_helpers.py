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


async def create_email_request(registration_id: int) -> dict:
    """Send a post request to an endpoint for email creation."""
    logging.info("[CHATBOT-MENSA] Creating email for registration ID: %s", registration_id)
    token = create_token(registration_id=registration_id)

    logging.info("[CHATBOT-MENSA] Sending request to create email...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://localhost:{get_settings().api_port}/emailrequest/",
            headers={"Authorization": f"Bearer {token}"},
        )
        logging.info("[CHATBOT-MENSA] Response status code: %s", response.status_code)
        logging.info("[CHATBOT-MENSA] Response content: %s", response.json())
        return response.json()


async def recover_email_password_request(
    registration_id: int,
) -> dict:
    """Send a post request to an endpoint for email password recovery."""
    logging.info(
        "[CHATBOT-MENSA] Recovering email password for registration ID: %s",
        registration_id,
    )
    token = create_token(registration_id=registration_id)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://localhost:{get_settings().api_port}/emailreset/",
            headers={"Authorization": f"Bearer {token}"},
        )
        logging.info("[CHATBOT-MENSA] Response status code: %s", response.status_code)
        logging.info("[CHATBOT-MENSA] Response content: %s", response.json())
        return response.json()


async def get_member_addresses_request(registration_id: int) -> dict:
    """Send a GET request to retrieve member addresses."""
    logging.info("[CHATBOT-MENSA] Getting addresses for registration ID: %s", registration_id)
    token = create_token(registration_id=registration_id)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:{get_settings().api_port}/address/",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = response.json()
        if data == []:
            logging.info("[CHATBOT-MENSA] No addresses registered for this member.")
            return {"message": "No addresses registered for this member."}
        logging.info("[CHATBOT-MENSA] Response status code: %s", response.status_code)
        logging.info("[CHATBOT-MENSA] Response content: %s", data)
        return data


async def update_address_request(registration_id: int, address_id: int, address: dict) -> dict:
    """Send a PUT request to update member address."""
    logging.info("[CHATBOT-MENSA] Updating address for registration ID: %s", registration_id)
    token = create_token(registration_id=registration_id)

    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"http://localhost:{get_settings().api_port}/address/{registration_id}/{address_id}",
            headers={"Authorization": f"Bearer {token}"},
            json=address,
        )
        logging.info("[CHATBOT-MENSA] Response status code: %s", response.status_code)
        logging.info("[CHATBOT-MENSA] Response content: %s", response.json())
        return response.json()


async def get_member_legal_reps(registration_id: int) -> dict:
    """Send a GET request to retrieve member legal representatives."""
    logging.info(
        "[CHATBOT-MENSA] Getting legal representatives for registration ID: %s",
        registration_id,
    )
    token = create_token(registration_id=registration_id)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:{get_settings().api_port}/legal_representative/",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = response.json()
        if not data or (isinstance(data, list) and len(data) == 0):
            logging.info("[CHATBOT-MENSA] No legal representatives registered for this member.")
            return {"message": "No legal representatives registered for this member."}
        logging.info("[CHATBOT-MENSA] Response status code: %s", response.status_code)
        logging.info("[CHATBOT-MENSA] Response content: %s", data)
        return data


async def add_member_legal_reps(registration_id: int, legal_representative: dict) -> dict:
    """Send a POST request to add a legal representative for a member."""
    logging.info(
        "[CHATBOT-MENSA] Adding legal representative for registration ID: %s",
        registration_id,
    )
    token = create_token(registration_id=registration_id)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://localhost:{get_settings().api_port}/legal_representative/{registration_id}",
            headers={"Authorization": f"Bearer {token}"},
            json=legal_representative,
        )
        logging.info("[CHATBOT-MENSA] Response status code: %s", response.status_code)
        logging.info("[CHATBOT-MENSA] Response content: %s", response.json())
        return response.json()


async def update_member_legal_reps(
    registration_id: int, legal_representative_id: int, legal_representative: dict
) -> dict:
    """Send a PUT request to update member legal representative."""
    logging.info(
        "[CHATBOT-MENSA] Updating legal representative for registration ID: %s",
        registration_id,
    )
    token = create_token(registration_id=registration_id)

    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"http://localhost:{get_settings().api_port}/legal_representative/{registration_id}/{legal_representative_id}",
            headers={"Authorization": f"Bearer {token}"},
            json=legal_representative,
        )
        logging.info("[CHATBOT-MENSA] Response status code: %s", response.status_code)
        logging.info("[CHATBOT-MENSA] Response content: %s", response.json())
        return response.json()


async def delete_member_legal_reps(registration_id: int, legal_representative_id: int) -> dict:
    """Send a DELETE request to remove a legal representative from a member."""
    logging.info(
        "[CHATBOT-MENSA] Deleting legal representative %s for registration ID: %s",
        legal_representative_id,
        registration_id,
    )
    token = create_token(registration_id=registration_id)

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"http://localhost:{get_settings().api_port}/legal_representative/{registration_id}/{legal_representative_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        logging.info("[CHATBOT-MENSA] Response status code: %s", response.status_code)
        logging.info("[CHATBOT-MENSA] Response content: %s", response.json())
        return response.json()


async def get_all_whatsapp_groups(registration_id: int) -> dict:
    """Send a GET request to retrieve all WhatsApp groups a member can join."""
    logging.info(
        "[CHATBOT-MENSA] Getting all WhatsApp groups for registration ID: %s",
        registration_id,
    )
    token = create_token(registration_id=registration_id)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:{get_settings().api_port}/get_can_participate",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = response.json()
        if not data or (isinstance(data, list) and len(data) == 0):
            logging.info("[CHATBOT-MENSA] No WhatsApp groups found.")
            return {"message": "No WhatsApp groups found."}
        logging.info("[CHATBOT-MENSA] Response status code: %s", response.status_code)
        logging.info("[CHATBOT-MENSA] Response content: %s", data)
        return data


async def request_whatsapp_group_join(registration_id: int, group_id: str) -> dict:
    """Send a POST request to request joining a WhatsApp group using GroupJoinRequest model."""
    logging.info(
        "[CHATBOT-MENSA] Requesting to join WhatsApp group %s for registration ID: %s",
        group_id,
        registration_id,
    )
    token = create_token(registration_id=registration_id)

    payload = {"group_id": group_id}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://localhost:{get_settings().api_port}/request_join_group",
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
        )
        logging.info("[CHATBOT-MENSA] Response status code: %s", response.status_code)
        logging.info("[CHATBOT-MENSA] Response content: %s", response.json())
        return response.json()


async def get_pending_whatsapp_group_join_requests(registration_id: int) -> dict:
    """Send a GET request to retrieve pending WhatsApp group join requests."""
    logging.info(
        "[CHATBOT-MENSA] Getting pending WhatsApp group join requests for registration ID: %s",
        registration_id,
    )
    token = create_token(registration_id=registration_id)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:{get_settings().api_port}/get_pending_requests",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = response.json()
        if not data or (isinstance(data, list) and len(data) == 0):
            logging.info("[CHATBOT-MENSA] No pending WhatsApp group join requests found.")
            return {"message": "No pending WhatsApp group join requests found."}
        logging.info("[CHATBOT-MENSA] Response status code: %s", response.status_code)
        logging.info("[CHATBOT-MENSA] Response content: %s", data)
        return data

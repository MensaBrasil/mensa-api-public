"""Validation service for WhatsApp messages."""

from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from people_api.database.models.models import Registration
from people_api.database.models.whatsapp import ReceivedWhatsappMessage
from people_api.services.membership_payment_service import MembershipPaymentService


async def validate_member_and_permissions(
    received_message: ReceivedWhatsappMessage, session: AsyncSession
) -> int:
    """Validate the member's existence and permissions."""

    registration = (
        await session.exec(
            Registration.get_registration_by_last_8_phone_digits(received_message.WaId)
        )
    ).first()

    if not registration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    payment = await MembershipPaymentService.get_last_payment(registration.registration_id, session)

    if (
        (payment is None)
        or (payment.expiration_date is None)
        or (payment.expiration_date < datetime.now().date())
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Member is not active")

    return registration.registration_id

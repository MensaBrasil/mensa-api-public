"""Whatsapp router for updating phone numbers for members and their legal representatives."""

from fastapi import APIRouter, Depends, Request

from people_api.services.whatsapp_service.chatbot.client import WhatsappChatBot

from ..database.models import UpdateInput
from ..database.models.whatsapp import ReceivedWhatsappMessage
from ..dbs import AsyncSessionsTuple, get_async_sessions
from ..services.whatsapp_service.chatbot.validation import (
    validate_member_and_permissions,
)
from ..services.whatsapp_service.utils import WhatsAppService

whatsapp_router = APIRouter(tags=["Whatsapp"], prefix="/whatsapp")


@whatsapp_router.post("/update-data")
async def update_data(
    update_input: UpdateInput,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """
    Whatsapp endpoint for updating phone numbers for members and their legal representatives.
    """
    return await WhatsAppService.update_data(update_input, session=sessions.rw)


@whatsapp_router.post("/chatbot-message")
async def chatbot_message(
    request: Request,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """
    Whatsapp endpoint for chatbot messages.
    """
    form_data = await request.form()
    data_dict = {key: str(value) for key, value in form_data.items()}
    received_message = ReceivedWhatsappMessage(**data_dict)

    registration_id = await validate_member_and_permissions(received_message, sessions.ro)

    return await WhatsappChatBot.chatbot_message(
        message=received_message, session=sessions.ro, registration_id=registration_id
    )

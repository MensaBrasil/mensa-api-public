"""Whatsapp router for updating phone numbers for members and their legal representatives."""

from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from ..database.models import UpdateInput
from ..database.models.whatsapp import ReceivedWhatsappMessage
from ..dbs import get_async_sessions, AsyncSessionsTuple
from ..services import WhatsappChatBot, WhatsAppService


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

    return await WhatsappChatBot.chatbot_message(received_message, session=sessions.rw)

"""Whatsapp router for updating phone numbers for members and their legal representatives."""

from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from ..database.models import UpdateInput
from ..database.models.whatsapp import ReceivedWhatsappMessage
from ..dbs import get_session
from ..services import WhatsappChatBot, WhatsAppService

whatsapp_router = APIRouter(tags=["Whatsapp"], prefix="/whatsapp")


@whatsapp_router.post("/update-data")
async def update_data(
    update_input: UpdateInput,
    session: Session = Depends(get_session),
):
    """
    Whatsapp endpoint for updating phone numbers for members and their legal representatives.
    phone number validation.
    """
    return WhatsAppService.update_data(update_input, session)


@whatsapp_router.post("/chatbot-message")
async def chatbot_message(
    request: Request,
    session: Session = Depends(get_session),
):
    """
    Whatsapp endpoint for chatbot messages.
    """
    form_data = await request.form()
    data_dict = {key: str(value) for key, value in form_data.items()}
    received_message = ReceivedWhatsappMessage(**data_dict)

    return WhatsappChatBot.chatbot_message(received_message, session)

"""Whatsapp router for updating phone numbers for members and their legal representatives."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database.models import UpdateInput
from ..dbs import get_session
from ..services import WhatsAppService

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

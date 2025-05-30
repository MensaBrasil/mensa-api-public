"""Service for sending WhatsApp messages using Twilio's API."""

import asyncio

from fastapi import HTTPException, Request, status
from twilio.request_validator import RequestValidator
from twilio.rest import Client

from ..settings import get_settings

SETTINGS = get_settings()


class TwilioService:
    """Service for sending WhatsApp messages using Twilio's API."""

    def __init__(self):
        self.account_sid = SETTINGS.twilio_account_sid
        self.auth_token = SETTINGS.twilio_auth_token
        self.from_whatsapp_number = SETTINGS.twilio_from_whatsapp_number

        self.client = Client(self.account_sid, self.auth_token)

    async def send_whatsapp_message(self, to_: str, message: str) -> None:
        """
        Asynchronously sends a WhatsApp message using Twilio's API.
        """
        from_ = self.from_whatsapp_number
        loop = asyncio.get_running_loop()

        await loop.run_in_executor(
            None,
            lambda: self.client.messages.create(
                body=message,
                from_=from_,
                to=to_,
            ),
        )

    @classmethod
    async def validate_twilio_request(cls, request: Request):
        """Validates the incoming request from Twilio."""
        validator = RequestValidator(get_settings().twilio_auth_token)
        signature = request.headers.get("X-Twilio-Signature", "")
        form = await request.form()
        form_dict = dict(form)

        scheme = request.headers.get("X-Forwarded-Proto", "http")
        host = request.headers.get("X-Forwarded-Host", request.headers.get("host", ""))
        url = f"{scheme}://{host}{request.url.path}"

        if not validator.validate(url, form_dict, signature):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Twilio signature."
            )

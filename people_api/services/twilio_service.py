"""Service for sending WhatsApp messages using Twilio's API."""

from twilio.rest import Client

import asyncio
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
            )
        )

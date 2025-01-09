"""Service for sending WhatsApp messages using Twilio's API."""

from twilio.rest import Client

from ..settings import TwilioSettings


class TwilioService:
    """Service for sending WhatsApp messages using Twilio's API."""

    def __init__(self):
        self.account_sid = TwilioSettings.account_sid
        self.auth_token = TwilioSettings.auth_token
        self.from_whatsapp_number = TwilioSettings.from_whatsapp_number

        self.client = Client(self.account_sid, self.auth_token)

    def send_whatsapp_message(self, to_: str, message: str) -> None:
        """
        Sends a WhatsApp message using Twilio's API.
            - to_number should be in format "whatsapp:..."
            - message is the text to send
        """
        from_ = self.from_whatsapp_number

        self.client.messages.create(
            body=message,
            from_=from_,
            to=to_,
        )

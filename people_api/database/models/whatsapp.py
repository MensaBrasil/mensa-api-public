"""WhatsApp model."""

from typing import Any

from pydantic import BaseModel, model_validator


class UpdateInput(BaseModel):
    phone: str
    birth_date: str | None = None
    cpf: str
    registration_id: int
    is_representative: bool
    token: str

    @model_validator(mode="before")
    @classmethod
    def check_birth_date_if_representative(cls, values: dict[str, Any]) -> dict[str, Any]:
        is_representative = values.get("is_representative")
        birth_date = values.get("birth_date")

        if not is_representative and birth_date is None:
            raise ValueError("Birth date cannot be None when is_representative is False")
        return values

    @model_validator(mode="before")
    @classmethod
    def convert_registration_id_to_int(cls, values: dict[str, Any]) -> dict[str, Any]:
        registration_id = values.get("registration_id")

        if isinstance(registration_id, str):
            try:
                values["registration_id"] = int(registration_id)

            except ValueError as exc:
                raise ValueError("registration_id must be convertible to an integer") from exc

        return values

    @model_validator(mode="before")
    @classmethod
    def validate_and_strip_whatsapp_prefix(cls, values: dict[str, Any]) -> dict[str, Any]:
        phone = values.get("phone")
        if phone and isinstance(phone, str):
            # Remove the 'whatsapp:' prefix
            values["phone"] = phone.replace("whatsapp:", "", 1)
        return values


class ReceivedWhatsappMessage(BaseModel):
    """Model for messages received from twilio"""

    SmsMessageSid: str
    NumMedia: str
    ProfileName: str
    MessageType: str
    SmsSid: str
    WaId: str
    SmsStatus: str
    Body: str
    To: str
    MessagingServiceSid: str
    NumSegments: str
    ReferralNumMedia: str
    MessageSid: str
    AccountSid: str
    From: str
    ApiVersion: str

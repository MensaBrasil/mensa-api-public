"""Email sending model for the People API."""

from pydantic import BaseModel, EmailStr


class BaseEmailContext(BaseModel):
    """Base placeholders for any email template."""

    recipient_name: str
    to_email: EmailStr
    subject: str

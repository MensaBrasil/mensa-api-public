"""Pending registration model for storing user data and token for verification."""

import uuid
from datetime import date
from typing import Literal

from pydantic import BaseModel, EmailStr
from pydantic_br import CPF
from sqlmodel import JSON, Column, Date, Field, select

from people_api.database.models.models import BaseSQLModel
from people_api.database.models.types import PhoneNumber, ZipNumber
from people_api.enums import Gender


class PendingRegistration(BaseSQLModel, table=True):
    """Model for pending registrations, including data and a unique token."""

    __tablename__ = "pending_registration"

    id: int = Field(primary_key=True)
    data: dict = Field(sa_column=Column(JSON))
    token: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True)
    email_sent_at: date | None = Field(
        sa_column=Column(Date, default=None, nullable=True, server_default=None)
    )

    @classmethod
    def get_select_stmt_by_token(cls, token: str):
        """Get a select statement to find a pending registration by its token."""

        return select(cls).where(cls.token == token)

    @classmethod
    def get_all_pending_registrations_with_no_email_sent(cls):
        """Get a select statement to retrieve all pending registrations."""

        return select(cls).where(cls.email_sent_at == None)  # noqa: E711


class LegalRepresentative(BaseModel):
    """Model for legal representatives of a pending registration."""

    name: str | None
    email: EmailStr | None = Field(max_length=255, min_length=5, index=True)
    phone_number: PhoneNumber | None = Field(max_length=60, min_length=9)


class Address(BaseModel):
    """Model for address details of a pending registration."""

    street: str
    neighborhood: str
    city: str
    state: str
    zip_code: ZipNumber
    country: str


class PendingRegistrationData(BaseModel):
    """Data model for pending registration, including personal and address details."""

    full_name: str
    social_name: str | None = None
    email: EmailStr = Field(max_length=255, min_length=5, index=True)
    birth_date: date
    cpf: CPF
    profession: str | None = None
    gender: Gender
    admission_type: Literal["test", "report"]
    phone_number: PhoneNumber = Field(max_length=60, min_length=9)
    address: Address
    legal_representatives: list[LegalRepresentative] | None = None


class PendingRegistrationMessage(BaseModel):
    """Message model for pending registration."""

    data: PendingRegistrationData
    token: str

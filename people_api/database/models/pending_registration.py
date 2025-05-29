"""Pending registration model for storing user data and token for verification."""

import uuid
from datetime import date

from pydantic import BaseModel, EmailStr
from sqlmodel import JSON, Column, Field

from people_api.database.models.models import BaseSQLModel
from people_api.database.models.types import CPFNumber, PhoneNumber, ZipNumber


class PendingRegistration(BaseSQLModel, table=True):
    """Model for pending registrations, including data and a unique token."""

    __tablename__ = "pending_registration"

    id: int = Field(primary_key=True)
    data: dict = Field(sa_column=Column(JSON))
    token: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True)


class LegalRepresentative(BaseModel):
    """Model for legal representatives of a pending registration."""

    name: str
    email: EmailStr = Field(max_length=255, min_length=5, index=True)
    phone_number: PhoneNumber = Field(max_length=60, min_length=9)


class Address(BaseModel):
    """Model for address details of a pending registration."""

    street: str
    neighborhood: str
    city: str
    state: str
    zip_code: ZipNumber | None = Field(None, max_length=12)


class PendingRegistrationData(BaseModel):
    """Data model for pending registration, including personal and address details."""

    full_name: str
    social_name: str | None = None
    email: EmailStr = Field(max_length=255, min_length=5, index=True)
    birth_date: date
    cpf: CPFNumber | None = Field(max_length=11, min_length=11)
    profession: str | None = None
    phone_number: PhoneNumber = Field(max_length=60, min_length=9)
    address: Address
    legal_representatives: list[LegalRepresentative] | None = None


class PendingRegistrationMessage(BaseModel):
    id: int
    data: PendingRegistrationData
    token: str

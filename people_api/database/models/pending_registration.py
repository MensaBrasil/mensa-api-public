"""Pending registration model for storing user data and token for verification."""

import uuid
from datetime import date

from pydantic import BaseModel, EmailStr, model_validator
from sqlmodel import JSON, Column, Date, Field, select

from people_api.database.models.models import BaseSQLModel
from people_api.database.models.types import CPFNumber, PhoneNumber, ZipNumber


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
    zip_code: ZipNumber | None = Field(None, max_length=12)
    country: str | None = Field(None)


class PendingRegistrationData(BaseModel):
    """Data model for pending registration, including personal and address details."""

    full_name: str
    social_name: str | None = None
    email: EmailStr = Field(max_length=255, min_length=5, index=True)
    birth_date: date
    cpf: CPFNumber | None
    profession: str | None = None
    gender: str | None = None
    phone_number: PhoneNumber = Field(max_length=60, min_length=9)
    address: Address
    legal_representatives: list[LegalRepresentative] | None = None

    @model_validator(mode="after")
    def validate_legal_representatives(self):
        """Set legal_representatives to [] if fields are empty or if age < 18."""

        today = date.today()
        age = (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )

        if age >= 18:
            self.legal_representatives = []
            return self

        if not self.legal_representatives:
            raise ValueError("Legal representatives are required for members under 18 years old")

        filtered_reps = []
        for rep in self.legal_representatives:
            if rep.name and rep.email and rep.phone_number:
                filtered_reps.append(rep)

        if not filtered_reps:
            raise ValueError(
                "At least one legal representative with complete information (name, email, phone) is required"
            )

        self.legal_representatives = filtered_reps
        return self


class PendingRegistrationMessage(BaseModel):
    """Message model for pending registration."""

    id: int
    data: PendingRegistrationData
    token: str

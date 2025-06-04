"""Utility helpers for member-related model conversions."""

from datetime import datetime

from people_api.database.models.models import (
    Addresses,
    Emails,
    LegalRepresentatives,
    Phones,
    Registration,
)
from people_api.database.models.pending_registration import PendingRegistrationData


def convert_pending_to_member_models(
    data: PendingRegistrationData,
    *,
    registration_id: int = 0,
):
    """Return initialized member-related models from pending registration data."""

    name_parts = data.full_name.strip().split()
    first_name = name_parts[0] if name_parts else None
    last_name = name_parts[-1] if len(name_parts) > 1 else None

    registration = Registration(
        name=data.full_name,
        social_name=data.social_name,
        birth_date=data.birth_date,
        cpf=data.cpf,
        expelled=False,
        deceased=False,
        transferred=False,
        profession=data.profession,
        first_name=first_name,
        last_name=last_name,
        gender=data.gender,
        join_date=datetime.now().date(),
    )

    address = Addresses(
        registration_id=registration_id,
        state=data.address.state,
        city=data.address.city,
        address=data.address.street,
        neighborhood=data.address.neighborhood,
        zip=data.address.zip_code,
        country=data.address.country,
    )

    email = Emails(
        registration_id=registration_id,
        email_type="primary",
        email_address=data.email,
    )

    phone = Phones(
        registration_id=registration_id,
        phone_number=data.phone_number,
    )

    reps = [
        LegalRepresentatives(
            registration_id=registration_id,
            full_name=rep.name,
            email=rep.email,
            phone=rep.phone_number,
        )
        for rep in data.legal_representatives or []
    ]

    return registration, address, email, phone, reps

# mypy: ignore-errors

"""MODELS - PERSON ADDRESS
The address of a person is part of the Person model
"""

# # Package # #
from datetime import date, datetime

from .common import BaseModel
from .fields import (
    AddressFields,
    EmailFields,
    LegalRepresentativeFields,
    PhoneFields,
    PostgresMemberFields,
)

__all__ = (
    "Address",
    "Phone",
    "Email",
    "PostgresMemberRegistration",
    "LegalRepresentative",
    "AddressCreate",
    "PhoneCreate",
    "EmailCreate",
    "LegalRepresentativeCreate",
    "AddressUpdate",
    "PhoneUpdate",
    "EmailUpdate",
    "LegalRepresentativeUpdate",
    "MemberProfessionFacebookUpdate",
    "MissingFieldsCreate",
)


class PostgresMemberRegistration(BaseModel):
    """Body of Member PATCH requests"""

    registration_id: int = PostgresMemberFields.registration_id
    name: str | None = PostgresMemberFields.name
    social_name: str | None = PostgresMemberFields.social_name
    first_name: str | None = PostgresMemberFields.first_name
    last_name: str | None = PostgresMemberFields.last_name
    birth_date: date | None = PostgresMemberFields.birth_date
    cpf: str | None = PostgresMemberFields.cpf
    profession: str | None = PostgresMemberFields.profession
    gender: str | None = PostgresMemberFields.gender
    join_date: date = PostgresMemberFields.join_date
    facebook: str | None = PostgresMemberFields.facebook
    expelled: bool = PostgresMemberFields.expelled
    suspended_until: date | None = PostgresMemberFields.suspended_until
    deceased: bool = PostgresMemberFields.deceased
    transferred: bool = PostgresMemberFields.transferred
    created_at: datetime = PostgresMemberFields.created_at
    updated_at: datetime | None = PostgresMemberFields.updated_at
    pronouns: str | None = PostgresMemberFields.pronouns


class Address(BaseModel):
    address_id: int = AddressFields.address_id
    registration_id: int = AddressFields.registration_id
    country: str | None = AddressFields.country
    state: str | None = AddressFields.state
    city: str | None = AddressFields.city
    country: str | None = AddressFields.country
    address: str | None = AddressFields.address
    latlong: str | None = AddressFields.latlong
    neighborhood: str | None = AddressFields.neighborhood
    zip: str | None = AddressFields.zip
    created_at: datetime = AddressFields.created_at
    updated_at: datetime = AddressFields.updated_at


class Phone(BaseModel):
    phone_id: int = PhoneFields.phone_id
    registration_id: int = PhoneFields.registration_id
    phone_number: str | None = PhoneFields.phone_number
    created_at: datetime = PhoneFields.created_at
    updated_at: datetime = PhoneFields.updated_at


class Email(BaseModel):
    email_id: int = EmailFields.email_id
    registration_id: int = EmailFields.registration_id
    email_type: str | None = EmailFields.email_type
    email_address: str | None = EmailFields.email_address
    created_at: datetime = EmailFields.created_at
    updated_at: datetime = EmailFields.updated_at


class LegalRepresentative(BaseModel):
    representative_id: int = LegalRepresentativeFields.representative_id
    registration_id: int = LegalRepresentativeFields.registration_id
    cpf: str | None = LegalRepresentativeFields.cpf
    full_name: str | None = LegalRepresentativeFields.full_name
    email: str | None = LegalRepresentativeFields.email
    phone: str | None = LegalRepresentativeFields.phone
    alternative_phone: str | None = LegalRepresentativeFields.alternative_phone
    observations: str | None = LegalRepresentativeFields.observations


class AddressCreate(BaseModel):
    state: str = AddressFields.state
    city: str = AddressFields.city
    country: str = AddressFields.country
    latlong: str = AddressFields.latlong
    address: str = AddressFields.address
    neighborhood: str = AddressFields.neighborhood
    zip: str = AddressFields.zip


class PhoneCreate(BaseModel):
    phone_number: str = PhoneFields.phone_number


class EmailCreate(BaseModel):
    email_type: str = EmailFields.email_type
    email_address: str = EmailFields.email_address


class LegalRepresentativeCreate(BaseModel):
    cpf: str | None = LegalRepresentativeFields.cpf
    full_name: str = LegalRepresentativeFields.full_name
    email: str | None = LegalRepresentativeFields.email
    phone: str | None = LegalRepresentativeFields.phone
    alternative_phone: str | None = LegalRepresentativeFields.alternative_phone
    observations: str | None = LegalRepresentativeFields.observations


class AddressUpdate(BaseModel):
    state: str | None = AddressFields.state
    city: str | None = AddressFields.city
    country: str | None = AddressFields.country
    latlong: str | None = AddressFields.latlong
    address: str | None = AddressFields.address
    neighborhood: str | None = AddressFields.neighborhood
    zip: str | None = AddressFields.zip


class PhoneUpdate(BaseModel):
    phone_number: str | None = PhoneFields.phone_number


class EmailUpdate(BaseModel):
    email_type: str | None = EmailFields.email_type
    email_address: str | None = EmailFields.email_address


class LegalRepresentativeUpdate(BaseModel):
    cpf: str | None = LegalRepresentativeFields.cpf
    full_name: str | None = LegalRepresentativeFields.full_name
    email: str | None = LegalRepresentativeFields.email
    phone: str | None = LegalRepresentativeFields.phone
    alternative_phone: str | None = LegalRepresentativeFields.alternative_phone
    observations: str | None = LegalRepresentativeFields.observations


# model to update profession and facebook url
class MemberProfessionFacebookUpdate(BaseModel):
    profession: str | None = PostgresMemberFields.profession
    facebook: str | None = PostgresMemberFields.facebook


class MissingFieldsCreate(BaseModel):
    cpf: str | None = PostgresMemberFields.cpf
    birth_date: str | None = PostgresMemberFields.birth_date

"""MODELS - PERSON ADDRESS
The address of a person is part of the Person model
"""

# # Package # #
from .common import BaseModel
from .fields import AddressFields, PhoneFields, EmailFields, PostgresMemberFields, LegalRepresentativeFields
from typing import Optional
from datetime import date, datetime

__all__ = ("Address","Phone", "Email", "PostgresMemberRegistration", "LegalRepresentative", "AddressCreate", "PhoneCreate", "EmailCreate", "LegalRepresentativeCreate", "AddressUpdate", "PhoneUpdate", "EmailUpdate", "LegalRepresentativeUpdate", "MemberProfessionFacebookUpdate", "MissingFieldsCreate")

class PostgresMemberRegistration(BaseModel):
    """Body of Member PATCH requests"""

    registration_id: int = PostgresMemberFields.registration_id
    name: Optional[str] = PostgresMemberFields.name
    social_name: Optional[str] = PostgresMemberFields.social_name
    first_name: Optional[str] = PostgresMemberFields.first_name
    last_name: Optional[str] = PostgresMemberFields.last_name
    birth_date: Optional[date] = PostgresMemberFields.birth_date
    cpf: Optional[str] = PostgresMemberFields.cpf
    profession: Optional[str] = PostgresMemberFields.profession
    gender: Optional[str] = PostgresMemberFields.gender
    join_date: date = PostgresMemberFields.join_date
    facebook: Optional[str] = PostgresMemberFields.facebook
    expelled: bool = PostgresMemberFields.expelled
    suspended_until: Optional[date] = PostgresMemberFields.suspended_until
    deceased: bool = PostgresMemberFields.deceased
    transferred: bool = PostgresMemberFields.transferred
    created_at: datetime = PostgresMemberFields.created_at
    updated_at: Optional[datetime] = PostgresMemberFields.updated_at
    pronouns: Optional[str] = PostgresMemberFields.pronouns

class Address(BaseModel):
    address_id: int = AddressFields.address_id
    registration_id: int = AddressFields.registration_id
    country: Optional[str] = AddressFields.country
    state: Optional[str] = AddressFields.state
    city: Optional[str] = AddressFields.city
    country: Optional[str] = AddressFields.country
    address: Optional[str] = AddressFields.address
    latlong: Optional[str] = AddressFields.latlong
    neighborhood: Optional[str] = AddressFields.neighborhood
    zip: Optional[str] = AddressFields.zip
    created_at: datetime = AddressFields.created_at
    updated_at: datetime = AddressFields.updated_at

class Phone(BaseModel):
    phone_id: int = PhoneFields.phone_id
    registration_id: int = PhoneFields.registration_id
    phone_number: Optional[str] = PhoneFields.phone_number
    created_at: datetime = PhoneFields.created_at
    updated_at: datetime = PhoneFields.updated_at

class Email(BaseModel):
    email_id: int = EmailFields.email_id
    registration_id: int = EmailFields.registration_id
    email_type: Optional[str] = EmailFields.email_type
    email_address: Optional[str] = EmailFields.email_address
    created_at: datetime = EmailFields.created_at
    updated_at: datetime = EmailFields.updated_at

class LegalRepresentative(BaseModel):
    representative_id: int = LegalRepresentativeFields.representative_id
    registration_id: int = LegalRepresentativeFields.registration_id
    cpf: Optional[str] = LegalRepresentativeFields.cpf
    full_name: Optional[str] = LegalRepresentativeFields.full_name
    email: Optional[str] = LegalRepresentativeFields.email
    phone: Optional[str] = LegalRepresentativeFields.phone
    alternative_phone: Optional[str] = LegalRepresentativeFields.alternative_phone
    observations: Optional[str] = LegalRepresentativeFields.observations

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
    cpf: Optional[str] = LegalRepresentativeFields.cpf
    full_name: str = LegalRepresentativeFields.full_name
    email: Optional[str] = LegalRepresentativeFields.email
    phone: Optional[str] = LegalRepresentativeFields.phone
    alternative_phone: Optional[str] = LegalRepresentativeFields.alternative_phone
    observations: Optional[str] = LegalRepresentativeFields.observations

class AddressUpdate(BaseModel):
    state: Optional[str] = AddressFields.state
    city: Optional[str] = AddressFields.city
    country: Optional[str] = AddressFields.country
    latlong: Optional[str] = AddressFields.latlong
    address: Optional[str] = AddressFields.address
    neighborhood: Optional[str] = AddressFields.neighborhood
    zip: Optional[str] = AddressFields.zip

class PhoneUpdate(BaseModel):
    phone_number: Optional[str] = PhoneFields.phone_number

class EmailUpdate(BaseModel):
    email_type: Optional[str] = EmailFields.email_type
    email_address: Optional[str] = EmailFields.email_address

class LegalRepresentativeUpdate(BaseModel):
    cpf: Optional[str] = LegalRepresentativeFields.cpf
    full_name: Optional[str] = LegalRepresentativeFields.full_name
    email: Optional[str] = LegalRepresentativeFields.email
    phone: Optional[str] = LegalRepresentativeFields.phone
    alternative_phone: Optional[str] = LegalRepresentativeFields.alternative_phone
    observations: Optional[str] = LegalRepresentativeFields.observations


#model to update profession and facebook url
class MemberProfessionFacebookUpdate(BaseModel):
    profession: Optional[str] = PostgresMemberFields.profession
    facebook: Optional[str] = PostgresMemberFields.facebook

class MissingFieldsCreate(BaseModel):
    cpf : Optional[str] = PostgresMemberFields.cpf
    birth_date : Optional[date] = PostgresMemberFields.birth_date
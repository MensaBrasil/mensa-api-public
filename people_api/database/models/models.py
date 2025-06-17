#   - This file contains the SQLModel classes for the database tables.
"""
SQLmodels

This module defines SQLModel classes for various entities used in the application. Each class corresponds
to a table in the database and represents a distinct entity with relevant fields and relationships.

These models are built with SQLAlchemy and SQLModel, allowing for clear schema definitions and relational mappings.
"""

from datetime import date, datetime

from pydantic import condecimal
from sqlmodel import (
    JSON,
    CheckConstraint,
    Column,
    Field,
    Relationship,
    SQLModel,
    UniqueConstraint,
)


class AddressesAudit(SQLModel, table=True):
    """Audit log for address changes, recording operations on address records."""

    audit_id: int | None = Field(default=None, primary_key=True)
    address_id: int = Field(default=None)
    operation: str = Field(max_length=10)
    operation_timestamp: datetime | None = Field(default_factory=datetime.utcnow)
    old_data: dict | None = Field(default=None, sa_column=Column(JSON))
    new_data: dict | None = Field(default=None, sa_column=Column(JSON))


class CadastroNaouse(SQLModel, table=True):
    """Model representing registration details with various personal and contact information."""

    N_DE_CADASTRO: str = Field(primary_key=True)
    SITUACAO: str | None = None
    STATUS: str | None = None
    NOME: str | None = None
    NOME_SOCIAL: str | None = None
    PRIMEIRO_NOME: str | None = None
    ULTIMO_NOME: str | None = None
    VENCIMENTO: str | None = None
    ULTIMO_PAGTO: str | None = None
    PAGAMENTO: str | None = None
    RESPONSAVEL_LEGAL: str | None = None
    IDADE: str | None = None
    EMAIL_PRINCIPAL: str | None = None
    EMAIL_RESPONSAVEL_JB: str | None = None
    EMAIL_ALTERNATIVO: str | None = None
    EMAIL_MENSA: str | None = None
    MI: str | None = None
    TIPO: str | None = None
    UF: str | None = None
    CIDADE: str | None = None
    ENDERECO: str | None = None
    BAIRRO: str | None = None
    CEP: str | None = None
    DATA_DE_NASCIMENTO: str | None = None
    CPF: str | None = None
    PROFISSAO: str | None = None
    SEXO: str | None = None
    TELEFONE_1: str | None = None
    TELEFONE_2: str | None = None
    TELEFONE_3: str | None = None
    TELEFONE_4: str | None = None
    DATA_INGRESSO: str | None = None
    FACEBOOK: str | None = None
    IDADE_AO_ENTRAR: str | None = None


class EmailsAudit(SQLModel, table=True):
    """Audit log for email changes, recording operations on email records."""

    audit_id: int | None = Field(default=None, primary_key=True)
    email_id: int
    operation: str = Field(max_length=10)
    operation_timestamp: datetime | None = Field(default_factory=datetime.utcnow)
    old_data: dict | None = Field(default=None, sa_column=Column(JSON))
    new_data: dict | None = Field(default=None, sa_column=Column(JSON))


class GroupRequests(SQLModel, table=True):
    """Model representing requests to join a group, including metadata such as phone and attempt count."""

    id: int | None = Field(default=None, primary_key=True)
    registration_id: int
    group_id: str
    created_at: datetime
    no_of_attempts: int = Field(default=0)
    phone_number: str
    last_attempt: datetime | None = None
    fulfilled: bool | None = None


class MembershipPaymentsAudit(SQLModel, table=True):
    """Audit log for membership payment changes, tracking changes to payment records."""

    audit_id: int | None = Field(default=None, primary_key=True)
    payment_id: int
    operation: str = Field(max_length=10)
    operation_timestamp: datetime | None = Field(default_factory=datetime.utcnow)
    old_data: dict | None = Field(default=None, sa_column=Column(JSON))
    new_data: dict | None = Field(default=None, sa_column=Column(JSON))


class PhonesAudit(SQLModel, table=True):
    """Audit log for phone record changes, capturing details of modifications."""

    audit_id: int | None = Field(default=None, primary_key=True)
    phone_id: int
    operation: str = Field(max_length=10)
    operation_timestamp: datetime | None = Field(default_factory=datetime.utcnow)
    old_data: dict | None = Field(default=None, sa_column=Column(JSON))
    new_data: dict | None = Field(default=None, sa_column=Column(JSON))


class Registration(SQLModel, table=True):
    """Model for user registration, including personal, social, and contact information."""

    __table_args__ = (
        CheckConstraint("(length((cpf)::text) = 11) OR (cpf IS NULL) OR ((cpf)::text = ''::text)"),
    )

    registration_id: int | None = Field(default=None, primary_key=True)
    expelled: bool = Field(default=False)
    deceased: bool = Field(default=False)
    transferred: bool = Field(default=False)
    name: str | None = None
    social_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    cpf: str | None = Field(max_length=11)
    profession: str | None = None
    gender: str | None = None
    join_date: date = Field(default_factory=date.today)
    facebook: str | None = None
    suspended_until: date | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None
    pronouns: str | None = None

    addresses: list["Addresses"] = Relationship(back_populates="registration")
    certs_antec_criminais: list["CertsAntecCriminais"] = Relationship(back_populates="registration")
    emails: list["Emails"] = Relationship(back_populates="registration")
    legal_representatives: list["LegalRepresentatives"] = Relationship(
        back_populates="registration"
    )
    member_groups: list["MemberGroups"] = Relationship(back_populates="registration")
    membership_payments: list["MembershipPayments"] = Relationship(back_populates="registration")
    phones: list["Phones"] = Relationship(back_populates="registration")


class RegistrationAudit(SQLModel, table=True):
    """Audit log for registration changes, logging details of updates to user registration records."""

    audit_id: int | None = Field(default=None, primary_key=True)
    registration_id: int
    operation: str = Field(max_length=10)
    operation_timestamp: datetime | None = Field(default_factory=datetime.utcnow)
    old_data: dict | None = Field(default=None, sa_column=Column(JSON))
    new_data: dict | None = Field(default=None, sa_column=Column(JSON))


class Addresses(SQLModel, table=True):
    """Model for address information related to user registrations."""

    address_id: int | None = Field(default=None, primary_key=True)
    registration_id: int = Field(foreign_key="registration.registration_id")
    state: str | None = None
    city: str | None = Field(max_length=100)
    address: str | None = Field(max_length=255)
    neighborhood: str | None = Field(max_length=100)
    zip: str | None = Field(max_length=40)
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = Field(default_factory=datetime.utcnow)
    country: str | None = None
    latlong: str | None = None

    registration: "Registration" = Relationship(back_populates="addresses")


class CertsAntecCriminais(SQLModel, table=True):
    """Model for storing criminal record certificates associated with user registrations."""

    id: int | None = Field(default=None, primary_key=True)
    registration_id: int = Field(foreign_key="registration.registration_id")
    expiration_date: date | None = None
    verified: bool | None = None
    url: str | None = None

    registration: "Registration" = Relationship(back_populates="certs_antec_criminais")


class Emails(SQLModel, table=True):
    """Model for storing email information linked to user registrations."""

    email_id: int | None = Field(default=None, primary_key=True)
    registration_id: int = Field(foreign_key="registration.registration_id")
    email_type: str | None = Field(max_length=50)
    email_address: str | None = Field(max_length=255, index=True)
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = Field(default_factory=datetime.utcnow)

    registration: "Registration" = Relationship(back_populates="emails")


class LegalRepresentatives(SQLModel, table=True):
    """Model for legal representatives associated with a user registration."""

    __table_args__ = (
        CheckConstraint("(length((cpf)::text) = 11) OR (cpf IS NULL) OR ((cpf)::text = ''::text)"),
    )

    representative_id: int | None = Field(default=None, primary_key=True)
    registration_id: int = Field(foreign_key="registration.registration_id")
    cpf: str | None = Field(max_length=11)
    full_name: str | None = Field(max_length=255)
    email: str | None = Field(max_length=255)
    phone: str | None = Field(max_length=15)
    alternative_phone: str | None = Field(max_length=15)
    observations: str | None = None

    registration: "Registration" = Relationship(back_populates="legal_representatives")


class MemberGroups(SQLModel, table=True):
    """Model representing group memberships for members, including entry and exit data."""

    __table_args__ = (UniqueConstraint("phone_number", "group_id", "entry_date"),)
    id: int | None = Field(default=None, primary_key=True)
    phone_number: str = Field(max_length=20)
    group_id: str = Field(max_length=255)
    entry_date: date = Field(default_factory=date.today)
    status: str = Field(max_length=50)
    registration_id: int | None = Field(foreign_key="registration.registration_id")
    exit_date: date | None = None
    removal_reason: str | None = None

    registration: "Registration" = Relationship(back_populates="member_groups")


class MembershipPayments(SQLModel, table=True):
    """Model for recording payment information related to membership dues."""

    payment_id: int | None = Field(default=None, primary_key=True)
    registration_id: int = Field(foreign_key="registration.registration_id")
    payment_date: date | None = Field(default_factory=date.today)
    expiration_date: date | None = None
    amount_paid: condecimal(max_digits=10, decimal_places=2) | None = None
    observation: str | None = None
    payment_method: str | None = None
    transaction_id: str | None = None
    payment_status: str | None = None
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None

    registration: Registration | None = Relationship(back_populates="membership_payments")


class Phones(SQLModel, table=True):
    """Model for phone numbers associated with user registrations."""

    phone_id: int | None = Field(default=None, primary_key=True)
    registration_id: int = Field(foreign_key="registration.registration_id")
    phone_number: str | None = Field(max_length=60)
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = Field(default_factory=datetime.utcnow)

    registration: Registration | None = Relationship(back_populates="phones")

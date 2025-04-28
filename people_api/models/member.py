# mypy: ignore-errors

"""MODELS - PERSON - UPDATE
Person Update model. All attributes are set as Optional, as we use the PATCH method for update
(in which only the attributes to change are sent on request body)
"""

# # Native # #
from datetime import date

# # Package # #
from .common import BaseModel
from .fields import FirebaseMemberFields
from .member_data import (
    Address,
    Email,
    LegalRepresentative,
    Phone,
    PostgresMemberRegistration,
)

__all__ = (
    "FirebaseMemberRead",
    "PostgresMemberRead",
    "GroupJoinRequest",
    "PronounsCreate",
)


class FirebaseMemberRead(BaseModel):
    """Body of Member PATCH requests"""

    AWalletAuthenticationToken: str | None = FirebaseMemberFields.AWalletAuthenticationToken
    CertificateToken: str | None = FirebaseMemberFields.CertificateToken
    MB: int = FirebaseMemberFields.MB
    birthdate: date | None = FirebaseMemberFields.birthdate
    display_name: str | None = FirebaseMemberFields.display_name
    email: str | None = FirebaseMemberFields.email
    expiration_date: date | None = FirebaseMemberFields.expiration_date
    fcm_token: list | None = None
    member_status: str | None = FirebaseMemberFields.member_status
    profile: str | None = FirebaseMemberFields.profile
    updated_at: date | None = FirebaseMemberFields.updated_at


class PostgresMemberRead(BaseModel):
    """Body of Member GET requests"""

    member: PostgresMemberRegistration = None
    addresses: list[Address] | None = None
    phones: list[Phone] | None = None
    emails: list[Email] | None = None
    legal_representatives: list[LegalRepresentative] | None = None


class GroupJoinRequest(BaseModel):
    group_id: str


class PronounsCreate(BaseModel):
    pronouns: str

"""MODELS - PERSON - UPDATE
Person Update model. All attributes are set as Optional, as we use the PATCH method for update
(in which only the attributes to change are sent on request body)
"""

# # Native # #
from datetime import date
from typing import List, Optional

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

__all__ = ("FirebaseMemberRead", "PostgresMemberRead", "GroupJoinRequest", "PronounsCreate")


class FirebaseMemberRead(BaseModel):
    """Body of Member PATCH requests"""

    AWalletAuthenticationToken: Optional[str] = FirebaseMemberFields.AWalletAuthenticationToken
    CertificateToken: Optional[str] = FirebaseMemberFields.CertificateToken
    MB: int = FirebaseMemberFields.MB
    birthdate: Optional[date] = FirebaseMemberFields.birthdate
    display_name: Optional[str] = FirebaseMemberFields.display_name
    email: Optional[str] = FirebaseMemberFields.email
    expiration_date: Optional[date] = FirebaseMemberFields.expiration_date
    fcm_token: Optional[list] = None
    member_status: Optional[str] = FirebaseMemberFields.member_status
    profile: Optional[str] = FirebaseMemberFields.profile
    updated_at: Optional[date] = FirebaseMemberFields.updated_at


class PostgresMemberRead(BaseModel):
    """Body of Member GET requests"""

    member: PostgresMemberRegistration = None
    addresses: Optional[List[Address]] = None
    phones: Optional[List[Phone]] = None
    emails: Optional[List[Email]] = None
    legal_representatives: Optional[List[LegalRepresentative]] = None


class GroupJoinRequest(BaseModel):
    group_id: str


class PronounsCreate(BaseModel):
    pronouns: str

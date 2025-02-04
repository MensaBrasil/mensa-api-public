# mypy: ignore-errors


"""MODELS - FIELDS
Definition of Fields used on model classes attributes.
We define them separately because the PersonUpdate and PersonCreate models need to re-define their attributes,
as they change from Optional to required.
Address could define its fields on the model itself, but we define them here for convenience
"""

# # Installed # #
from pydantic import Field

# # Package # #
from ..utils import get_time, get_uuid

__all__ = (
    "PersonFields",
    "AddressFields",
    "PhoneFields",
    "EmailFields",
    "LegalRepresentativeFields",
)

_string = dict(min_length=1)
"""Common attributes for all String fields"""
_unix_ts = dict(example=get_time())
"""Common attributes for all Unix timestamp fields"""


class FirebaseMemberFields:
    AWalletAuthenticationToken = Field(
        description="Apple Wallet Auth token",
    )
    CertificateToken = Field(
        description="Certificate token",
    )
    MB = Field(
        description="MB",
    )
    birthdate = Field(
        description="Birthdate",
    )
    display_name = Field(
        description="Display name",
    )
    email = Field(
        description="Email",
    )
    expiration_date = Field(
        description="Expiration date",
    )
    member_status = Field(
        description="Member status",
    )
    profile = Field(
        description="Profile",
    )
    updated_at = Field(
        description="Updated at",
    )
    fcm_token = Field(
        description="FCM token",
    )


class PostgresMemberFields:
    registration_id = Field(..., description="Unique identifier for the registration")
    name = Field(None, description="Full name of the member", max_length=255)
    social_name = Field(None, description="Social name of the member", max_length=255)
    first_name = Field(None, description="First name of the member", max_length=255)
    last_name = Field(None, description="Last name of the member", max_length=255)
    birth_date = Field(None, description="Date of birth of the member")
    cpf = Field(None, description="CPF of the member", min_length=0, max_length=11)
    profession = Field(None, description="Profession of the member", max_length=255)
    gender = Field(None, description="Gender of the member", max_length=50)
    join_date = Field(..., description="Date when the member joined")
    facebook = Field(None, description="Facebook profile of the member", max_length=255)
    expelled = Field(False, description="Whether the member was expelled")
    suspended_until = Field(None, description="Date until which the member is suspended")
    deceased = Field(False, description="Whether the member is deceased")
    transferred = Field(False, description="Whether the member was transferred")
    created_at = Field(..., description="Timestamp when the registration was created")
    updated_at = Field(None, description="Timestamp when the registration was last updated")
    pronouns = Field(None, description="Pronouns of the member", max_length=255)


class PersonFields:
    name = Field(description="Full name of this person", example="John Smith", **_string)
    address = Field(description="Address object where this person live")
    address_update = Field(
        description=f"{address.description}. When updating, the whole Address object is required, as it gets replaced"
    )
    birth = Field(
        description="Date of birth, in format YYYY-MM-DD, or Unix timestamp", example="1999-12-31"
    )
    age = Field(description="Age of this person, if date of birth is specified", example=20)
    person_id = Field(
        description="Unique identifier of this person in the database",
        example=get_uuid(),
        min_length=36,
        max_length=36,
    )
    """The person_id is the _id field of Mongo documents, and is set on PeopleRepository.create"""

    created = Field(
        alias="created", description="When the person was registered (Unix timestamp)", **_unix_ts
    )
    """Created is set on PeopleRepository.create"""
    updated = Field(
        alias="updated",
        description="When the person was updated for the last time (Unix timestamp)",
        **_unix_ts,
    )
    """Created is set on PeopleRepository.update (and initially on create)"""


class AddressFields:
    address_id = Field(description="Unique identifier for the address")
    registration_id = Field(
        description="Foreign key referencing registration_id in registration table"
    )
    state = Field(description="State", max_length=255)
    country = Field(description="Country", max_length=255)
    city = Field(description="City", max_length=100)
    latlong = Field(description="Latitude and longitude", max_length=100)
    address = Field(description="Address", max_length=255)
    neighborhood = Field(description="Neighborhood", max_length=100)
    zip = Field(description="ZIP code", max_length=40)
    created_at = Field(description="Timestamp when the address was created")
    updated_at = Field(description="Timestamp when the address was last updated")


class PhoneFields:
    phone_id = Field(description="Unique identifier for the phone")
    registration_id = Field(description="Foreign key to the registration table")
    phone_number = Field(description="Phone number of the member", max_length=60)
    created_at = Field(description="Timestamp when the phone was added")
    updated_at = Field(description="Timestamp when the phone was last updated")


class EmailFields:
    email_id = Field(description="Unique identifier for the email")
    registration_id = Field(description="Reference to the related registration")
    email_type = Field(None, description="Type of the email", max_length=50)
    email_address = Field(None, description="Email address", max_length=255)
    created_at = Field(description="Timestamp when the email was added")
    updated_at = Field(description="Timestamp when the email was last updated")


class LegalRepresentativeFields:
    representative_id = Field(description="Unique identifier for the legal representative")
    registration_id = Field(description="Reference to the associated registration")
    cpf = Field(None, description="CPF of the legal representative", max_length=11)
    full_name = Field(None, description="Full name of the legal representative", max_length=255)
    email = Field(None, description="Email address of the legal representative", max_length=255)
    phone = Field(None, description="Phone number of the legal representative", max_length=15)
    alternative_phone = Field(
        None, description="Alternative phone number of the legal representative", max_length=15
    )
    observations = Field(None, description="Additional observations")

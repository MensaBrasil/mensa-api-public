"""
SQLmodels
"""

from datetime import date, datetime, timezone

from pydantic import condecimal
from sqlmodel import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Field,
    ForeignKey,
    Integer,
    Relationship,
    Session,
    SQLModel,
    String,
    Text,
    UniqueConstraint,
    func,
    select,
    text,
)


class BaseSQLModel(SQLModel):
    """Base class for SQLModel classes, providing common fields and methods."""

    created_at: datetime | None = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(default_factory=lambda: datetime.now(timezone.utc))


class BaseAuditModel(BaseSQLModel):
    """Base class for audit log models, providing common fields and methods."""

    audit_id: int | None = Field(default=None, primary_key=True)
    operation: str = Field(max_length=10)
    operation_timestamp: datetime | None = Field(default_factory=lambda: datetime.now(timezone.utc))


class AddressesAudit(BaseAuditModel, table=True):
    """Audit log for address changes, recording operations on address records."""

    __tablename__ = "addresses_audit"

    address_id: int = Field(default=None)
    old_data: dict | None = Field(default=None, sa_column=Column(JSON))
    new_data: dict | None = Field(default=None, sa_column=Column(JSON))


class EmailsAudit(BaseAuditModel, table=True):
    """Audit log for email changes, recording operations on email records."""

    __tablename__ = "emails_audit"

    email_id: int
    old_data: dict | None = Field(default=None, sa_column=Column(JSON))
    new_data: dict | None = Field(default=None, sa_column=Column(JSON))


class GroupRequests(BaseSQLModel, table=True):
    """Model representing requests to join a group, including metadata such as phone and attempt count."""

    __tablename__ = "group_requests"

    id: int | None = Field(default=None, primary_key=True)
    registration_id: int
    group_id: str
    no_of_attempts: int | None = Field(sa_column=Column(Integer, server_default=text("0")))
    last_attempt: datetime | None = None
    fulfilled: bool | None = None


class MembershipPaymentsAudit(BaseAuditModel, table=True):
    """Audit log for membership payment changes, tracking changes to payment records."""

    __tablename__ = "membership_payments_audit"

    payment_id: int
    old_data: dict | None = Field(default=None, sa_column=Column(JSON))
    new_data: dict | None = Field(default=None, sa_column=Column(JSON))


class PhonesAudit(BaseAuditModel, table=True):
    """Audit log for phone record changes, capturing details of modifications."""

    __tablename__ = "phones_audit"

    phone_id: int
    old_data: dict | None = Field(default=None, sa_column=Column(JSON))
    new_data: dict | None = Field(default=None, sa_column=Column(JSON))


class Registration(BaseSQLModel, table=True):
    """Model for user registration, including personal, social, and contact information."""

    __tablename__ = "registration"
    __table_args__ = (
        CheckConstraint(
            "(length((cpf)::text) = 11) OR (cpf IS NULL) OR ((cpf)::text = ''::text)",
            name="check_cpf_length",
        ),
    )

    registration_id: int | None = Field(default=None, primary_key=True)
    expelled: bool = Field(sa_column=Column(Boolean, server_default=text("false")))
    deceased: bool = Field(sa_column=Column(Boolean, server_default=text("false")))
    transferred: bool = Field(sa_column=Column(Boolean, server_default=text("false")))
    name: str | None = None
    social_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    cpf: str | None = Field(max_length=11, min_length=11)
    profession: str | None = None
    gender: str | None = None
    join_date: date | None = Field(default_factory=date.today)
    facebook: str | None = None
    discord_id: str | None = None
    suspended_until: date | None = None
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

    @classmethod
    def select_stmt(cls, registration_id: int, session: Session) -> "Registration":
        """Return a registration record by ID."""
        statement = select(cls).where(cls.registration_id == registration_id)
        results = session.exec(statement)
        if not results:
            raise ValueError(f"Registration ID {registration_id} not found")
        return results.first()

    @classmethod
    def get_first_name(cls, registration_id: int, session: Session) -> str:
        """
        Return the first name of a user registration.
        If social_name is not empty, use it as the first name.
        If not, split the name and return the first part.
        """
        registration = cls.select_stmt(registration_id, session)
        if registration.social_name:
            return registration.social_name
        return registration.name.split(" ")[0]

    @classmethod
    def get_by_email(cls, email: str, session: Session) -> "Registration | None":
        """
        Return the registration record associated with the given email.
        This uses a join with the Emails table.
        """

        statement = select(cls).join(Emails).where(Emails.email_address == email)
        result = session.exec(statement)
        return result.first()

    @classmethod
    def upsert_discord_id(cls, registration_id: int, discord_id: str, session: Session) -> None:
        """
        Upsert (update) the discord_id for the given registration.
        """
        registration = cls.select_stmt(registration_id, session)
        if registration:
            registration.discord_id = discord_id
            session.add(registration)
            session.commit()
            session.refresh(registration)


class RegistrationAudit(BaseAuditModel, table=True):
    """Audit log for registration changes, logging details of updates to user registration records."""

    __tablename__ = "registration_audit"

    registration_id: int
    old_data: dict | None = Field(default=None, sa_column=Column(JSON))
    new_data: dict | None = Field(default=None, sa_column=Column(JSON))


class Addresses(BaseSQLModel, table=True):
    """Model for address information related to user registrations."""

    __tablename__ = "addresses"

    address_id: int | None = Field(default=None, primary_key=True)
    registration_id: int = Field(foreign_key="registration.registration_id")
    state: str | None = None
    city: str | None = Field(max_length=100)
    address: str | None = Field(max_length=255)
    neighborhood: str | None = Field(max_length=100)
    zip: str | None = Field(max_length=40)
    country: str | None = None
    latlong: str | None = None

    registration: "Registration" = Relationship(back_populates="addresses")


class CertsAntecCriminais(BaseSQLModel, table=True):
    """Model for storing criminal record certificates associated with user registrations."""

    __tablename__ = "certs_antec_criminais"

    id: int | None = Field(default=None, primary_key=True)
    registration_id: int = Field(foreign_key="registration.registration_id")
    expiration_date: date | None = None
    verified: bool | None = None
    url: str | None = None

    registration: "Registration" = Relationship(back_populates="certs_antec_criminais")


class Emails(BaseSQLModel, table=True):
    """Model for storing email information linked to user registrations."""

    __tablename__ = "emails"

    email_id: int | None = Field(default=None, primary_key=True)
    registration_id: int = Field(foreign_key="registration.registration_id")
    email_type: str | None = Field(max_length=50)
    email_address: str | None = Field(max_length=255, min_length=5, index=True)
    registration: "Registration" = Relationship(back_populates="emails")


class LegalRepresentatives(BaseSQLModel, table=True):
    """Model for legal representatives associated with a user registration."""

    __tablename__ = "legal_representatives"

    representative_id: int | None = Field(default=None, primary_key=True)
    registration_id: int = Field(foreign_key="registration.registration_id")
    cpf: str | None = Field(max_length=11, min_length=11)
    full_name: str | None = Field(max_length=255)
    email: str | None = Field(max_length=255, min_length=5, index=True)
    phone: str | None = Field(max_length=60, min_length=9)
    alternative_phone: str | None = Field(default=None, max_length=60, min_length=9)
    observations: str | None = None

    registration: "Registration" = Relationship(back_populates="legal_representatives")


class MemberGroups(BaseSQLModel, table=True):
    """Model representing group memberships for members, including entry and exit data."""

    __tablename__ = "member_groups"
    __table_args__ = (
        UniqueConstraint("phone_number", "group_id", "entry_date", name="unique_member_group"),
    )

    id: int | None = Field(default=None, primary_key=True)
    phone_number: str = Field(max_length=20, min_length=10)
    group_id: str = Field(max_length=255)
    entry_date: date = Field(sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP")))
    status: str = Field(max_length=50)
    registration_id: int | None = Field(foreign_key="registration.registration_id")
    exit_date: date | None = None
    removal_reason: str | None = None

    registration: "Registration" = Relationship(back_populates="member_groups")


class MembershipPayments(BaseSQLModel, table=True):
    """Model for recording payment information related to membership dues."""

    __tablename__ = "membership_payments"

    payment_id: int | None = Field(default=None, primary_key=True)
    registration_id: int = Field(foreign_key="registration.registration_id")
    payment_date: datetime | None = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    )
    expiration_date: date | None = None
    amount_paid: condecimal(max_digits=10, decimal_places=2) | None = None  # type: ignore
    observation: str | None = None
    payment_method: str | None = None
    transaction_id: str | None = None
    payment_status: str | None = None
    registration: Registration | None = Relationship(back_populates="membership_payments")

    @classmethod
    def get_last_payment(
        cls, registration_id: int, session: Session
    ) -> "MembershipPayments | None":
        """Return the last payment record for a given registration ID."""
        statement = (
            select(cls)
            .where(cls.registration_id == registration_id)
            .order_by(cls.payment_date.desc())
        )
        results = session.exec(statement)
        return results.first()


class Phones(BaseSQLModel, table=True):
    """Model for phone numbers associated with user registrations."""

    __tablename__ = "phones"

    phone_id: int | None = Field(default=None, primary_key=True)
    registration_id: int = Field(foreign_key="registration.registration_id")
    phone_number: str = Field(max_length=60, min_length=9)
    registration: Registration | None = Relationship(back_populates="phones")

    @classmethod
    def select(cls, phone: int, session: Session) -> list["Phones"]:
        """Return a list of phone records matching the numeric phone pattern."""
        statement = select(cls).where(
            func.lower(
                func.cast(func.regexp_replace(cls.phone_number, r"\D", "", "g"), String)
            ).like(f"%{phone}%")
        )
        results = session.exec(statement)
        return list(results.all())

    @classmethod
    def get_member_by_phone(cls, phone_number: int, session: Session) -> "Phones | None":
        """Return a member by phone number."""
        phones = cls.select(phone=phone_number, session=session)
        if len(phones) > 1:
            raise ValueError("More than one phone number found")
        return phones[0] if phones else None


class WhatsappComms(BaseSQLModel, table=True):
    """Model representing a communication log with a phone number, date, status, and reason."""

    __tablename__ = "whatsapp_comms"
    __table_args__ = (UniqueConstraint("phone_number", "reason", name="uq_phone_number_reason"),)

    id: int | None = Field(default=None, primary_key=True)
    phone_number: str = Field(max_length=20, min_length=10)
    communication_date: datetime | None = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    )
    status: str = Field(default="pending", max_length=50)
    reason: str | None = Field(default=None, max_length=255)
    timestamp: datetime | None = Field(
        sa_column=Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    )


class GroupList(SQLModel, table=True):
    """Model for the group_list table."""

    __tablename__ = "group_list"

    group_id: str = Field(max_length=255, primary_key=True)
    group_name: str = Field(max_length=255)


class WhatsappMessages(SQLModel, table=True):
    """Model for the whatsapp_messages table."""

    __tablename__ = "whatsapp_messages"

    id: int = Field(primary_key=True)
    message_id: str = Field(max_length=128, unique=True)
    group_id: str = Field(max_length=128, index=True)
    registration_id: int = Field(index=True)
    timestamp: datetime = Field(index=True)
    phone: str = Field(max_length=20, min_length=10)
    message_type: str = Field(max_length=50)
    device_type: str = Field(max_length=50)
    content: str | None = Field(default=None, sa_column=Column(Text, nullable=True))


class IAMRoles(SQLModel, table=True):
    """Model for the iam_roles table."""

    __tablename__ = "iam_roles"

    id: int = Field(primary_key=True)
    role_name: str = Field(max_length=128)
    role_description: str = Field(max_length=512)


class IAMGroups(SQLModel, table=True):
    """Model for the iam_groups table."""

    __tablename__ = "iam_groups"

    id: int = Field(primary_key=True)
    group_name: str = Field(max_length=128)
    group_description: str = Field(max_length=512)


class IAMPermissions(SQLModel, table=True):
    """Model for the iam_role_permissions table."""

    __tablename__ = "iam_permissions"

    id: int = Field(primary_key=True)
    permission_name: str = Field(max_length=128)
    permission_description: str = Field(max_length=512)


class IAMRolePermissionsMap(SQLModel, table=True):
    """Model for the iam_role_permissions_map table."""

    __tablename__ = "iam_role_permissions_map"

    id: int = Field(primary_key=True)
    role_id: int = Field(sa_column=Column(Integer, ForeignKey("iam_roles.id", ondelete="CASCADE")))
    permission_id: int = Field(
        sa_column=Column(Integer, ForeignKey("iam_permissions.id", ondelete="CASCADE"))
    )


class IAMGroupPermissionsMap(SQLModel, table=True):
    """Model for the iam_group_permissions_map table."""

    __tablename__ = "iam_group_permissions_map"

    id: int = Field(primary_key=True)
    group_id: int = Field(
        sa_column=Column(Integer, ForeignKey("iam_groups.id", ondelete="CASCADE"))
    )
    permission_id: int = Field(
        sa_column=Column(Integer, ForeignKey("iam_permissions.id", ondelete="CASCADE"))
    )


class IAMUserRolesMap(SQLModel, table=True):
    """Model for the iam_user_roles_map table."""

    __tablename__ = "iam_user_roles_map"

    id: int = Field(primary_key=True)
    registration_id: int = Field(
        sa_column=Column(Integer, ForeignKey("registration.registration_id", ondelete="CASCADE"))
    )
    role_id: int = Field(sa_column=Column(Integer, ForeignKey("iam_roles.id", ondelete="CASCADE")))


class IAMUserGroupsMap(SQLModel, table=True):
    """Model for the iam_user_groups_map table."""

    __tablename__ = "iam_user_groups_map"

    id: int = Field(primary_key=True)
    registration_id: int = Field(
        sa_column=Column(Integer, ForeignKey("registration.registration_id", ondelete="CASCADE"))
    )
    group_id: int = Field(
        sa_column=Column(Integer, ForeignKey("iam_groups.id", ondelete="CASCADE"))
    )

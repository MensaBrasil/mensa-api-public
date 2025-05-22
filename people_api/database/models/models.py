"""
SQLmodels
"""

from datetime import date, datetime, timezone

from pydantic import EmailStr, condecimal
from sqlmodel import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Field,
    ForeignKey,
    Integer,
    Relationship,
    SQLModel,
    String,
    Text,
    UniqueConstraint,
    and_,
    col,
    delete,
    func,
    insert,
    select,
    text,
    update,
)

from people_api.database.models.feedback import FeedbackTargets, FeedbackTypes
from people_api.database.models.types import CPFNumber, PhoneNumber, ZipNumber


class BaseSQLModel(SQLModel):
    """Base class for SQLModel classes, providing common fields and methods."""

    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now()},
    )  # type: ignore
    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()},
    )  # type: ignore

    @classmethod
    def select_all(cls, **filters):
        """Select all instances of the model that match the provided filters."""
        query = select(cls)
        for field_name, value in filters.items():
            query = query.where(getattr(cls, field_name) == value)
        return query

    @classmethod
    def select_one(cls, **filters):
        """Select a single instance of the model that matches the provided filters."""
        query = select(cls)
        for field_name, value in filters.items():
            query = query.where(getattr(cls, field_name) == value)
        return query

    @classmethod
    def update_instance(cls, instance: "BaseSQLModel", update_data: dict) -> "BaseSQLModel":
        """Update the provided instance with the provided data."""
        for key, value in update_data.items():
            setattr(instance, key, value)
        return instance


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

    registration_id: int = Field(default=None, primary_key=True)
    expelled: bool = Field(sa_column=Column(Boolean, server_default=text("false")))
    deceased: bool = Field(sa_column=Column(Boolean, server_default=text("false")))
    transferred: bool = Field(sa_column=Column(Boolean, server_default=text("false")))
    name: str | None = None
    social_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    cpf: CPFNumber | None = Field(max_length=11, min_length=11)
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
    def select_stmt_by_id(cls, registration_id: int):
        """Return a select statement for a registration record by ID."""
        return select(cls).where(cls.registration_id == registration_id)

    @classmethod
    def select_stmt_by_email(cls, email: str):
        """
        Return a select statement for the registration record associated with the given email.
        """
        return select(cls).join(Emails).where(Emails.email_address == email)

    @classmethod
    def update_stmt_discord_id(cls, registration_id: int, discord_id: str):
        """
        Return an update statement for the discord_id for the given registration.
        """
        return (
            update(cls)
            .where(cls.registration_id == registration_id)  # type: ignore[arg-type]
            .values(discord_id=discord_id)
        )

    @classmethod
    def get_registration_by_last_8_phone_digits(cls, phone_number: str):
        """
        Return a select statement for a registration record by the last 8 digits of the phone number.
        """
        phone_pattern = f"%{phone_number[-8:]}"
        return (
            select(cls)
            .join(Phones)
            .where(
                func.lower(
                    func.cast(func.regexp_replace(Phones.phone_number, r"\D", "", "g"), String)
                ).like(phone_pattern)
            )
        )


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
    zip: ZipNumber | None = Field(None, max_length=12)
    country: str | None = None
    registration: "Registration" = Relationship(back_populates="addresses")

    @classmethod
    def get_address_for_member(cls, member_id: int):
        """
        Return a select statement for Addresses instances for a given member_id.
        """
        return select(cls).where(cls.registration_id == member_id)

    @classmethod
    def insert_stmt_for_address(cls, mb: int, address: "Addresses"):
        """
        Return an insert statement for adding an address for the given member.
        """
        return insert(cls).values(
            registration_id=mb,
            state=address.state,
            city=address.city,
            address=address.address,
            neighborhood=address.neighborhood,
            zip=address.zip,
        )

    @classmethod
    def update_stmt_for_address(cls, mb: int, address_id: int, new_address: "Addresses"):
        """
        Return an update statement for updating an address record based on the given
        member id (mb) and address id, using the new address details.
        """
        return (
            update(cls)
            .where(and_(cls.registration_id == mb, cls.address_id == address_id))
            .values(
                state=new_address.state,
                city=new_address.city,
                address=new_address.address,
                neighborhood=new_address.neighborhood,
                zip=new_address.zip,
            )
        )

    @classmethod
    def delete_stmt_for_address(cls, mb: int, address_id: int):
        """
        Return a delete statement for an address record based on the given member (mb)
        and address ID.
        """
        return delete(Addresses).where(
            and_(Addresses.registration_id == mb, Addresses.address_id == address_id)
        )


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
    email_address: EmailStr | None = Field(None, max_length=255, min_length=5, index=True)
    registration: "Registration" = Relationship(back_populates="emails")

    @classmethod
    def insert_stmt_for_email(cls, mb: int, email: "Emails"):
        """
        Return an insert statement for adding an email record for the given member.
        """
        return insert(cls).values(
            registration_id=mb,
            email_type=email.email_type,
            email_address=email.email_address,
        )

    @classmethod
    def update_stmt_for_email(cls, mb: int, email_id: int, new_email: "Emails"):
        """
        Return an update statement for modifying an email record based on the given
        member id (mb) and email id, setting the new email_type and email_address.
        """
        return (
            update(cls)
            .where(and_(cls.registration_id == mb, cls.email_id == email_id))
            .values(
                email_type=new_email.email_type,
                email_address=new_email.email_address,
            )
        )

    @classmethod
    def get_emails_for_member(cls, member_id: int):
        """
        Return a select statement for Email instances for a given member_id.
        """
        return select(cls).where(cls.registration_id == member_id)

    @classmethod
    def delete_stmt_for_email(cls, mb: int, email_id: int):
        """
        Return a delete statement for an email record based on the given member id (mb)
        and email id.
        """
        return delete(cls).where(and_(cls.registration_id == mb, cls.email_id == email_id))

    @classmethod
    def select_registration_id_by_email(cls, email: str):
        """
        Return a select statement that retrieves the registration_id based on email_address.
        """
        return select(cls.registration_id).where(cls.email_address == email)


class LegalRepresentatives(BaseSQLModel, table=True):
    """Model for legal representatives associated with a user registration."""

    __tablename__ = "legal_representatives"
    representative_id: int | None = Field(default=None, primary_key=True)
    registration_id: int = Field(foreign_key="registration.registration_id")
    cpf: CPFNumber | None = Field(None, max_length=11, min_length=11)
    full_name: str | None = Field(max_length=255)
    email: EmailStr | None = Field(None, max_length=255, min_length=5, index=True)
    phone: PhoneNumber | None = Field(max_length=60, min_length=9)
    alternative_phone: PhoneNumber | None = Field(max_length=60, min_length=9)
    observations: str | None = None
    registration: "Registration" = Relationship(back_populates="legal_representatives")

    @classmethod
    def insert_stmt_for_legal_representative(
        cls, mb: int, legal_representative: "LegalRepresentatives"
    ):
        """
        Return an insert statement for adding a legal representative for the given member.
        """
        return insert(cls).values(
            registration_id=mb,
            cpf=legal_representative.cpf,
            full_name=legal_representative.full_name,
            email=legal_representative.email,
            phone=legal_representative.phone,
            alternative_phone=legal_representative.alternative_phone,
            observations=legal_representative.observations,
        )

    @classmethod
    def get_legal_representatives_for_member(cls, member_id: int):
        """
        Return a select statement for LegalRepresentative instances for a given member_id.
        """
        return select(cls).where(cls.registration_id == member_id)

    @classmethod
    def update_stmt_for_legal_representative(
        cls, mb: int, legal_rep_id: int, new_legal_rep: "LegalRepresentatives"
    ):
        """
        Return an update statement for a legal representative record based on the given member id (mb)
        and legal representative id, using the new legal representative details.
        """
        return (
            update(cls)
            .where(and_(cls.registration_id == mb, cls.representative_id == legal_rep_id))
            .values(
                cpf=new_legal_rep.cpf,
                full_name=new_legal_rep.full_name,
                email=new_legal_rep.email,
                phone=new_legal_rep.phone,
                alternative_phone=new_legal_rep.alternative_phone,
                observations=new_legal_rep.observations,
            )
        )

    @classmethod
    def delete_stmt_for_legal_representative(cls, mb: int, legal_rep_id: int):
        """
        Return a delete statement for a legal representative record based on the given member (mb)
        and legal representative id.
        """
        return delete(cls).where(
            and_(cls.registration_id == mb, cls.representative_id == legal_rep_id)
        )


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
    def select_stmt_last_payment(cls, registration_id: int):
        """Return a select statement for the last payment record for a given registration ID."""
        return (
            select(cls)
            .where(cls.registration_id == registration_id)
            .order_by(Column("payment_date").desc())
        )


class Phones(BaseSQLModel, table=True):
    """Model for phone numbers associated with user registrations."""

    __tablename__ = "phones"
    phone_id: int | None = Field(default=None, primary_key=True)
    registration_id: int = Field(foreign_key="registration.registration_id")
    phone_number: PhoneNumber = Field(max_length=60, min_length=9)
    registration: Registration | None = Relationship(back_populates="phones")

    @classmethod
    def select_stmt_by_phone_pattern(cls, phone: int):
        """Return a select statement for phone records matching the numeric phone pattern."""
        return select(cls).where(
            func.lower(
                func.cast(func.regexp_replace(cls.phone_number, r"\D", "", "g"), String)
            ).like(f"%{phone}%")
        )

    @classmethod
    def select_stmt_by_registration_id(cls, registration_id: int):
        """Return a select statement for phone records by registration ID."""
        return select(cls).where(cls.registration_id == registration_id)

    @classmethod
    def get_member_by_trailing_8_digit_phone(cls, phone_number: int):
        """Return a select statement for a member by the last 8 digits of the phone number."""
        phone_pattern = f"%{str(phone_number)[-8:]}"
        return select(cls).where(
            func.lower(
                func.cast(func.regexp_replace(cls.phone_number, r"\D", "", "g"), String)
            ).like(phone_pattern)
        )

    @classmethod
    def get_phones_for_member(cls, member_id: int):
        """
        Return a select statement for Phones instances for a given member_id.
        """
        return select(cls).where(cls.registration_id == member_id)

    @classmethod
    def insert_stmt_for_phone(cls, mb: int, phone: PhoneNumber):
        """Return an insert statement for adding a phone for the given member."""
        return insert(cls).values(registration_id=mb, phone_number=phone)

    @classmethod
    def update_stmt_for_phone(cls, mb: int, phone_id: int, new_phone: PhoneNumber):
        """
        Return an update statement for the phone number for the given registration (mb)
        and phone ID.
        """
        return (
            update(cls)
            .where(and_(cls.registration_id == mb, cls.phone_id == phone_id))
            .values(phone_number=new_phone)
        )

    @classmethod
    def delete_stmt_for_phone(cls, mb: int, phone_id: int):
        """
        Return a delete statement for a phone record based on the given registration (mb)
        and phone ID.
        """
        return delete(cls).where(and_(cls.registration_id == mb, cls.phone_id == phone_id))


class WhatsappComms(BaseSQLModel, table=True):
    """Model representing a communication log with a phone number, date, status, and reason."""

    __tablename__ = "whatsapp_comms"
    __table_args__ = (UniqueConstraint("phone_number", "reason", name="uq_phone_number_reason"),)

    id: int | None = Field(default=None, primary_key=True)
    phone_number: str = Field(max_length=20, min_length=10)
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

    @classmethod
    def select_by_group_name(cls, group_name: str):
        """
        Return a select statement that retrieves GroupList instances whose group_name matches the given string.
        """
        return select(cls).where(cls.group_name == group_name)


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


class PhoneInput(SQLModel):
    """Model for phone input data."""

    phone: PhoneNumber


class EmailInput(SQLModel):
    """Model for email input data."""

    email_address: EmailStr
    email_type: str | None = Field(max_length=50)


class IAMRoles(SQLModel, table=True):
    """Model for the iam_roles table."""

    __tablename__ = "iam_roles"

    id: int = Field(primary_key=True)
    role_name: str = Field(max_length=128)
    role_description: str = Field(max_length=512)

    @classmethod
    def select_by_role_name(cls, role_name: str):
        """
        Return a select statement for IAMRoles instances with the given role_name.
        """
        return select(cls).where(cls.role_name == role_name)


class IAMGroups(SQLModel, table=True):
    """Model for the iam_groups table."""

    __tablename__ = "iam_groups"

    id: int = Field(primary_key=True)
    group_name: str = Field(max_length=128)
    group_description: str = Field(max_length=512)

    @classmethod
    def select_by_group_name(cls, group_name: str):
        """
        Return a select statement for IAMGroups instances with the given group_name.
        """
        return select(cls).where(cls.group_name == group_name)


class IAMPermissions(SQLModel, table=True):
    """Model for the iam_role_permissions table."""

    __tablename__ = "iam_permissions"

    id: int = Field(primary_key=True)
    permission_name: str = Field(max_length=128)
    permission_description: str = Field(max_length=512)

    @classmethod
    def select_role_permissions_by_registration_id(cls, registration_id: int):
        """
        Get permissions for a member based on their roles.
        """
        return (
            select(col(cls.permission_name))
            .select_from(IAMUserRolesMap)
            .join(
                IAMRolePermissionsMap,
                col(IAMUserRolesMap.role_id) == col(IAMRolePermissionsMap.role_id),
            )
            .join(
                cls,
                col(IAMRolePermissionsMap.permission_id) == col(cls.id),
            )
            .where(col(IAMUserRolesMap.registration_id) == registration_id)
        )

    @classmethod
    def select_group_permissions_by_registration_id(cls, registration_id: int):
        """
        Get permissions for a member based on their groups.
        """
        return (
            select(col(cls.permission_name))
            .select_from(IAMUserGroupsMap)
            .join(
                IAMGroupPermissionsMap,
                col(IAMUserGroupsMap.group_id) == col(IAMGroupPermissionsMap.group_id),
            )
            .join(
                cls,
                col(IAMGroupPermissionsMap.permission_id) == col(cls.id),
            )
            .where(col(IAMUserGroupsMap.registration_id) == registration_id)
        )

    @classmethod
    def get_role_permissions_by_role_name(cls, role_name: str):
        """
        Get permissions for a role by role name.
        """
        return (
            select(col(cls.permission_name))
            .select_from(IAMRolePermissionsMap)
            .join(
                cls,
                col(IAMRolePermissionsMap.permission_id) == col(cls.id),
            )
            .join(IAMRoles, col(IAMRolePermissionsMap.role_id) == col(IAMRoles.id))
            .where(col(IAMRoles.role_name) == role_name)
        )

    @classmethod
    def get_group_permissions_by_group_name(cls, group_name: str):
        """
        Get permissions for a group by group name.
        """
        return (
            select(col(cls.permission_name))
            .select_from(IAMGroupPermissionsMap)
            .join(
                cls,
                col(IAMGroupPermissionsMap.permission_id) == col(cls.id),
            )
            .join(IAMGroups, col(IAMGroupPermissionsMap.group_id) == col(IAMGroups.id))
            .where(col(IAMGroups.group_name) == group_name)
        )

    @classmethod
    def select_by_permission_name(cls, permission_name: str):
        """
        Return a select statement for IAMPermissions instances with the given permission_name.
        """
        return select(cls).where(cls.permission_name == permission_name)


class IAMRolePermissionsMap(SQLModel, table=True):
    """Model for the iam_role_permissions_map table."""

    __tablename__ = "iam_role_permissions_map"

    id: int = Field(primary_key=True)
    role_id: int = Field(sa_column=Column(Integer, ForeignKey("iam_roles.id", ondelete="CASCADE")))
    permission_id: int = Field(
        sa_column=Column(Integer, ForeignKey("iam_permissions.id", ondelete="CASCADE"))
    )

    @classmethod
    def select_by_role_and_permission(cls, role_id: int, permission_id: int):
        """
        Return a select statement to check if a mapping exists for the given role_id and permission_id.
        """
        return select(cls).where(cls.role_id == role_id, cls.permission_id == permission_id)


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

    @classmethod
    def select_by_group_and_permission(cls, group_id: int, permission_id: int):
        """
        Return a select statement to check if a mapping exists for the given group_id and permission_id.
        """
        return select(cls).where(cls.group_id == group_id, cls.permission_id == permission_id)


class IAMUserRolesMap(SQLModel, table=True):
    """Model for the iam_user_roles_map table."""

    __tablename__ = "iam_user_roles_map"

    id: int = Field(primary_key=True)
    registration_id: int = Field(
        sa_column=Column(Integer, ForeignKey("registration.registration_id", ondelete="CASCADE"))
    )
    role_id: int = Field(sa_column=Column(Integer, ForeignKey("iam_roles.id", ondelete="CASCADE")))

    @classmethod
    def select_role_names_by_registration_id(cls, registration_id: int):
        """
        Return a select statement that retrieves role names for a given registration_id.
        """
        return (
            select(IAMRoles.role_name)
            .select_from(cls)
            .join(IAMRoles, col(cls.role_id) == col(IAMRoles.id))
            .where(cls.registration_id == registration_id)
        )

    @classmethod
    def select_members_by_role_name(cls, role_name: str):
        """
        Return a select statement that retrieves members (name and registration_id) for a given role name.
        """
        return (
            select(Registration.name, cls.registration_id)
            .join(IAMRoles, col(cls.role_id) == col(IAMRoles.id))
            .join(
                Registration,
                col(cls.registration_id) == col(Registration.registration_id),
            )
            .where(IAMRoles.role_name == role_name)
        )

    @classmethod
    def select_by_role_and_member(cls, role_id: int, member_id: int):
        """
        Return a select statement to check if a role is already assigned to a member.
        """
        return select(cls).where(cls.role_id == role_id, cls.registration_id == member_id)


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

    @classmethod
    def select_group_names_by_registration_id(cls, registration_id: int):
        """
        Return a select statement that retrieves group names for a given registration_id.
        """
        return (
            select(IAMGroups.group_name)
            .select_from(cls)
            .join(IAMGroups, col(cls.group_id) == col(IAMGroups.id))
            .where(cls.registration_id == registration_id)
        )

    @classmethod
    def select_members_by_group_name(cls, group_name: str):
        """
        Return a select statement that retrieves members (name and registration_id) for a given group name.
        """
        return (
            select(Registration.name, cls.registration_id)
            .join(IAMGroups, col(cls.group_id) == col(IAMGroups.id))
            .join(
                Registration,
                col(cls.registration_id) == col(Registration.registration_id),
            )
            .where(IAMGroups.group_name == group_name)
        )

    @classmethod
    def select_by_group_and_member(cls, group_id: int, member_id: int):
        """
        Return a select statement to check if a group is already assigned to a member.
        """
        return select(cls).where(cls.group_id == group_id, cls.registration_id == member_id)


class Feedback(BaseSQLModel, table=True):
    """Model for feedback records."""

    __tablename__ = "feedbacks"

    id: int | None = Field(default=None, primary_key=True)
    registration_id: int = Field(
        sa_column=Column(Integer, ForeignKey("registration.registration_id", ondelete="CASCADE"))
    )
    feedback_text: str | None = Field(max_length=1200)
    feedback_target: FeedbackTargets = Field(
        sa_column=Column(Enum(FeedbackTargets), nullable=False)
    )
    feedback_type: FeedbackTypes = Field(
        sa_column=Column(
            Enum(FeedbackTypes),
            nullable=False,
        )
    )

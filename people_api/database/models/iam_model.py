"""Models for the Identity and Access Management (IAM) database."""

from fastapi import HTTPException, status
from pydantic import BaseModel, field_validator


def validate_name(data, field_name: str):
    """Validate name field."""
    if not isinstance(data, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Field: "{field_name}" must be a string.',
        )
    if data == "" or data.isspace():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Field: "{field_name}" cannot be empty.',
        )
    if data.isnumeric():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Field: "{field_name}" cannot be numeric.',
        )
    if " " in data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Field: "{field_name}" cannot contain spaces.',
        )

    processed_data = data.upper()
    return processed_data


def validate_permission_name(data, field_name: str):
    """Validate permission name field."""
    if not isinstance(data, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Field: "{field_name}" must be a string.',
        )
    if data == "" or data.isspace():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Field: "{field_name}" cannot be empty.',
        )
    if data.isnumeric():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Field: "{field_name}" cannot be numeric.',
        )
    if " " in data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Field: "{field_name}" cannot contain spaces.',
        )

    processed_data = data.upper()
    return processed_data


def validate_description(data, field_name: str):
    """Validate description field."""
    if not isinstance(data, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Field: "{field_name}" must be a string.',
        )
    if data == "" or data.isspace():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Field: "{field_name}" cannot be empty.',
        )
    if data.isnumeric():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Field: "{field_name}" cannot be numeric.',
        )

    return data


def validate_member_id(data, field_name: str):
    """Validate member ID field."""
    if not isinstance(data, int):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Field: "{field_name}" must be an integer.',
        )
    if data <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Field: "{field_name}" must be positive. (greater than 0)',
        )

    processed_data = int(data)
    return processed_data


class BaseValidateRoleName(BaseModel):
    """Base model for validating role name."""

    role_name: str

    @field_validator("role_name", mode="before")
    @classmethod
    def validate_role_name(cls, data):
        """Validate role name."""
        return validate_name(data, "role_name")


class BaseValidateRoleDescription(BaseModel):
    """Base model for validating role description."""

    role_description: str

    @field_validator("role_description", mode="before")
    @classmethod
    def validate_role_description(cls, data):
        """Validate role description."""
        return validate_description(data, "role_description")


class BaseValidateGroupName(BaseModel):
    """Base model for validating group name."""

    group_name: str

    @field_validator("group_name", mode="before")
    @classmethod
    def validate_group_name(cls, data):
        """Validate group name."""
        return validate_name(data, "group_name")


class BaseValidateGroupDescription(BaseModel):
    """Base model for validating group description."""

    group_description: str

    @field_validator("group_description", mode="before")
    @classmethod
    def validate_group_description(cls, data):
        """Validate group description."""
        return validate_description(data, "group_description")


class BaseValidatePermissionName(BaseModel):
    """Base model for validating permission name."""

    permission_name: str

    @field_validator("permission_name", mode="before")
    @classmethod
    def validate_permission_name(cls, data):
        """Validate permission name."""
        return validate_permission_name(data, "permission_name")


class BaseValidatePermissionDescription(BaseModel):
    """Base model for validating permission description."""

    permission_description: str

    @field_validator("permission_description", mode="before")
    @classmethod
    def validate_permission_description(cls, data):
        """Validate permission description."""
        return validate_description(data, "permission_description")


class BaseValidateMemberId(BaseModel):
    """Base model for validating member ID."""

    member_id: int

    @field_validator("member_id", mode="before")
    @classmethod
    def validate_member_id(cls, data):
        """Validate member ID."""
        return validate_member_id(data, "member_id")


class BaseValidateNewRoleName(BaseModel):
    """Base model for validating new role name."""

    new_role_name: str

    @field_validator("new_role_name", mode="before")
    @classmethod
    def validate_new_role_name(cls, data):
        """Validate new role name."""
        return validate_name(data, "new_role_name")


class BaseValidateNewRoleDescription(BaseModel):
    """Base model for validating new role description."""

    new_role_description: str | None = None

    @field_validator("new_role_description", mode="before")
    @classmethod
    def validate_new_role_description(cls, data):
        """Validate new role description."""
        return validate_description(data, "new_role_description")


class BaseValidateNewGroupName(BaseModel):
    """Base model for validating new group name."""

    new_group_name: str

    @field_validator("new_group_name", mode="before")
    @classmethod
    def validate_new_group_name(cls, data):
        """Validate new group name."""
        return validate_name(data, "new_group_name")


class BaseValidateNewGroupDescription(BaseModel):
    """Base model for validating new group description."""

    new_group_description: str | None = None

    @field_validator("new_group_description", mode="before")
    @classmethod
    def validate_new_group_description(cls, data):
        """Validate new group description."""
        return validate_description(data, "new_group_description")


class BaseValidateNewPermissionName(BaseModel):
    """Base model for validating new permission name."""

    new_permission_name: str

    @field_validator("new_permission_name", mode="before")
    @classmethod
    def validate_new_permission_name(cls, data):
        """Validate new permission name."""
        return validate_name(data, "new_permission_name")


class BaseValidateNewPermissionDescription(BaseModel):
    """Base model for validating new permission description."""

    new_permission_description: str | None = None

    @field_validator("new_permission_description", mode="before")
    @classmethod
    def validate_new_permission_description(cls, data):
        """Validate new permission description."""
        return validate_description(data, "new_permission_description")


class CreateRole(BaseValidateRoleName, BaseValidateRoleDescription):
    """Model for creating a role."""


class CreateGroup(BaseValidateGroupName, BaseValidateGroupDescription):
    """Model for creating a group."""


class CreatePermission(BaseValidatePermissionName, BaseValidatePermissionDescription):
    """Model for creating a permission."""


class AddRoleToMember(BaseValidateRoleName, BaseValidateMemberId):
    """Model for adding a role to a member."""


class AddGroupToMember(BaseValidateGroupName, BaseValidateMemberId):
    """Model for adding a group to a member."""


class AddPermissionToRole(BaseValidateRoleName, BaseValidatePermissionName):
    """Model for adding a permission to a role."""


class AddPermissionToGroup(BaseValidateGroupName, BaseValidatePermissionName):
    """Model for adding a permission to a group."""


class UpdateRole(BaseValidateRoleName, BaseValidateNewRoleName, BaseValidateNewRoleDescription):
    """Model for updating a role."""


class UpdateGroup(BaseValidateGroupName, BaseValidateNewGroupName, BaseValidateNewGroupDescription):
    """Model for updating a group."""


class UpdatePermission(
    BaseValidatePermissionName,
    BaseValidateNewPermissionName,
    BaseValidateNewPermissionDescription,
):
    """Model for updating a permission."""


class RemoveRoleFromMember(BaseValidateRoleName, BaseValidateMemberId):
    """Model for removing a role from a member."""


class RemoveGroupFromMember(BaseValidateGroupName, BaseValidateMemberId):
    """Model for removing a group from a member."""


class RemovePermissionFromRole(BaseValidateRoleName, BaseValidatePermissionName):
    """Model for removing a permission from a role."""


class RemovePermissionFromGroup(BaseValidateGroupName, BaseValidatePermissionName):
    """Model for removing a permission from a group."""


class DeleteRole(BaseValidateRoleName):
    """Model for deleting a role."""


class DeleteGroup(BaseValidateGroupName):
    """Model for deleting a group."""


class DeletePermission(BaseValidatePermissionName):
    """Model for deleting a permission."""

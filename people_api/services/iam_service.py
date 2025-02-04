"""This module contains the service class for IAM."""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database.models import (
    IAMGroupPermissionsMap,
    IAMGroups,
    IAMPermissions,
    IAMRolePermissionsMap,
    IAMRoles,
    IAMUserGroupsMap,
    IAMUserRolesMap,
    Registration,
)
from ..repositories import MemberRepository


class IamService:
    """Service class for IAM."""

    @staticmethod
    def get_member_roles(token_data: str, session: Session):
        """Get roles for a member by member id."""

        try:
            registration_id = MemberRepository.getMBByEmail(token_data["email"], session)

            statement = (
                select(IAMRoles.role_name)
                .select_from(IAMUserRolesMap)
                .join(IAMRoles, IAMUserRolesMap.role_id == IAMRoles.id)
                .where(IAMUserRolesMap.registration_id == registration_id)
            )
            results = session.exec(statement)
            roles = [result.role_name for result in results.all()]
            return (
                roles
                if roles
                else HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No roles found for member with id {registration_id}.",
                )
            )
        except Exception as e:
            return {"detail": f"Error: {e}"}

    @staticmethod
    def get_member_groups(token_data: str, session: Session):
        """Get groups for a member by member id."""

        try:
            registration_id = MemberRepository.getMBByEmail(token_data["email"], session)

            statement = (
                select(IAMGroups.group_name)
                .select_from(IAMUserGroupsMap)
                .join(IAMGroups, IAMUserGroupsMap.group_id == IAMGroups.id)
                .where(IAMUserGroupsMap.registration_id == registration_id)
            )
            results = session.exec(statement)
            groups = [result.group_name for result in results.all()]
            return (
                groups
                if groups
                else HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No groups found for member with id {registration_id}.",
                )
            )
        except Exception as e:
            return {"detail": f"Error: {e}"}

    @staticmethod
    def get_role_permissions_by_role_name(role_name: str, session: Session):
        """Get permissions for a role by role name."""

        statement = select(IAMRoles).filter(IAMRoles.role_name == role_name)
        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} does not exist.",
            )

        statement = (
            select(IAMPermissions.permission_name)
            .select_from(IAMRolePermissionsMap)
            .join(
                IAMPermissions,
                IAMRolePermissionsMap.permission_id == IAMPermissions.id,
            )
            .join(IAMRoles, IAMRolePermissionsMap.role_id == IAMRoles.id)
            .where(IAMRoles.role_name == role_name)
        )
        results = session.exec(statement)
        permissions = [result.permission_name for result in results.all()]
        if permissions:
            return permissions
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No permissions found for role: {role_name}.",
            )

    @staticmethod
    def get_group_permissions_by_group_name(group_name: str, session: Session):
        """Get permissions for a group by group name."""

        statement = select(IAMGroups).filter(IAMGroups.group_name == group_name)
        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} does not exist.",
            )

        statement = (
            select(IAMPermissions.permission_name)
            .select_from(IAMGroupPermissionsMap)
            .join(
                IAMPermissions,
                IAMGroupPermissionsMap.permission_id == IAMPermissions.id,
            )
            .join(IAMGroups, IAMGroupPermissionsMap.group_id == IAMGroups.id)
            .where(IAMGroups.group_name == group_name)
        )
        results = session.exec(statement)
        permissions = [result.permission_name for result in results.all()]
        if permissions:
            return permissions
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No permissions found for group {group_name}.",
            )

    @staticmethod
    def get_members_by_role_name(role_name: str, session: Session):
        """Get members by role."""

        statement = select(IAMRoles).filter(IAMRoles.role_name == role_name)
        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} does not exist.",
            )

        statement = (
            select(Registration.name, IAMUserRolesMap.registration_id)
            .join(IAMRoles, IAMUserRolesMap.role_id == IAMRoles.id)
            .join(
                Registration,
                IAMUserRolesMap.registration_id == Registration.registration_id,
            )
            .where(IAMRoles.role_name == role_name)
        )
        results = session.exec(statement)
        members = [[row[0], row[1]] for row in results.all()]
        if members:
            return members
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No members found with role {role_name}.",
            )

    @staticmethod
    def get_members_by_group_name(group_name: str, session: Session):
        """Get members by group."""

        statement = select(IAMGroups).filter(IAMGroups.group_name == group_name)
        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} does not exist.",
            )

        statement = (
            select(Registration.name, IAMUserGroupsMap.registration_id)
            .join(IAMGroups, IAMUserGroupsMap.group_id == IAMGroups.id)
            .join(
                Registration,
                IAMUserGroupsMap.registration_id == Registration.registration_id,
            )
            .where(IAMGroups.group_name == group_name)
        )
        results = session.exec(statement)
        members = [[row[0], row[1]] for row in results.all()]
        if members:
            return members
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No members found in group {group_name}.",
            )

    @staticmethod
    def create_role(role_name: str, role_description: str, session: Session):
        """Create a new role."""

        statement = select(IAMRoles).filter(IAMRoles.role_name == role_name)
        if session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role: {role_name} already exists.",
            )
        try:
            new_role = IAMRoles(role_name=role_name, role_description=role_description)
            session.add(new_role)
            return {"detail": f"Role: {new_role.role_name} created successfully."}
        except Exception as e:
            return {"detail": f"Error: {e}"}

    @staticmethod
    def create_group(group_name: str, group_description: str, session: Session):
        """Create a new group."""

        statement = select(IAMGroups).filter(IAMGroups.group_name == group_name)
        if session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Group: {group_name} already exists.",
            )
        try:
            new_group = IAMGroups(group_name=group_name, group_description=group_description)
            session.add(new_group)
            return {"detail": f"Group: {new_group.group_name} created successfully."}
        except Exception as e:
            return {"detail": f"Error: {e}"}

    @staticmethod
    def create_permission(permission_name: str, permission_description: str, session: Session):
        """Create a new permission."""

        statement = select(IAMPermissions).filter(IAMPermissions.permission_name == permission_name)
        if session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Permission: {permission_name} already exists.",
            )
        try:
            new_permission = IAMPermissions(
                permission_name=permission_name,
                permission_description=permission_description,
            )
            session.add(new_permission)
            return {"detail": f"Permission: {new_permission.permission_name} created successfully."}
        except Exception as e:
            return {"detail": f"Error: {e}"}

    @staticmethod
    def edit_role_by_name(
        role_name: str,
        new_role_name: str,
        session: Session,
        new_role_description: str = None,
    ):
        """Edit a role by role name."""

        statement = select(IAMRoles).filter(IAMRoles.role_name == role_name)
        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} does not exist.",
            )

        statement = select(IAMRoles).filter(IAMRoles.role_name == role_name)
        role = session.exec(statement).scalar()
        role.role_name = new_role_name
        role.role_description = (
            new_role_description if new_role_description else role.role_description
        )
        return {"detail": f"Role: {role_name} updated successfully."}

    @staticmethod
    def edit_group_by_name(
        group_name: str,
        new_group_name: str,
        session: Session,
        new_group_description: str = None,
    ):
        """Edit a group by group name."""

        statement = select(IAMGroups).filter(IAMGroups.group_name == group_name)
        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} does not exist.",
            )

        statement = select(IAMGroups).filter(IAMGroups.group_name == group_name)
        group = session.exec(statement).scalar()
        group.group_name = new_group_name
        group.group_description = (
            new_group_description if new_group_description else group.group_description
        )
        return {"detail": f"Group: {group_name} updated successfully."}

    @staticmethod
    def edit_permission_by_name(
        permission_name: str,
        new_permission_name: str,
        session: Session,
        new_permission_description: str = None,
    ):
        """Edit a permission by permission name."""

        statement = select(IAMPermissions).filter(IAMPermissions.permission_name == permission_name)
        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission: {permission_name} does not exist.",
            )

        statement = select(IAMPermissions).filter(IAMPermissions.permission_name == permission_name)
        permission = session.exec(statement).scalar()
        permission.permission_name = new_permission_name
        permission.permission_description = (
            new_permission_description
            if new_permission_description
            else permission.permission_description
        )
        return {"detail": f"Permission: {permission_name} updated successfully."}

    @staticmethod
    def add_permission_to_role(role_name: str, permission_name: str, session: Session):
        """Add a permission to a role."""

        statement = select(IAMRoles.id).filter(IAMRoles.role_name == role_name)
        role_id = session.exec(statement).scalar()
        statement = select(IAMPermissions.id).filter(
            IAMPermissions.permission_name == permission_name
        )
        permission_id = session.exec(statement).scalar()
        statement = select(IAMRolePermissionsMap).filter(
            IAMRolePermissionsMap.role_id == role_id,
            IAMRolePermissionsMap.permission_id == permission_id,
        )
        role_already_has_permission = session.exec(statement).scalar()

        if role_already_has_permission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role: {role_name} already has permission: {permission_name}.",
            )
        statement = select(IAMRoles).filter(IAMRoles.role_name == role_name)
        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role: {role_name} does not exist.",
            )
        statement = select(IAMPermissions).filter(IAMPermissions.permission_name == permission_name)
        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Permission: {permission_name} does not exist.",
            )
        try:
            statement = select(IAMRoles).filter(IAMRoles.role_name == role_name)
            role = session.exec(statement).scalar()
            statement = select(IAMPermissions).filter(
                IAMPermissions.permission_name == permission_name
            )
            permission = session.exec(statement).scalar()
            role_permission_map = IAMRolePermissionsMap(
                role_id=role.id, permission_id=permission.id
            )
            session.add(role_permission_map)
            return {
                "detail": f"Permission: {permission_name} added to role: {role_name} successfully."
            }
        except Exception as e:
            return {"detail": f"Error: {e}"}

    @staticmethod
    def add_permission_to_group(group_name: str, permission_name: str, session: Session):
        """Add a permission to a group."""

        statement = select(IAMGroups.id).filter(IAMGroups.group_name == group_name)
        group_id = session.exec(statement).scalar()
        statement = select(IAMPermissions.id).filter(
            IAMPermissions.permission_name == permission_name
        )
        permission_id = session.exec(statement).scalar()
        statement = select(IAMGroupPermissionsMap).filter(
            IAMGroupPermissionsMap.group_id == group_id,
            IAMGroupPermissionsMap.permission_id == permission_id,
        )
        group_already_has_permission = session.exec(statement).scalar()
        if group_already_has_permission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Group: {group_name} already has permission: {permission_name}.",
            )
        statement = select(IAMGroups).filter(IAMGroups.group_name == group_name)
        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Group: {group_name} does not exist.",
            )
        statement = select(IAMPermissions).filter(IAMPermissions.permission_name == permission_name)
        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Permission: {permission_name} does not exist.",
            )
        try:
            statement = select(IAMGroups).filter(IAMGroups.group_name == group_name)
            group = session.exec(statement).scalar()
            statement = select(IAMPermissions).filter(
                IAMPermissions.permission_name == permission_name
            )
            permission = session.exec(statement).scalar()
            group_permission_map = IAMGroupPermissionsMap(
                group_id=group.id, permission_id=permission.id
            )
            session.add(group_permission_map)
            return {
                "detail": f"Permission: {permission_name} added to group: {group_name} successfully."
            }
        except Exception as e:
            return {"detail": f"Error: {e}"}

    @staticmethod
    def add_role_to_member(role_name: str, member_id: int, session: Session):
        """Add a role to a member."""

        statement = select(IAMRoles.id).filter(IAMRoles.role_name == role_name)
        role_id = session.exec(statement).scalar()
        statement = select(IAMUserRolesMap).filter(
            IAMUserRolesMap.role_id == role_id,
            IAMUserRolesMap.registration_id == member_id,
        )
        check_role_assigned = session.exec(statement).scalar()
        if check_role_assigned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role: {role_name} already assigned to member with id: {member_id}.",
            )
        statement = select(IAMRoles).filter(IAMRoles.role_name == role_name)
        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role: {role_name} does not exist.",
            )
        try:
            statement = select(IAMRoles).filter(IAMRoles.role_name == role_name)
            role = session.exec(statement).scalar()
            role_map = IAMUserRolesMap(role_id=role.id, registration_id=member_id)
            session.add(role_map)
            return {
                "detail": f"Role: {role_name} added to member with id: {member_id} successfully."
            }
        except Exception as e:
            return {"detail": f"Error: {e}"}

    @staticmethod
    def add_group_to_member(group_name: str, member_id: int, session: Session):
        """Add a group to a member."""

        statement = select(IAMGroups.id).filter(IAMGroups.group_name == group_name)
        group_id = session.exec(statement).scalar()
        statement = select(IAMUserGroupsMap).filter(
            IAMUserGroupsMap.group_id == group_id,
            IAMUserGroupsMap.registration_id == member_id,
        )
        check_group_assigned = session.exec(statement).scalar()
        if check_group_assigned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Group: {group_name} already assigned to member with id: {member_id}.",
            )
        statement = select(IAMGroups).filter(IAMGroups.group_name == group_name)
        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Group: {group_name} does not exist.",
            )
        try:
            statement = select(IAMGroups).filter(IAMGroups.group_name == group_name)
            group = session.exec(statement).scalar()
            group_map = IAMUserGroupsMap(group_id=group.id, registration_id=member_id)
            session.add(group_map)
            return {
                "detail": f"Group: {group_name} added to member with id: {member_id} successfully."
            }
        except Exception as e:
            return {"detail": f"Error: {e}"}

    @staticmethod
    def remove_permission_from_role(role_name: str, permission_name: str, session: Session):
        """Remove a permission from a role."""

        statement = select(IAMRoles).filter(IAMRoles.role_name == role_name)
        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} does not exist.",
            )

        statement = select(IAMPermissions).filter(IAMPermissions.permission_name == permission_name)
        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission: {permission_name} does not exist.",
            )

        statement = select(IAMRoles).filter(IAMRoles.role_name == role_name)
        role = session.exec(statement).scalar()
        statement = select(IAMPermissions).filter(IAMPermissions.permission_name == permission_name)
        permission = session.exec(statement).scalar()
        statement = select(IAMRolePermissionsMap).filter(
            IAMRolePermissionsMap.role_id == role.id,
            IAMRolePermissionsMap.permission_id == permission.id,
        )

        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} does not have permission: {permission_name}.",
            )

        role_permission_map = session.exec(statement).scalar()
        session.delete(role_permission_map)
        return {
            "detail": f"Permission: {permission_name} removed from role: {role_name} successfully."
        }

    @staticmethod
    def remove_permission_from_group(group_name: str, permission_name: str, session: Session):
        """Remove a permission from a group."""

        statement = select(IAMGroups).filter(IAMGroups.group_name == group_name)
        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} does not exist.",
            )

        statement = select(IAMPermissions).filter(IAMPermissions.permission_name == permission_name)
        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission: {permission_name} does not exist.",
            )

        statement = select(IAMGroups).filter(IAMGroups.group_name == group_name)
        group = session.exec(statement).scalar()
        statement = select(IAMPermissions).filter(IAMPermissions.permission_name == permission_name)
        permission = session.exec(statement).scalar()
        statement = select(IAMGroupPermissionsMap).filter(
            IAMGroupPermissionsMap.group_id == group.id,
            IAMGroupPermissionsMap.permission_id == permission.id,
        )

        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} does not have permission: {permission_name}.",
            )

        group_permission_map = session.exec(statement).scalar()
        session.delete(group_permission_map)
        return {
            "detail": f"Permission: {permission_name} removed from group: {group_name} successfully."
        }

    @staticmethod
    def remove_role_from_member(role_name: str, member_id: int, session: Session):
        """Remove a role from a member."""

        statement = select(IAMRoles).filter(IAMRoles.role_name == role_name)
        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} does not exist.",
            )

        statement = select(Registration).filter(Registration.registration_id == member_id)
        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Member with id: {member_id} does not exist.",
            )

        statement = select(IAMRoles).filter(IAMRoles.role_name == role_name)
        role = session.exec(statement).scalar()
        statement = select(IAMUserRolesMap).filter(
            IAMUserRolesMap.role_id == role.id,
            IAMUserRolesMap.registration_id == member_id,
        )

        statement = select(IAMUserRolesMap).filter(
            IAMUserRolesMap.role_id == role.id,
            IAMUserRolesMap.registration_id == member_id,
        )
        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} not assigned to member with id: {member_id}.",
            )

        role_map = session.exec(statement).scalar()

        session.delete(role_map)
        return {
            "detail": f"Role: {role_name} removed from member with id: {member_id} successfully."
        }

    @staticmethod
    def remove_group_from_member(group_name: str, member_id: int, session: Session):
        """Remove a group from a member."""

        statement = select(IAMGroups).filter(IAMGroups.group_name == group_name)
        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} does not exist.",
            )

        statement = select(Registration).filter(Registration.registration_id == member_id)
        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Member with id: {member_id} does not exist.",
            )

        statement = select(IAMGroups).filter(IAMGroups.group_name == group_name)
        group = session.exec(statement).scalar()
        statement = select(IAMUserGroupsMap).filter(
            IAMUserGroupsMap.group_id == group.id,
            IAMUserGroupsMap.registration_id == member_id,
        )

        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} not assigned to member with id: {member_id}.",
            )

        group_map = session.exec(statement).scalar()

        session.delete(group_map)
        return {
            "detail": f"Group: {group_name} removed from member with id: {member_id} successfully."
        }

    @staticmethod
    def delete_role(role_name: str, session: Session):
        """Delete a role by role name."""

        statment = select(IAMRoles).filter(IAMRoles.role_name == role_name)
        if not session.exec(statment).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} does not exist.",
            )

        statement = select(IAMRoles).filter(IAMRoles.role_name == role_name)
        role = session.exec(statement).scalar()
        session.delete(role)
        return {"detail": f"Role: {role_name} deleted successfully."}

    @staticmethod
    def delete_group(group_name: str, session: Session):
        """Delete a group by group name."""

        statement = select(IAMGroups).filter(IAMGroups.group_name == group_name)
        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} does not exist.",
            )

        statement = select(IAMGroups).filter(IAMGroups.group_name == group_name)
        group = session.exec(statement).scalar()
        session.delete(group)
        return {"detail": f"Group: {group_name} deleted successfully."}

    @staticmethod
    def delete_permission(permission_name: str, session: Session):
        """Delete a permission by permission name."""

        statement = select(IAMPermissions).filter(IAMPermissions.permission_name == permission_name)
        if not session.exec(statement).scalar():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission: {permission_name} does not exist.",
            )

        statement = select(IAMPermissions).filter(IAMPermissions.permission_name == permission_name)
        permission = session.exec(statement).scalar()
        session.delete(permission)
        return {"detail": f"Permission: {permission_name} deleted successfully."}

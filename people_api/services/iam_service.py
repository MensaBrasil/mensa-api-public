"""This module contains the service class for IAM."""

from fastapi import HTTPException, status
from sqlmodel import Session, col, select

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
    def get_member_by_id(member_id: int, session: Session) -> Registration:
        """Get member by member id."""
        return session.exec(
            select(Registration).where(col(Registration.registration_id) == member_id)
        ).first()  # type: ignore

    @staticmethod
    def get_role_by_role_name(role_name: str, session: Session) -> IAMRoles:
        """Get role by role name."""
        return session.exec(select(IAMRoles).filter(col(IAMRoles.role_name) == role_name)).first()  # type: ignore

    @staticmethod
    def get_role_id_by_role_name(role_name: str, session: Session) -> IAMRoles:
        """Get role by role name."""
        return session.exec(select(IAMRoles).filter(col(IAMRoles.role_name) == role_name)).first()  # type: ignore

    @staticmethod
    def get_group_by_group_name(group_name: str, session: Session) -> IAMGroups:
        """Get group by group name."""
        return session.exec(
            select(IAMGroups).filter(col(IAMGroups.group_name) == group_name)
        ).first()  # type: ignore

    @staticmethod
    def get_group_id_by_group_name(group_name: str, session: Session) -> IAMGroups:
        """Get group by group name."""
        return session.exec(
            select(IAMGroups).filter(col(IAMGroups.group_name) == group_name)
        ).first()  # type: ignore

    @staticmethod
    def get_permission_by_permission_name(permission_name: str, session: Session) -> IAMPermissions:
        """Get permission by permission name."""
        return session.exec(
            select(IAMPermissions).filter(col(IAMPermissions.permission_name) == permission_name)
        ).first()  # type: ignore

    @staticmethod
    def get_permission_id_by_permission_name(
        permission_name: str, session: Session
    ) -> IAMPermissions:
        """Get permission by permission name."""
        return session.exec(
            select(IAMPermissions).filter(col(IAMPermissions.permission_name) == permission_name)
        ).first()  # type: ignore

    @staticmethod
    def get_member_roles(token_data: dict, session: Session):
        """Get roles for a member by member id."""

        registration_id = MemberRepository.getMBByEmail(token_data["email"], session)

        statement = (
            select(col(col(IAMRoles.role_name)))
            .select_from(IAMUserRolesMap)
            .join(IAMRoles, col(col(IAMUserRolesMap.role_id)) == col(col(IAMRoles.id)))
            .where(col(IAMUserRolesMap.registration_id) == registration_id)
        )
        roles = session.exec(statement).all()
        if roles:
            return roles
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No roles found for member with id {registration_id}.",
            )

    @staticmethod
    def get_member_groups(token_data: dict, session: Session):
        """Get groups for a member by member id."""

        registration_id = MemberRepository.getMBByEmail(token_data["email"], session)

        statement = (
            select(col(IAMGroups.group_name))
            .select_from(IAMUserGroupsMap)
            .join(IAMGroups, col(col(IAMUserGroupsMap.group_id)) == col(col(IAMGroups.id)))
            .where(col(IAMUserGroupsMap.registration_id) == registration_id)
        )
        groups = session.exec(statement).all()
        if groups:
            return groups
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No groups found for member with id {registration_id}.",
            )

    @staticmethod
    def get_role_permissions_by_role_name(role_name: str, session: Session):
        """Get permissions for a role by role name."""

        if not IamService.get_role_by_role_name(role_name, session):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} does not exist.",
            )

        statement = (
            select(col(IAMPermissions.permission_name))
            .select_from(IAMRolePermissionsMap)
            .join(
                IAMPermissions,
                col(IAMRolePermissionsMap.permission_id) == col(col(IAMPermissions.id)),
            )
            .join(IAMRoles, col(IAMRolePermissionsMap.role_id) == col(IAMRoles.id))
            .where(col(IAMRoles.role_name) == role_name)
        )
        permissions = session.exec(statement).all()
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

        if not IamService.get_group_by_group_name(group_name, session):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} does not exist.",
            )

        statement = (
            select(col(IAMPermissions.permission_name))
            .select_from(IAMGroupPermissionsMap)
            .join(
                IAMPermissions,
                col(IAMGroupPermissionsMap.permission_id) == col(IAMPermissions.id),
            )
            .join(IAMGroups, col(IAMGroupPermissionsMap.group_id) == col(IAMGroups.id))
            .where(col(IAMGroups.group_name) == group_name)
        )
        permissions = session.exec(statement).all()
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

        if not IamService.get_role_by_role_name(role_name, session):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} does not exist.",
            )

        statement = (
            select(Registration.name, col(IAMUserRolesMap.registration_id))
            .join(IAMRoles, col(IAMUserRolesMap.role_id) == col(IAMRoles.id))
            .join(
                Registration,
                col(IAMUserRolesMap.registration_id) == col(Registration.registration_id),
            )
            .where(col(IAMRoles.role_name) == role_name)
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

        if not IamService.get_group_by_group_name(group_name, session):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} does not exist.",
            )

        statement = (
            select(Registration.name, col(IAMUserGroupsMap.registration_id))
            .join(IAMGroups, col(IAMUserGroupsMap.group_id) == col(IAMGroups.id))
            .join(
                Registration,
                col(IAMUserGroupsMap.registration_id) == col(Registration.registration_id),
            )
            .where(col(IAMGroups.group_name) == group_name)
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

        if IamService.get_role_by_role_name(role_name, session):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role: {role_name} already exists.",
            )

        try:
            new_role = IAMRoles(role_name=role_name, role_description=role_description)
            session.add(new_role)
            return {"detail": f"Role: {new_role.role_name} created successfully."}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}"
            ) from e

    @staticmethod
    def create_group(group_name: str, group_description: str, session: Session):
        """Create a new group."""

        if IamService.get_group_by_group_name(group_name, session):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Group: {group_name} already exists.",
            )
        try:
            new_group = IAMGroups(group_name=group_name, group_description=group_description)
            session.add(new_group)
            return {"detail": f"Group: {new_group.group_name} created successfully."}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}"
            ) from e

    @staticmethod
    def create_permission(permission_name: str, permission_description: str, session: Session):
        """Create a new permission."""

        if IamService.get_permission_by_permission_name(permission_name, session):
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}"
            ) from e

    @staticmethod
    def edit_role_by_name(
        role_name: str,
        new_role_name: str,
        session: Session,
        new_role_description: str | None = None,
    ):
        """Edit a role by role name."""

        role = IamService.get_role_by_role_name(role_name, session)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} does not exist.",
            )

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
        new_group_description: str | None = None,
    ):
        """Edit a group by group name."""

        group = IamService.get_group_by_group_name(group_name, session)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} does not exist.",
            )

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
        new_permission_description: str | None = None,
    ):
        """Edit a permission by permission name."""

        permission = IamService.get_permission_by_permission_name(permission_name, session)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission: {permission_name} does not exist.",
            )

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

        role = IamService.get_role_by_role_name(role_name, session)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} does not exist.",
            )

        permission = IamService.get_permission_by_permission_name(permission_name, session)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission: {permission_name} does not exist.",
            )

        role_id = IamService.get_role_id_by_role_name(role_name, session).id
        permission_id = IamService.get_permission_id_by_permission_name(permission_name, session).id
        statement = select(IAMRolePermissionsMap).filter(
            col(IAMRolePermissionsMap.role_id) == role_id,
            col(IAMRolePermissionsMap.permission_id) == permission_id,
        )
        role_already_has_permission = session.exec(statement).first()

        if role_already_has_permission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role: {role_name} already has permission: {permission_name}.",
            )

        try:
            role_permission_map = IAMRolePermissionsMap(
                role_id=role.id, permission_id=permission.id
            )
            session.add(role_permission_map)
            return {
                "detail": f"Permission: {permission_name} added to role: {role_name} successfully."
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}"
            ) from e

    @staticmethod
    def add_permission_to_group(group_name: str, permission_name: str, session: Session):
        """Add a permission to a group."""

        group = IamService.get_group_by_group_name(group_name, session)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} does not exist.",
            )

        permission = IamService.get_permission_by_permission_name(permission_name, session)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission: {permission_name} does not exist.",
            )

        group_id = IamService.get_group_id_by_group_name(group_name, session).id
        permission_id = IamService.get_permission_id_by_permission_name(permission_name, session).id

        group_already_has_permission = session.exec(
            select(IAMGroupPermissionsMap).filter(
                col(IAMGroupPermissionsMap.group_id) == group_id,
                col(IAMGroupPermissionsMap.permission_id) == permission_id,
            )
        ).first()

        if group_already_has_permission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Group: {group_name} already has permission: {permission_name}.",
            )
        try:
            group_permission_map = IAMGroupPermissionsMap(
                group_id=group.id, permission_id=permission.id
            )
            session.add(group_permission_map)
            return {
                "detail": f"Permission: {permission_name} added to group: {group_name} successfully."
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}"
            ) from e

    @staticmethod
    def add_role_to_member(role_name: str, member_id: int, session: Session):
        """Add a role to a member."""

        role = IamService.get_role_by_role_name(role_name, session)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} does not exist.",
            )

        role_id = IamService.get_role_id_by_role_name(role_name, session).id

        check_role_assigned = session.exec(
            select(IAMUserRolesMap).filter(
                col(IAMUserRolesMap.role_id) == role_id,
                col(IAMUserRolesMap.registration_id) == member_id,
            )
        ).first()

        if check_role_assigned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role: {role_name} already assigned to member with id: {member_id}.",
            )

        try:
            role_map = IAMUserRolesMap(role_id=role.id, registration_id=member_id)
            session.add(role_map)
            return {
                "detail": f"Role: {role_name} added to member with id: {member_id} successfully."
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}"
            ) from e

    @staticmethod
    def add_group_to_member(group_name: str, member_id: int, session: Session):
        """Add a group to a member."""

        group = IamService.get_group_by_group_name(group_name, session)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} does not exist.",
            )

        group_id = IamService.get_group_id_by_group_name(group_name, session).id
        check_group_assigned = session.exec(
            select(IAMUserGroupsMap).filter(
                col(IAMUserGroupsMap.group_id) == group_id,
                col(IAMUserGroupsMap.registration_id) == member_id,
            )
        ).first()

        if check_group_assigned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Group: {group_name} already assigned to member with id: {member_id}.",
            )

        try:
            group_map = IAMUserGroupsMap(group_id=group.id, registration_id=member_id)
            session.add(group_map)
            return {
                "detail": f"Group: {group_name} added to member with id: {member_id} successfully."
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}"
            ) from e

    @staticmethod
    def remove_permission_from_role(role_name: str, permission_name: str, session: Session):
        """Remove a permission from a role."""

        role = IamService.get_role_by_role_name(role_name, session)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} does not exist.",
            )

        permission = IamService.get_permission_by_permission_name(permission_name, session)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission: {permission_name} does not exist.",
            )

        role_permission_map = session.exec(
            select(IAMRolePermissionsMap).filter(
                col(IAMRolePermissionsMap.role_id) == role.id,
                col(IAMRolePermissionsMap.permission_id) == permission.id,
            )
        ).first()

        if not role_permission_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} does not have permission: {permission_name}.",
            )

        session.delete(role_permission_map)
        return {
            "detail": f"Permission: {permission_name} removed from role: {role_name} successfully."
        }

    @staticmethod
    def remove_permission_from_group(group_name: str, permission_name: str, session: Session):
        """Remove a permission from a group."""

        group = IamService.get_group_by_group_name(group_name, session)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} does not exist.",
            )

        permission = IamService.get_permission_by_permission_name(permission_name, session)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission: {permission_name} does not exist.",
            )

        group_permission_map = session.exec(
            select(IAMGroupPermissionsMap).filter(
                col(IAMGroupPermissionsMap.group_id) == group.id,
                col(IAMGroupPermissionsMap.permission_id) == permission.id,
            )
        ).first()

        if not group_permission_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} does not have permission: {permission_name}.",
            )

        session.delete(group_permission_map)
        return {
            "detail": f"Permission: {permission_name} removed from group: {group_name} successfully."
        }

    @staticmethod
    def remove_role_from_member(role_name: str, member_id: int, session: Session):
        """Remove a role from a member."""

        role = IamService.get_role_by_role_name(role_name, session)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} does not exist.",
            )

        member = IamService.get_member_by_id(member_id, session)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Member with id: {member_id} does not exist.",
            )

        role_member_map = session.exec(
            select(IAMUserRolesMap).filter(
                col(IAMUserRolesMap.role_id) == role.id,
                col(IAMUserRolesMap.registration_id) == member_id,
            )
        ).first()
        if not role_member_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} not assigned to member with id: {member_id}.",
            )

        session.delete(role_member_map)
        return {
            "detail": f"Role: {role_name} removed from member with id: {member_id} successfully."
        }

    @staticmethod
    def remove_group_from_member(group_name: str, member_id: int, session: Session):
        """Remove a group from a member."""

        group = IamService.get_group_by_group_name(group_name, session)

        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} does not exist.",
            )

        member = IamService.get_member_by_id(member_id, session)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Member with id: {member_id} does not exist.",
            )

        group_member_map = session.exec(
            select(IAMUserGroupsMap).filter(
                col(IAMUserGroupsMap.group_id) == group.id,
                col(IAMUserGroupsMap.registration_id) == member_id,
            )
        ).first()
        if not group_member_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} not assigned to member with id: {member_id}.",
            )
        session.delete(group_member_map)
        return {
            "detail": f"Group: {group_name} removed from member with id: {member_id} successfully."
        }

    @staticmethod
    def delete_role(role_name: str, session: Session):
        """Delete a role by role name."""

        role = IamService.get_role_by_role_name(role_name, session)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} does not exist.",
            )

        session.delete(role)
        return {"detail": f"Role: {role_name} deleted successfully."}

    @staticmethod
    def delete_group(group_name: str, session: Session):
        """Delete a group by group name."""

        group = IamService.get_group_by_group_name(group_name, session)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} does not exist.",
            )

        session.delete(group)
        return {"detail": f"Group: {group_name} deleted successfully."}

    @staticmethod
    def delete_permission(permission_name: str, session: Session):
        """Delete a permission by permission name."""

        permission = IamService.get_permission_by_permission_name(permission_name, session)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission: {permission_name} does not exist.",
            )

        session.delete(permission)
        return {"detail": f"Permission: {permission_name} deleted successfully."}

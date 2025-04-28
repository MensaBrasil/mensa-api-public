"""This module contains the service class for IAM."""

from fastapi import HTTPException, status
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession

from people_api.schemas import UserToken

from ..database.models import (
    Emails,
    IAMGroupPermissionsMap,
    IAMGroups,
    IAMPermissions,
    IAMRolePermissionsMap,
    IAMRoles,
    IAMUserGroupsMap,
    IAMUserRolesMap,
    Registration,
)


class IamService:
    """Service class for IAM."""

    @staticmethod
    async def get_member_id_by_email(email: str, session: AsyncSession) -> int:
        """Get member id by email."""
        result = (await session.exec(Emails.select_registration_id_by_email(email))).first()
        return result

    @staticmethod
    async def get_member_by_id(member_id: int, session: AsyncSession) -> Registration:
        """Get member by member id."""
        return (await session.exec(Registration.select_stmt_by_id(member_id))).first()

    @staticmethod
    async def get_role_by_role_name(role_name: str, session: AsyncSession) -> IAMRoles:
        """Get role by role name."""
        return (await session.exec(IAMRoles.select_by_role_name(role_name))).first()

    @staticmethod
    async def get_role_id_by_role_name(role_name: str, session: AsyncSession) -> IAMRoles:
        """Get role by role name."""
        return (await session.exec(IAMRoles.select_by_role_name(role_name))).first()

    @staticmethod
    async def get_group_by_group_name(group_name: str, session: AsyncSession) -> IAMGroups:
        """Get group by group name."""
        return (await session.exec(IAMGroups.select_by_group_name(group_name))).first()

    @staticmethod
    async def get_group_id_by_group_name(group_name: str, session: AsyncSession) -> IAMGroups:
        """Get group by group name."""
        return (await session.exec(IAMGroups.select_by_group_name(group_name))).first()

    @staticmethod
    async def get_permission_by_permission_name(
        permission_name: str, session: AsyncSession
    ) -> IAMPermissions:
        """Get permission by permission name."""
        return (
            await session.exec(IAMPermissions.select_by_permission_name(permission_name))
        ).first()

    @staticmethod
    async def get_permission_id_by_permission_name(
        permission_name: str, session: AsyncSession
    ) -> IAMPermissions:
        """Get permission by permission name."""
        return (
            await session.exec(IAMPermissions.select_by_permission_name(permission_name))
        ).first()

    @staticmethod
    async def get_member_roles(token_data: UserToken, session: AsyncSession):
        """Get roles for a member by member id."""
        roles = (
            await session.exec(
                IAMUserRolesMap.select_role_names_by_registration_id(token_data.registration_id)
            )
        ).all()
        return roles or []

    @staticmethod
    async def get_member_groups(token_data: UserToken, session: AsyncSession):
        """Get groups for a member by member id."""
        groups = (
            await session.exec(
                IAMUserGroupsMap.select_group_names_by_registration_id(token_data.registration_id)
            )
        ).all()
        return groups or []

    @staticmethod
    async def get_member_permissions(token_data: UserToken, session: AsyncSession) -> list[str]:
        """Get permissions for a member by member id."""
        role_permissions_stmt = IAMPermissions.select_role_permissions_by_registration_id(
            token_data.registration_id
        )
        group_permissions_stmt = IAMPermissions.select_group_permissions_by_registration_id(
            token_data.registration_id
        )

        role_permissions = (await session.exec(role_permissions_stmt)).all()
        group_permissions = (await session.exec(group_permissions_stmt)).all()

        all_permissions = set(role_permissions + group_permissions)
        sorted_permissions = sorted(all_permissions)

        if sorted_permissions:
            return sorted_permissions
        else:
            return []

    @staticmethod
    def get_all_permissions_for_member(registration_id: int, session: Session) -> list[str]:
        """Get all permissions for a member by member id."""
        role_permissions_stmt = IAMPermissions.select_role_permissions_by_registration_id(
            registration_id
        )
        group_permissions_stmt = IAMPermissions.select_group_permissions_by_registration_id(
            registration_id
        )

        role_permissions = session.exec(role_permissions_stmt).all()
        group_permissions = session.exec(group_permissions_stmt).all()

        all_permissions = set(role_permissions + group_permissions)
        sorted_permissions = sorted(all_permissions)

        if sorted_permissions:
            return sorted_permissions
        return []

    @staticmethod
    async def get_role_permissions_by_role_name(role_name: str, session: AsyncSession):
        """Get permissions for a role by role name."""
        if not await IamService.get_role_by_role_name(role_name, session):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} does not exist.",
            )

        stmt = IAMPermissions.get_role_permissions_by_role_name(role_name)
        permissions = (await session.exec(stmt)).all()
        return permissions or []

    @staticmethod
    async def get_group_permissions_by_group_name(group_name: str, session: AsyncSession):
        """Get permissions for a group by group name."""
        if not await IamService.get_group_by_group_name(group_name, session):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} does not exist.",
            )

        stmt = IAMPermissions.get_group_permissions_by_group_name(group_name)
        permissions = (await session.exec(stmt)).all()
        return permissions or []

    @staticmethod
    async def get_members_by_role_name(role_name: str, session: AsyncSession):
        """Get members by role."""
        if not await IamService.get_role_by_role_name(role_name, session):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} does not exist.",
            )

        stmt = IAMUserRolesMap.select_members_by_role_name(role_name)
        results = await session.exec(stmt)
        members = [[row[0], row[1]] for row in results.all()]
        return members or []

    @staticmethod
    async def get_members_by_group_name(group_name: str, session: AsyncSession):
        """Get members by group."""
        if not await IamService.get_group_by_group_name(group_name, session):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} does not exist.",
            )

        stmt = IAMUserGroupsMap.select_members_by_group_name(group_name)
        results = await session.exec(stmt)
        members = [[row[0], row[1]] for row in results.all()]
        return members or []

    @staticmethod
    async def create_role(role_name: str, role_description: str, session: AsyncSession):
        """Create a new role."""
        if await IamService.get_role_by_role_name(role_name, session):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role: {role_name} already exists.",
            )

        new_role = IAMRoles(role_name=role_name, role_description=role_description)
        session.add(new_role)
        return {"detail": f"Role: {new_role.role_name} created successfully."}

    @staticmethod
    async def create_group(group_name: str, group_description: str, session: AsyncSession):
        """Create a new group."""

        if await IamService.get_group_by_group_name(group_name, session):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Group: {group_name} already exists.",
            )
        new_group = IAMGroups(group_name=group_name, group_description=group_description)
        session.add(new_group)
        return {"detail": f"Group: {new_group.group_name} created successfully."}

    @staticmethod
    async def create_permission(
        permission_name: str, permission_description: str, session: AsyncSession
    ):
        """Create a new permission."""

        if await IamService.get_permission_by_permission_name(permission_name, session):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Permission: {permission_name} already exists.",
            )
        new_permission = IAMPermissions(
            permission_name=permission_name,
            permission_description=permission_description,
        )
        session.add(new_permission)
        return {"detail": f"Permission: {new_permission.permission_name} created successfully."}

    @staticmethod
    async def edit_role_by_name(
        role_name: str,
        new_role_name: str,
        session: AsyncSession,
        new_role_description: str | None = None,
    ):
        """Edit a role by role name."""

        role = await IamService.get_role_by_role_name(role_name, session)
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
    async def edit_group_by_name(
        group_name: str,
        new_group_name: str,
        session: AsyncSession,
        new_group_description: str | None = None,
    ):
        """Edit a group by group name."""
        group = await IamService.get_group_by_group_name(group_name, session)
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
    async def edit_permission_by_name(
        permission_name: str,
        new_permission_name: str,
        session: AsyncSession,
        new_permission_description: str | None = None,
    ):
        """Edit a permission by permission name."""
        permission = await IamService.get_permission_by_permission_name(permission_name, session)
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
    async def add_permission_to_role(role_name: str, permission_name: str, session: AsyncSession):
        """Add a permission to a role."""
        role = await IamService.get_role_by_role_name(role_name, session)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} does not exist.",
            )
        permission = await IamService.get_permission_by_permission_name(permission_name, session)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission: {permission_name} does not exist.",
            )
        role_id = (await IamService.get_role_id_by_role_name(role_name, session)).id
        permission_id = (
            await IamService.get_permission_id_by_permission_name(permission_name, session)
        ).id
        exists = (
            await session.exec(
                IAMRolePermissionsMap.select_by_role_and_permission(role_id, permission_id)
            )
        ).first()
        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role: {role_name} already has permission: {permission_name}.",
            )
        role_permission_map = IAMRolePermissionsMap(role_id=role.id, permission_id=permission.id)
        session.add(role_permission_map)
        return {"detail": f"Permission: {permission_name} added to role: {role_name} successfully."}

    @staticmethod
    async def add_permission_to_group(group_name: str, permission_name: str, session: AsyncSession):
        """Add a permission to a group."""
        group = await IamService.get_group_by_group_name(group_name, session)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} does not exist.",
            )
        permission = await IamService.get_permission_by_permission_name(permission_name, session)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission: {permission_name} does not exist.",
            )
        group_id = (await IamService.get_group_id_by_group_name(group_name, session)).id
        permission_id = (
            await IamService.get_permission_id_by_permission_name(permission_name, session)
        ).id
        exists = (
            await session.exec(
                IAMGroupPermissionsMap.select_by_group_and_permission(group_id, permission_id)
            )
        ).first()
        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Group: {group_name} already has permission: {permission_name}.",
            )
        group_permission_map = IAMGroupPermissionsMap(
            group_id=group.id, permission_id=permission.id
        )
        session.add(group_permission_map)
        return {
            "detail": f"Permission: {permission_name} added to group: {group_name} successfully."
        }

    @staticmethod
    async def add_role_to_member(role_name: str, member_id: int, session: AsyncSession):
        """Add a role to a member."""
        role = await IamService.get_role_by_role_name(role_name, session)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} does not exist.",
            )
        role_id = (await IamService.get_role_id_by_role_name(role_name, session)).id
        exists = (
            await session.exec(IAMUserRolesMap.select_by_role_and_member(role_id, member_id))
        ).first()
        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role: {role_name} already assigned to member with id: {member_id}.",
            )
        role_map = IAMUserRolesMap(role_id=role.id, registration_id=member_id)
        session.add(role_map)
        return {"detail": f"Role: {role_name} added to member with id: {member_id} successfully."}

    @staticmethod
    async def add_group_to_member(group_name: str, member_id: int, session: AsyncSession):
        """Add a group to a member."""
        group = await IamService.get_group_by_group_name(group_name, session)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} does not exist.",
            )
        group_id = (await IamService.get_group_id_by_group_name(group_name, session)).id
        exists = (
            await session.exec(IAMUserGroupsMap.select_by_group_and_member(group_id, member_id))
        ).first()
        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Group: {group_name} already assigned to member with id: {member_id}.",
            )
        group_map = IAMUserGroupsMap(group_id=group.id, registration_id=member_id)
        session.add(group_map)
        return {"detail": f"Group: {group_name} added to member with id: {member_id} successfully."}

    @staticmethod
    async def remove_permission_from_role(
        role_name: str, permission_name: str, session: AsyncSession
    ):
        """Remove a permission from a role."""
        role = await IamService.get_role_by_role_name(role_name, session)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} does not exist.",
            )
        permission = await IamService.get_permission_by_permission_name(permission_name, session)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission: {permission_name} does not exist.",
            )
        role_permission_map = (
            await session.exec(
                IAMRolePermissionsMap.select_by_role_and_permission(role.id, permission.id)
            )
        ).first()
        if not role_permission_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} does not have permission: {permission_name}.",
            )
        await session.delete(role_permission_map)
        return {
            "detail": f"Permission: {permission_name} removed from role: {role_name} successfully."
        }

    @staticmethod
    async def remove_permission_from_group(
        group_name: str, permission_name: str, session: AsyncSession
    ):
        """Remove a permission from a group."""
        group = await IamService.get_group_by_group_name(group_name, session)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} does not exist.",
            )
        permission = await IamService.get_permission_by_permission_name(permission_name, session)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission: {permission_name} does not exist.",
            )

        group_permission_map = (
            await session.exec(
                IAMGroupPermissionsMap.select_by_group_and_permission(group.id, permission.id)
            )
        ).first()
        if not group_permission_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} does not have permission: {permission_name}.",
            )
        await session.delete(group_permission_map)
        return {
            "detail": f"Permission: {permission_name} removed from group: {group_name} successfully."
        }

    @staticmethod
    async def remove_role_from_member(role_name: str, member_id: int, session: AsyncSession):
        """Remove a role from a member."""
        role = await IamService.get_role_by_role_name(role_name, session)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} does not exist.",
            )
        member = await IamService.get_member_by_id(member_id, session)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Member with id: {member_id} does not exist.",
            )
        role_member_map = (
            await session.exec(IAMUserRolesMap.select_by_role_and_member(role.id, member_id))
        ).first()
        if not role_member_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} not assigned to member with id: {member_id}.",
            )
        await session.delete(role_member_map)
        return {
            "detail": f"Role: {role_name} removed from member with id: {member_id} successfully."
        }

    @staticmethod
    async def remove_group_from_member(group_name: str, member_id: int, session: AsyncSession):
        """Remove a group from a member."""
        group = await IamService.get_group_by_group_name(group_name, session)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} does not exist.",
            )
        member = await IamService.get_member_by_id(member_id, session)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Member with id: {member_id} does not exist.",
            )
        group_member_map = (
            await session.exec(IAMUserGroupsMap.select_by_group_and_member(group.id, member_id))
        ).first()
        if not group_member_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} not assigned to member with id: {member_id}.",
            )
        await session.delete(group_member_map)
        return {
            "detail": f"Group: {group_name} removed from member with id: {member_id} successfully."
        }

    @staticmethod
    async def delete_role(role_name: str, session: AsyncSession):
        """Delete a role by role name."""
        role = await IamService.get_role_by_role_name(role_name, session)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role: {role_name} does not exist.",
            )
        await session.delete(role)
        return {"detail": f"Role: {role_name} deleted successfully."}

    @staticmethod
    async def delete_group(group_name: str, session: AsyncSession):
        """Delete a group by group name."""
        group = await IamService.get_group_by_group_name(group_name, session)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group: {group_name} does not exist.",
            )
        await session.delete(group)
        return {"detail": f"Group: {group_name} deleted successfully."}

    @staticmethod
    async def delete_permission(permission_name: str, session: AsyncSession):
        """Delete a permission by permission name."""
        permission = await IamService.get_permission_by_permission_name(permission_name, session)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission: {permission_name} does not exist.",
            )
        await session.delete(permission)
        return {"detail": f"Permission: {permission_name} deleted successfully."}

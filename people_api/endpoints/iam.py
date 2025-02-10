"""Endpoints for managing roles and groups."""

from fastapi import APIRouter, Depends, status

from ..auth import verify_firebase_token
from ..database.models.iam_model import (
    AddGroupToMember,
    AddPermissionToGroup,
    AddPermissionToRole,
    AddRoleToMember,
    CreateGroup,
    CreatePermission,
    CreateRole,
    DeleteGroup,
    DeletePermission,
    DeleteRole,
    RemoveGroupFromMember,
    RemovePermissionFromGroup,
    RemovePermissionFromRole,
    RemoveRoleFromMember,
    UpdateGroup,
    UpdatePermission,
    UpdateRole,
)
from ..dbs import AsyncSessionsTuple, get_async_sessions
from ..services import IamService

iam_router = APIRouter(tags=["IAM"], prefix="/iam", dependencies=[Depends(verify_firebase_token)])

# POST requests


@iam_router.post("/create_role/", status_code=status.HTTP_201_CREATED, tags=["roles"])
async def _create_role(
    role: CreateRole,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Create a new role"""
    return await IamService.create_role(
        role_name=role.role_name,
        role_description=role.role_description,
        session=sessions.rw,
    )


@iam_router.post("/create_group/", status_code=status.HTTP_201_CREATED, tags=["groups"])
async def _create_group(
    group: CreateGroup,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Create a new group"""
    return await IamService.create_group(
        group_name=group.group_name,
        group_description=group.group_description,
        session=sessions.rw,
    )


@iam_router.post(
    "/create_permission/",
    status_code=status.HTTP_201_CREATED,
    tags=["permissions"],
)
async def _create_permission(
    permission: CreatePermission,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Create a new permission"""
    return await IamService.create_permission(
        permission_name=permission.permission_name,
        permission_description=permission.permission_description,
        session=sessions.rw,
    )


@iam_router.post(
    "/add_role_to_member/",
    status_code=status.HTTP_201_CREATED,
    tags=["roles"],
)
async def _add_role_to_member(
    role: AddRoleToMember,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Add role to member"""
    return await IamService.add_role_to_member(
        role_name=role.role_name, member_id=role.member_id, session=sessions.rw
    )


@iam_router.post(
    "/add_group_to_member/",
    status_code=status.HTTP_201_CREATED,
    tags=["groups"],
)
async def _add_group_to_member(
    group: AddGroupToMember,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Add group to member"""
    return await IamService.add_group_to_member(
        group_name=group.group_name, member_id=group.member_id, session=sessions.rw
    )


@iam_router.post(
    "/add_permission_to_role/",
    status_code=status.HTTP_201_CREATED,
    tags=["roles"],
)
async def _add_permission_to_role(
    data: AddPermissionToRole,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Add permission to role"""
    return await IamService.add_permission_to_role(
        role_name=data.role_name,
        permission_name=data.permission_name,
        session=sessions.rw,
    )


@iam_router.post(
    "/add_permission_to_group/",
    status_code=status.HTTP_201_CREATED,
    tags=["groups"],
)
async def _add_permission_to_group(
    data: AddPermissionToGroup,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Add permission to group"""
    return await IamService.add_permission_to_group(
        group_name=data.group_name,
        permission_name=data.permission_name,
        session=sessions.rw,
    )


# GET requests


@iam_router.get("/roles/", status_code=status.HTTP_200_OK, tags=["roles"])
async def _get_roles(
    token_data=Depends(verify_firebase_token),
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Get roles for member"""
    return await IamService.get_member_roles(token_data=token_data, session=sessions.rw)


@iam_router.get("/groups/", status_code=status.HTTP_200_OK, tags=["groups"])
async def _get_groups(
    token_data=Depends(verify_firebase_token),
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Get groups for member"""
    return await IamService.get_member_groups(token_data=token_data, session=sessions.rw)


@iam_router.get(
    "/members/role/",
    status_code=status.HTTP_200_OK,
    tags=["roles"],
)
async def _get_members_with_role(
    role_name: str,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Get members with specific role"""
    return await IamService.get_members_by_role_name(role_name=role_name, session=sessions.rw)


@iam_router.get(
    "/members/group/",
    status_code=status.HTTP_200_OK,
    tags=["groups"],
)
async def _get_members_in_group(
    group_name: str,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Get members in specific group"""
    return await IamService.get_members_by_group_name(group_name=group_name, session=sessions.rw)


@iam_router.get(
    "/role_permissions/",
    status_code=status.HTTP_200_OK,
    tags=["roles"],
)
async def _get_role_permissions(
    role_name: str,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Get permissions for role"""
    return await IamService.get_role_permissions_by_role_name(
        role_name=role_name, session=sessions.rw
    )


@iam_router.get(
    "/group_permissions/",
    status_code=status.HTTP_200_OK,
    tags=["groups"],
)
async def _get_group_permissions(
    group_name: str,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Get permissions for group"""
    return await IamService.get_group_permissions_by_group_name(
        group_name=group_name, session=sessions.rw
    )


# PATCH requests


@iam_router.patch("/update_role/", status_code=status.HTTP_200_OK, tags=["roles"])
async def _update_role(
    update_role: UpdateRole,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Update role"""
    return await IamService.edit_role_by_name(
        role_name=update_role.role_name,
        new_role_name=update_role.new_role_name,
        session=sessions.rw,
        new_role_description=update_role.new_role_description,
    )


@iam_router.patch("/update_group/", status_code=status.HTTP_200_OK, tags=["groups"])
async def _update_group(
    update_group: UpdateGroup,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Update group"""
    return await IamService.edit_group_by_name(
        group_name=update_group.group_name,
        new_group_name=update_group.new_group_name,
        session=sessions.rw,
        new_group_description=update_group.new_group_description,
    )


@iam_router.patch(
    "/update_permission/",
    status_code=status.HTTP_200_OK,
    tags=["permissions"],
)
async def _update_permission(
    data: UpdatePermission,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Update permission"""
    return await IamService.edit_permission_by_name(
        permission_name=data.permission_name,
        new_permission_name=data.new_permission_name,
        session=sessions.rw,
        new_permission_description=data.new_permission_description,
    )


# DELETE requests


@iam_router.delete(
    "/remove_role_from_member/",
    status_code=status.HTTP_200_OK,
    tags=["roles"],
)
async def _remove_role_from_member(
    request: RemoveRoleFromMember,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Remove role from member"""
    return await IamService.remove_role_from_member(
        role_name=request.role_name, member_id=request.member_id, session=sessions.rw
    )


@iam_router.delete(
    "/remove_group_from_member/",
    status_code=status.HTTP_200_OK,
    tags=["groups"],
)
async def _remove_group_from_member(
    request: RemoveGroupFromMember,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Remove group from member"""
    return await IamService.remove_group_from_member(
        group_name=request.group_name, member_id=request.member_id, session=sessions.rw
    )


@iam_router.delete(
    "/remove_permission_from_role/",
    status_code=status.HTTP_200_OK,
    tags=["roles"],
)
async def _remove_permission_from_role(
    request: RemovePermissionFromRole,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Remove permission from role"""
    return await IamService.remove_permission_from_role(
        role_name=request.role_name,
        permission_name=request.permission_name,
        session=sessions.rw,
    )


@iam_router.delete(
    "/remove_permission_from_group/",
    status_code=status.HTTP_200_OK,
    tags=["groups"],
)
async def _remove_permission_from_group(
    request: RemovePermissionFromGroup,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Remove permission from group"""
    return await IamService.remove_permission_from_group(
        group_name=request.group_name,
        permission_name=request.permission_name,
        session=sessions.rw,
    )


@iam_router.delete("/delete_role/", status_code=status.HTTP_200_OK, tags=["roles"])
async def _delete_role(
    request: DeleteRole,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Delete role"""
    return await IamService.delete_role(role_name=request.role_name, session=sessions.rw)


@iam_router.delete("/delete_group/", status_code=status.HTTP_200_OK, tags=["groups"])
async def _delete_group(
    request: DeleteGroup,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Delete group"""
    return await IamService.delete_group(group_name=request.group_name, session=sessions.rw)


@iam_router.delete(
    "/delete_permission/",
    status_code=status.HTTP_200_OK,
    tags=["permissions"],
)
async def _delete_permission(
    request: DeletePermission,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Delete permission"""
    return await IamService.delete_permission(
        permission_name=request.permission_name, session=sessions.rw
    )

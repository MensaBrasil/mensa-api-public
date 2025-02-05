"""Endpoints for managing roles and groups."""

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

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
from ..dbs import get_session
from ..services import IamService

iam_router = APIRouter(tags=["IAM"], prefix="/iam", dependencies=[Depends(verify_firebase_token)])

# POST requests


@iam_router.post("/create_role/", status_code=status.HTTP_201_CREATED, tags=["roles"])
async def _create_role(
    role: CreateRole,
    session: Session = Depends(get_session),
):
    """Create a new role"""
    return IamService.create_role(
        role_name=role.role_name,
        role_description=role.role_description,
        session=session,
    )


@iam_router.post("/create_group/", status_code=status.HTTP_201_CREATED, tags=["groups"])
async def _create_group(
    group: CreateGroup,
    session: Session = Depends(get_session),
):
    """Create a new group"""
    return IamService.create_group(
        group_name=group.group_name,
        group_description=group.group_description,
        session=session,
    )


@iam_router.post(
    "/create_permission/",
    status_code=status.HTTP_201_CREATED,
    tags=["permissions"],
)
async def _create_permission(
    permission: CreatePermission,
    session: Session = Depends(get_session),
):
    """Create a new permission"""
    return IamService.create_permission(
        permission_name=permission.permission_name,
        permission_description=permission.permission_description,
        session=session,
    )


@iam_router.post(
    "/add_role_to_member/",
    status_code=status.HTTP_201_CREATED,
    tags=["roles"],
)
async def _add_role_to_member(
    role: AddRoleToMember,
    session: Session = Depends(get_session),
):
    """Add role to member"""
    return IamService.add_role_to_member(
        role_name=role.role_name, member_id=role.member_id, session=session
    )


@iam_router.post(
    "/add_group_to_member/",
    status_code=status.HTTP_201_CREATED,
    tags=["groups"],
)
async def _add_group_to_member(
    group: AddGroupToMember,
    session: Session = Depends(get_session),
):
    """Add group to member"""
    return IamService.add_group_to_member(
        group_name=group.group_name, member_id=group.member_id, session=session
    )


@iam_router.post(
    "/add_permission_to_role/",
    status_code=status.HTTP_201_CREATED,
    tags=["roles"],
)
async def _add_permission_to_role(
    data: AddPermissionToRole,
    session: Session = Depends(get_session),
):
    """Add permission to role"""
    return IamService.add_permission_to_role(
        role_name=data.role_name,
        permission_name=data.permission_name,
        session=session,
    )


@iam_router.post(
    "/add_permission_to_group/",
    status_code=status.HTTP_201_CREATED,
    tags=["groups"],
)
async def _add_permission_to_group(
    data: AddPermissionToGroup,
    session: Session = Depends(get_session),
):
    """Add permission to group"""
    return IamService.add_permission_to_group(
        group_name=data.group_name,
        permission_name=data.permission_name,
        session=session,
    )


# GET requests


@iam_router.get("/roles/", status_code=status.HTTP_200_OK, tags=["roles"])
async def _get_roles(
    token_data=Depends(verify_firebase_token), session: Session = Depends(get_session)
):
    """Get roles for member"""
    return IamService.get_member_roles(token_data=token_data, session=session)


@iam_router.get("/groups/", status_code=status.HTTP_200_OK, tags=["groups"])
async def _get_groups(
    token_data=Depends(verify_firebase_token), session: Session = Depends(get_session)
):
    """Get groups for member"""
    return IamService.get_member_groups(token_data=token_data, session=session)


@iam_router.get(
    "/members/role/",
    status_code=status.HTTP_200_OK,
    tags=["roles"],
)
async def _get_members_with_role(
    role_name: str,
    session: Session = Depends(get_session),
):
    """Get members with specific role"""
    return IamService.get_members_by_role_name(role_name=role_name, session=session)


@iam_router.get(
    "/members/group/",
    status_code=status.HTTP_200_OK,
    tags=["groups"],
)
async def _get_members_in_group(
    group_name: str,
    session: Session = Depends(get_session),
):
    """Get members in specific group"""
    return IamService.get_members_by_group_name(group_name=group_name, session=session)


@iam_router.get(
    "/role_permissions/",
    status_code=status.HTTP_200_OK,
    tags=["roles"],
)
async def _get_role_permissions(
    role_name: str,
    session: Session = Depends(get_session),
):
    """Get permissions for role"""
    return IamService.get_role_permissions_by_role_name(role_name=role_name, session=session)


@iam_router.get(
    "/group_permissions/",
    status_code=status.HTTP_200_OK,
    tags=["groups"],
)
async def _get_group_permissions(
    group_name: str,
    session: Session = Depends(get_session),
):
    """Get permissions for group"""
    return IamService.get_group_permissions_by_group_name(group_name=group_name, session=session)


# PATCH requests


@iam_router.patch("/update_role/", status_code=status.HTTP_200_OK, tags=["roles"])
async def _update_role(
    update_role: UpdateRole,
    session: Session = Depends(get_session),
):
    """Update role"""
    return IamService.edit_role_by_name(
        role_name=update_role.role_name,
        new_role_name=update_role.new_role_name,
        session=session,
        new_role_description=update_role.new_role_description,
    )


@iam_router.patch("/update_group/", status_code=status.HTTP_200_OK, tags=["groups"])
async def _update_group(
    update_group: UpdateGroup,
    session: Session = Depends(get_session),
):
    """Update group"""
    return IamService.edit_group_by_name(
        group_name=update_group.group_name,
        new_group_name=update_group.new_group_name,
        session=session,
        new_group_description=update_group.new_group_description,
    )


@iam_router.patch(
    "/update_permission/",
    status_code=status.HTTP_200_OK,
    tags=["permissions"],
)
async def _update_permission(
    data: UpdatePermission,
    session: Session = Depends(get_session),
):
    """Update permission"""
    return IamService.edit_permission_by_name(
        permission_name=data.permission_name,
        new_permission_name=data.new_permission_name,
        session=session,
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
    session: Session = Depends(get_session),
):
    """Remove role from member"""
    return IamService.remove_role_from_member(
        role_name=request.role_name, member_id=request.member_id, session=session
    )


@iam_router.delete(
    "/remove_group_from_member/",
    status_code=status.HTTP_200_OK,
    tags=["groups"],
)
async def _remove_group_from_member(
    request: RemoveGroupFromMember,
    session: Session = Depends(get_session),
):
    """Remove group from member"""
    return IamService.remove_group_from_member(
        group_name=request.group_name, member_id=request.member_id, session=session
    )


@iam_router.delete(
    "/remove_permission_from_role/",
    status_code=status.HTTP_200_OK,
    tags=["roles"],
)
async def _remove_permission_from_role(
    request: RemovePermissionFromRole,
    session: Session = Depends(get_session),
):
    """Remove permission from role"""
    return IamService.remove_permission_from_role(
        role_name=request.role_name,
        permission_name=request.permission_name,
        session=session,
    )


@iam_router.delete(
    "/remove_permission_from_group/",
    status_code=status.HTTP_200_OK,
    tags=["groups"],
)
async def _remove_permission_from_group(
    request: RemovePermissionFromGroup,
    session: Session = Depends(get_session),
):
    """Remove permission from group"""
    return IamService.remove_permission_from_group(
        group_name=request.group_name,
        permission_name=request.permission_name,
        session=session,
    )


@iam_router.delete("/delete_role/", status_code=status.HTTP_200_OK, tags=["roles"])
async def _delete_role(
    request: DeleteRole,
    session: Session = Depends(get_session),
):
    """Delete role"""
    return IamService.delete_role(role_name=request.role_name, session=session)


@iam_router.delete("/delete_group/", status_code=status.HTTP_200_OK, tags=["groups"])
async def _delete_group(
    request: DeleteGroup,
    session: Session = Depends(get_session),
):
    """Delete group"""
    return IamService.delete_group(group_name=request.group_name, session=session)


@iam_router.delete(
    "/delete_permission/",
    status_code=status.HTTP_200_OK,
    tags=["permissions"],
)
async def _delete_permission(
    request: DeletePermission,
    session: Session = Depends(get_session),
):
    """Delete permission"""
    return IamService.delete_permission(permission_name=request.permission_name, session=session)

"""Endpoints for managing member WhatsApp groups and group join requests."""

from fastapi import APIRouter, Depends

from people_api.schemas import InternalToken, UserToken

from ..auth import permission_required, verify_firebase_token
from ..dbs import AsyncSessionsTuple, get_async_sessions
from ..models.member import GroupJoinRequest
from ..permissions import AdminPermissions
from ..services import GroupService

group_router = APIRouter()


@group_router.get(
    "/get_can_participate",
    description="Get groups that the member can participate in",
    tags=["group", "whatsapp", "zelador"],
)
async def _get_can_participate(
    token_data: UserToken | InternalToken = Depends(verify_firebase_token),
    session: AsyncSessionsTuple = Depends(get_async_sessions),
):
    response = await GroupService.get_can_participate(token_data, session.ro)
    return response


@group_router.get(
    "/get_participate_in",
    description="Get groups that the member is participating in",
    tags=["group", "whatsapp", "zelador"],
)
async def _get_participate_in(
    token_data: UserToken | InternalToken = Depends(verify_firebase_token),
    session: AsyncSessionsTuple = Depends(get_async_sessions),
):
    return await GroupService.get_participate_in(token_data, session.ro)


@group_router.get(
    "/get_pending_requests",
    description="Get pending group join requests",
    tags=["group", "whatsapp", "zelador"],
)
async def _get_pending_requests(
    token_data: UserToken | InternalToken = Depends(verify_firebase_token),
    session: AsyncSessionsTuple = Depends(get_async_sessions),
):
    return await GroupService.get_pending_requests(token_data, session.ro)


@group_router.get(
    "/get_failed_requests",
    description="Get failed group join requests",
    tags=["group", "whatsapp", "zelador"],
)
async def _get_failed_requests(
    token_data: UserToken | InternalToken = Depends(verify_firebase_token),
    session: AsyncSessionsTuple = Depends(get_async_sessions),
):
    return await GroupService.get_failed_requests(token_data, session.ro)


@group_router.post(
    "/request_join_group",
    tags=["group", "whatsapp", "zelador"],
    description="Request to join a group",
)
async def _request_join_group(
    join_request: GroupJoinRequest,
    token_data: UserToken | InternalToken = Depends(verify_firebase_token),
    session: AsyncSessionsTuple = Depends(get_async_sessions),
):
    return await GroupService.request_join_group(join_request, token_data, session.rw)


@group_router.get(
    "/get_authorization_status",
    tags=["group", "whatsapp", "zelador"],
    description="Get zelador authorization status",
)
async def _get_authorization_status(
    token_data: UserToken | InternalToken = Depends(verify_firebase_token),
    session: AsyncSessionsTuple = Depends(get_async_sessions),
):
    return await GroupService.get_authorization_status(token_data, session.ro)


@group_router.get(
    "/get_workers",
    tags=["group", "whatsapp", "zelador"],
    description="Get workers in a group",
)
async def _get_workers(
    _token_data: UserToken | InternalToken = Depends(
        permission_required(AdminPermissions.manage_workers)
    ),
    session: AsyncSessionsTuple = Depends(get_async_sessions),
):
    return await GroupService.get_workers(session.ro)


@group_router.post(
    "/add_worker",
    tags=["group", "whatsapp", "zelador"],
    description="Add a worker to the database",
)
async def _add_worker(
    worker_phone: str,
    _token_data: UserToken | InternalToken = Depends(
        permission_required(AdminPermissions.manage_workers)
    ),
    session: AsyncSessionsTuple = Depends(get_async_sessions),
):
    return await GroupService.add_worker(worker_phone, session.rw)


@group_router.delete(
    "/remove_worker",
    tags=["group", "whatsapp", "zelador"],
    description="Remove a worker from the database",
)
async def _remove_worker(
    worker_phone: str,
    _token_data: UserToken | InternalToken = Depends(
        permission_required(AdminPermissions.manage_workers)
    ),
    session: AsyncSessionsTuple = Depends(get_async_sessions),
):
    return await GroupService.remove_worker(worker_phone, session.rw)

"""Endpoints for managing members in Google Workspace."""

from fastapi import APIRouter, Depends, Form

from ..services.workspace_service import WorkspaceService, verify_secret_key

google_workspace_router = APIRouter()


@google_workspace_router.post(
    "/create_user/",
    include_in_schema=True,
    description="Create a new user in Google Workspace",
)
async def _create_user(
    primary_email: str = Form(...),
    given_name: str = Form(...),
    family_name: str = Form(...),
    secondary_email: str = Form(None),
    api_key: str = Depends(verify_secret_key),
):
    return WorkspaceService.create_user(primary_email, given_name, family_name, secondary_email)

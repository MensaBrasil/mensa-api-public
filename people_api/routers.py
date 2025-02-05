from fastapi import APIRouter

from .endpoints import (
    certificate_router,
    data_router,
    google_workspace_router,
    group_router,
    iam_router,
    member_address_router,
    member_email_router,
    member_legal_representative_router,
    member_misc_router,
    member_phone_router,
    missing_fields_router,
    oauth_router,
    whatsapp_router,
)

APP_ROUTERS = [
    data_router,
    whatsapp_router,
    group_router,
    certificate_router,
    member_misc_router,
    member_address_router,
    member_email_router,
    member_legal_representative_router,
    member_phone_router,
    google_workspace_router,
    missing_fields_router,
    oauth_router,
    iam_router,
]

all_routers = APIRouter()

for router in APP_ROUTERS:
    all_routers.include_router(router)

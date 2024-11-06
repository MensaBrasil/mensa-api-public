# type: ignore
# pylint: disable-all
# ruff: noqa

"""APP
FastAPI app definition, initialization and definition of routes
"""

# # Installed # #

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from .endpoints import (
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
]

from .middlewares import request_handler

# # Package # #
from .settings import api_settings as settings

app = FastAPI(title=settings.title, docs_url="/documentation$@vtW6qodxYLQ", redoc_url=None)
app.middleware("http")(request_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://carteirinhas.mensa.org.br",
        "https://app.flutterflow.io",
    ],  # List of origins permitted to make requests
    allow_credentials=True,  # Allow cookies to be included in requests
    allow_methods=["*"],  # List of allowed HTTP methods
    allow_headers=["*"],  # List of allowed HTTP headers
)

for router in APP_ROUTERS:
    app.include_router(router)

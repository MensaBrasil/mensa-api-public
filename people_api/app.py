# type: ignore
# pylint: disable-all
# ruff: noqa

"""APP
FastAPI app definition, initialization and definition of routes
"""

# # Installed # #
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import all_routers
from .middlewares import request_handler

# # Package # #
from .settings import Settings

SETTINGS = Settings()

app = FastAPI(
    title=SETTINGS.api_title,
    docs_url="/documentation$@vtW6qodxYLQ",
    redoc_url=None,
    openapi_url="/api/vtW6qodxYLQ/openapi.json",
)
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

app.include_router(all_routers)

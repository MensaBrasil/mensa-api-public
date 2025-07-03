"""APP
FastAPI app definition, initialization and definition of routes
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import all_routers
from .settings import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    docs_url="/documentation$@vtW6qodxYLQ",
    redoc_url=None,
    openapi_url="/api/vtW6qodxYLQ/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.flutterflow.io",
    ],
    allow_origin_regex=r"https://.*\.mensa\.org\.br",
    # List of origins permitted to make requests
    allow_credentials=True,  # Allow cookies to be included in requests
    allow_methods=["*"],  # List of allowed HTTP methods
    allow_headers=["*"],  # List of allowed HTTP headers
)

app.include_router(all_routers)


def start_api():
    """Start the FastAPI app."""
    uvicorn.run(app, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    start_api()

"""Schemas. Make this a folder if there are multiple schemas"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class OAuthStateResponse(BaseModel):
    """Schema for OAuth state response"""

    state: str


class UserToken(BaseModel):
    """Pydantic model for Firebase token data."""

    email: EmailStr | None
    permissions: list[str] = []
    exp: int | None = None
    iat: int | None = None
    aud: str | None = None
    iss: str | None = None
    sub: str | None = None
    registration_id: int
    auth_time: int | None = None

    class Config:
        """Pydantic model configuration."""

        extra = "allow"


class InternalToken(BaseModel):
    """Pydantic model for internal JWT token claims."""

    iss: str
    sub: str
    exp: datetime
    iat: datetime
    registration_id: int | None
    email: EmailStr | None
    permissions: list[str] = []

    model_config = ConfigDict(extra="allow")

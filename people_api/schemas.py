"""Schemas. Make this a folder if there are multiple schemas"""

from pydantic import BaseModel, EmailStr


class OAuthStateResponse(BaseModel):
    """Schema for OAuth state response"""

    state: str

class FirebaseToken(BaseModel):
    """Pydantic model for Firebase token data."""
    email: EmailStr
    permissions: list[str] = []
    exp: int | None = None
    iat: int | None = None
    aud: str | None = None
    iss: str | None = None
    sub: str | None = None
    auth_time: int | None = None

    class Config:
        """Pydantic model configuration."""
        extra = "allow"

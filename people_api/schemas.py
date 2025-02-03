"""Schemas. Make this a folder if there are multiple schemas"""

from pydantic import BaseModel


class OAuthStateResponse(BaseModel):
    """Schema for OAuth state response"""

    state: str

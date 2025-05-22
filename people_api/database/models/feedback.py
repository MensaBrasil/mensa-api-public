"""Feedback model for the database."""

from enum import Enum

from fastapi import HTTPException, status
from pydantic import BaseModel, Field, field_validator


class FeedbackTargets(str, Enum):
    """
    Enum for feedback targets.
    """

    CHATBOT = "CHATBOT"
    WHATSAPP = "WHATSAPP"
    MOBILE_APP = "MOBILE_APP"
    SECRETARIA = "SECRETARIA"
    GESTAO = "GESTAO"


class FeedbackTypes(str, Enum):
    """
    Enum for feedback types.
    """

    NEUTRAL = "NEUTRAL"
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    FEATURE_REQUEST = "FEATURE_REQUEST"


class FeedbackBaseModel(BaseModel):
    """
    Feedback model for the database.
    """


class FeedbackCreate(FeedbackBaseModel):
    """
    Feedback model for creating feedback.
    """

    registration_id: int = Field(..., description="ID of the member submitting feedback")
    feedback_text: str = Field(
        min_length=10, max_length=1200, description="Feedback text (max 1200 chars)"
    )
    feedback_target: FeedbackTargets = Field(..., description="Target of the feedback")
    feedback_type: FeedbackTypes = Field(..., description="Type of feedback")

    @field_validator("feedback_text", mode="before")
    @classmethod
    def not_empty_feedback_text(cls, v):
        """Validate that feedback text is not empty."""
        if not v or not v.strip():
            raise ValueError("Feedback text must not be empty.")
        if not 10 < len(v) < 1200:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Feedback text must be between 10 and 1200 characters.",
            )
        return v

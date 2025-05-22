"""Service for processing feedback"""

import logging

from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from ..database.models import Feedback, Registration
from ..database.models.feedback import FeedbackCreate
from ..schemas import InternalToken, UserToken


class FeedbackService:
    """
    Service for processing feedback.
    """

    @staticmethod
    async def process_feedback(
        feedback_data: FeedbackCreate,
        token_data: UserToken | InternalToken,
        session: AsyncSession,
    ):
        """
        Process feedback from the user.
        """
        try:
            if not token_data.registration_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not authenticated",
                )
            registration = (
                await session.exec(
                    Registration.select_stmt_by_id(registration_id=token_data.registration_id)
                )
            ).first()
            if not registration:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Registration not found",
                )

            feedback = Feedback(
                registration_id=token_data.registration_id,
                feedback_text=feedback_data.feedback_text,
                feedback_target=feedback_data.feedback_target,
                feedback_type=feedback_data.feedback_type,
            )
            session.add(feedback)

            return {"message": "Feedback submitted successfully"}

        except Exception as e:
            logging.error("Error processing feedback: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while processing feedback.",
            ) from e

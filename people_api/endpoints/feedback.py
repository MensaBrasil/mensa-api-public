from fastapi import APIRouter, Depends

from ..auth import verify_firebase_token
from ..database.models.feedback import FeedbackCreate
from ..dbs import AsyncSessionsTuple, get_async_sessions
from ..schemas import InternalToken, UserToken
from ..services.feedback_service import FeedbackService

feedback_router = APIRouter(prefix="/feedback", tags=["feedback"])


@feedback_router.post(path="/", description="Send feedback.", tags=["feedback"])
async def give_feedback(
    feedback_data: FeedbackCreate,
    token_data: UserToken | InternalToken = Depends(verify_firebase_token),
    session: AsyncSessionsTuple = Depends(get_async_sessions),
):
    return await FeedbackService.process_feedback(
        feedback_data=feedback_data,
        token_data=token_data,
        session=session.rw,
    )

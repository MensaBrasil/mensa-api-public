"""
Endpoints for managing the Volunteer Recognition platform.
"""

import base64
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import select

from people_api.auth import (
    get_registration_id,
    permission_required,
    verify_firebase_token,
)
from people_api.database.models.models import LegalRepresentatives, Registration
from people_api.database.models.volunteer import (
    ActivityWithCategoryPublic,
    CombinedNamesResponse,
    LeaderboardEntry,
    UserActivityFullResponse,
    VolunteerActivityCategory,
    VolunteerActivityCategoryCreate,
    VolunteerActivityCategoryPublic,
    VolunteerActivityCategoryUpdate,
    VolunteerActivityEvaluation,
    VolunteerActivityEvaluationCreate,
    VolunteerActivityEvaluationPublic,
    VolunteerActivityLog,
    VolunteerActivityLogCreate,
    VolunteerActivityLogPublic,
    VolunteerPointTransaction,
)
from people_api.permissions import Volunteer as P
from people_api.utils import generate_presigned_media_url, upload_media_to_s3

from ..dbs import AsyncSessionsTuple, get_async_sessions
from ..schemas import UserToken
from ..settings import get_settings

volunteer_router = APIRouter(
    tags=["VolunteerRecognition"],
    prefix="/volunteer",
    dependencies=[Depends(verify_firebase_token)],
)


@volunteer_router.post(
    "/admin/categories/",
    response_model=VolunteerActivityCategoryPublic,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(permission_required(P.category_create))],
)
async def create_activity_category(
    category: VolunteerActivityCategoryCreate,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Create a new activity category."""
    category_obj = VolunteerActivityCategory(**category.model_dump())
    sessions.rw.add(category_obj)
    await sessions.rw.commit()
    await sessions.rw.refresh(category_obj)
    return category_obj


@volunteer_router.patch(
    "/admin/categories/by-name/{category_name}",
    response_model=VolunteerActivityCategoryPublic,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(permission_required(P.category_update))],
)
async def update_activity_category_by_name(
    category_name: str,
    category_data: VolunteerActivityCategoryUpdate,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Update an existing activity category by its name."""
    query = VolunteerActivityCategory.select_one(name=category_name)
    result = await sessions.rw.exec(query)
    category_obj = result.one_or_none()
    if not category_obj:
        raise HTTPException(status_code=404, detail="Activity category not found")
    updated_category = VolunteerActivityCategory.update_instance(
        category_obj, category_data.model_dump(exclude_unset=True)
    )
    sessions.rw.add(updated_category)
    return updated_category


@volunteer_router.delete(
    "/admin/categories/{category_name}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(permission_required(P.category_delete))],
)
async def delete_activity_category(
    category_name: str,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """Delete an activity category by its name."""
    query = VolunteerActivityCategory.select_one(name=category_name)
    result = await sessions.rw.exec(query)
    category_obj = result.one_or_none()
    if not category_obj:
        raise HTTPException(status_code=404, detail="Activity category not found")
    await sessions.rw.delete(category_obj)
    return {"ok": True, "detail": "Activity category deleted"}


@volunteer_router.get(
    "/categories/",
    response_model=list[VolunteerActivityCategoryPublic],
    status_code=status.HTTP_200_OK,
)
async def get_all_activity_categories(
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """
    Fetch all existing volunteer activity categories using the select_all method.
    """
    query = VolunteerActivityCategory.select_all()
    result = await sessions.ro.exec(query)
    categories = result.all()
    return categories


@volunteer_router.post(
    "/activity/logs/",
    response_model=VolunteerActivityLogPublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_activity_log(
    log: VolunteerActivityLogCreate,
    registration_id: int = Depends(get_registration_id),
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """
    Create a new volunteer activity log.
    """
    data = log.model_dump(exclude={"registration_id"})
    data["registration_id"] = registration_id

    if data.get("media_file"):
        try:
            file_content = base64.b64decode(data["media_file"])
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid media_file encoding") from e

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
        s3_key = f"activity_media/{timestamp}_uploaded_image.jpg"
        bucket = get_settings().volunteer_s3_bucket
        try:
            media_url = upload_media_to_s3(bucket, s3_key, file_content, "image/jpeg")
        except Exception as e:
            logging.error(f"Error uploading image to S3: {e}")
            raise HTTPException(status_code=500, detail="Error uploading image to S3") from e
        data["media_path"] = media_url

    activity_log = VolunteerActivityLog(**data)
    sessions.rw.add(activity_log)
    await sessions.rw.commit()
    await sessions.rw.refresh(activity_log)
    return activity_log


@volunteer_router.post(
    "/admin/evaluations/",
    response_model=VolunteerActivityEvaluationPublic,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(permission_required(P.evaluation_create))],
)
async def create_activity_evaluation(
    evaluation: VolunteerActivityEvaluationCreate,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
    token_data: UserToken = Depends(verify_firebase_token),
):
    """
    Create a new activity evaluation, including the evaluator's registration_id.
    """
    evaluation.evaluator_id = token_data.registration_id

    evaluation_obj = VolunteerActivityEvaluation(**evaluation.model_dump())
    sessions.rw.add(evaluation_obj)

    if evaluation_obj.status.lower() == "approved":
        query = select(VolunteerActivityLog).where(
            VolunteerActivityLog.id == evaluation_obj.activity_id
        )
        result = await sessions.ro.exec(query)
        activity_log = result.one_or_none()
        if not activity_log:
            raise HTTPException(status_code=404, detail="Activity log not found")
        category_query = select(VolunteerActivityCategory).where(
            VolunteerActivityCategory.id == activity_log.category_id
        )
        category_result = await sessions.ro.exec(category_query)
        category = category_result.one_or_none()
        if not category:
            raise HTTPException(status_code=404, detail="Activity category not found")

        if activity_log.registration_id is None:
            raise HTTPException(status_code=400, detail="No registration found")

        point_transaction = VolunteerPointTransaction.prepare_transaction(
            registration_id=activity_log.registration_id,
            activity_id=activity_log.id,
            points=category.points,
        )
        sessions.rw.add(point_transaction)

    await sessions.rw.commit()
    await sessions.rw.refresh(evaluation_obj)

    return evaluation_obj


@volunteer_router.get(
    "/activity/evaluations/member/",
    response_model=list[VolunteerActivityEvaluationPublic],
    status_code=status.HTTP_200_OK,
)
async def get_member_activity_evaluations(
    token_data: UserToken = Depends(verify_firebase_token),
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """
    Fetch activity evaluations for the authenticated member.
    """
    registration_id = token_data.registration_id
    query = VolunteerActivityEvaluation.select_evaluations_for_member(registration_id)
    result = await sessions.ro.exec(query)
    evaluations = result.all()
    return evaluations


@volunteer_router.get(
    "/leaderboard/",
    response_model=list[LeaderboardEntry],
    status_code=status.HTTP_200_OK,
)
async def get_leaderboard(
    start_date: datetime = Query(..., description="Start date (ISO format)"),
    end_date: datetime = Query(..., description="End date (ISO format)"),
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """
    Retrieve volunteer point totals and ranking between start_date and end_date.
    """
    query = VolunteerPointTransaction.select_leaderboard_period(start_date, end_date)
    result = await sessions.ro.exec(query)
    rows = result.all()

    leaderboard = [
        LeaderboardEntry(
            registration_id=row[0],
            volunteer_name=row[1] or "Unknown",
            total_points=row[2],
            rank=row[3],
        )
        for row in rows
    ]
    return leaderboard


@volunteer_router.get(
    "/activities/",
    response_model=list[VolunteerActivityLogPublic],
)
async def get_public_activity_feed(
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """
    Retrieve all volunteer activity logs for the public feed.
    """
    query = VolunteerActivityLog.select_all()
    result = await sessions.ro.exec(query)
    logs = result.all()

    for log in logs:
        log.media_path = generate_presigned_media_url(log.media_path)

    return logs


@volunteer_router.get(
    "/admin/categories/{category_id}",
    response_model=VolunteerActivityCategoryPublic,
)
async def get_activity_category_by_id(
    category_id: int,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """
    Retrieve a single activity category by its ID.
    """
    query = VolunteerActivityCategory.select_one(id=category_id)
    result = await sessions.ro.exec(query)
    category_obj = result.one_or_none()
    if not category_obj:
        raise HTTPException(status_code=404, detail="Activity category not found")
    return category_obj


@volunteer_router.get(
    "/names", response_model=CombinedNamesResponse, status_code=status.HTTP_200_OK
)
async def get_combined_names(
    token_data: UserToken = Depends(verify_firebase_token),
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """
    Retrieve combined names from both the registration record and legal representatives
    for the authenticated user.
    """
    registration_id = token_data.registration_id

    query = select(Registration).where(Registration.registration_id == registration_id)
    result = await sessions.ro.exec(query)
    registration_obj = result.one_or_none()

    lr_query = select(LegalRepresentatives).where(
        LegalRepresentatives.registration_id == registration_id
    )
    lr_result = await sessions.ro.exec(lr_query)
    legal_reps = lr_result.all()
    return CombinedNamesResponse.from_data(registration_obj, list(legal_reps))


@volunteer_router.get(
    "/admin/evaluate-with-category/",
    response_model=list[ActivityWithCategoryPublic],
    status_code=status.HTTP_200_OK,
)
async def get_unevaluated_activities_for_evaluation(
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """
    Retrieve all volunteer activity logs that have not yet been evaluated.
    """
    query = VolunteerActivityLog.select_unevaluated()
    result = await sessions.ro.exec(query)
    logs = result.all()

    activities_with_category = []
    for log in logs:
        category_query = select(VolunteerActivityCategory).where(
            VolunteerActivityCategory.id == log.category_id
        )
        category_result = await sessions.ro.exec(category_query)
        category_obj = category_result.one_or_none()
        if not category_obj:
            logging.warning(
                f"Category id {log.category_id} not found for activity id {log.id}. Skipping activity."
            )
            continue

        presigned_media_url = generate_presigned_media_url(log.media_path)
        activity_public = VolunteerActivityLogPublic.model_validate(log)
        activities_with_category.append(
            ActivityWithCategoryPublic(
                activity=activity_public,
                category_name=category_obj.name,
                presigned_media_url=presigned_media_url,
            )
        )
    return activities_with_category


@volunteer_router.get(
    "/activity-with-category/",
    response_model=ActivityWithCategoryPublic,
    status_code=status.HTTP_200_OK,
)
async def get_activity_with_category(
    activity_id: int,
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """
    Retrieve a single activity by its ID along with the category name.
    """
    query = select(VolunteerActivityLog).where(VolunteerActivityLog.id == activity_id)
    result = await sessions.ro.exec(query)
    activity_obj = result.one_or_none()
    if not activity_obj:
        raise HTTPException(status_code=404, detail="Activity log not found")

    category_query = select(VolunteerActivityCategory).where(
        VolunteerActivityCategory.id == activity_obj.category_id
    )
    category_result = await sessions.ro.exec(category_query)
    category_obj = category_result.one_or_none()
    if not category_obj:
        raise HTTPException(status_code=404, detail="Activity category not found")
    presigned_media_url = generate_presigned_media_url(activity_obj.media_path)
    activity_public = VolunteerActivityLogPublic.model_validate(activity_obj)
    return ActivityWithCategoryPublic(
        activity=activity_public,
        category_name=category_obj.name,
        presigned_media_url=presigned_media_url,
    )


@volunteer_router.get(
    "/points/",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def get_total_points(
    token_data: UserToken = Depends(verify_firebase_token),
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """
    Retrieve the total number of points for the authenticated registration.
    """

    registration_id = token_data.registration_id
    query = VolunteerPointTransaction.total_points_query(registration_id)
    result = await sessions.ro.exec(query)
    total_points = result.one_or_none()
    if total_points is None:
        total_points = 0
    return {"registration_id": registration_id, "total_points": total_points}


@volunteer_router.get(
    "/activities/full/approved/",
    response_model=list[UserActivityFullResponse],
    status_code=status.HTTP_200_OK,
)
async def get_user_full_activities_approved(
    token_data: UserToken = Depends(verify_firebase_token),
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """
    Retrieve all volunteer activity logs for the authenticated user that have been approved."""
    registration_id = token_data.registration_id
    result = await sessions.ro.exec(
        VolunteerActivityLog.select_full_user_activities_approved(registration_id)
    )
    rows = result.all()

    activities: list[UserActivityFullResponse] = []
    for log, evaluation, points in rows:
        activity = VolunteerActivityLogPublic.model_validate(log)
        evaluation_public = VolunteerActivityEvaluationPublic.model_validate(evaluation)
        activity.media_path = generate_presigned_media_url(log.media_path)
        activities.append(
            UserActivityFullResponse(
                activity=activity,
                evaluation=evaluation_public,
                points=points,
            )
        )
    return activities


@volunteer_router.get(
    "/activities/full/rejected/",
    response_model=list[UserActivityFullResponse],
    status_code=status.HTTP_200_OK,
)
async def get_user_full_activities_rejected(
    token_data: UserToken = Depends(verify_firebase_token),
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """
    Retrieve all volunteer activity logs for the authenticated user that have been rejected."""
    registration_id = token_data.registration_id
    result = await sessions.ro.exec(
        VolunteerActivityLog.select_full_user_activities_rejected(registration_id)
    )
    rows = result.all()

    activities: list[UserActivityFullResponse] = []
    for log, evaluation in rows:
        activity = VolunteerActivityLogPublic.model_validate(log)
        evaluation_public = VolunteerActivityEvaluationPublic.model_validate(evaluation)
        activity.media_path = generate_presigned_media_url(log.media_path)
        activities.append(
            UserActivityFullResponse(
                activity=activity,
                evaluation=evaluation_public,
            )
        )
    return activities


@volunteer_router.get(
    "/activities/full/unevaluated/",
    response_model=list[UserActivityFullResponse],
    status_code=status.HTTP_200_OK,
)
async def get_user_full_activities_unevaluated(
    token_data: UserToken = Depends(verify_firebase_token),
    sessions: AsyncSessionsTuple = Depends(get_async_sessions),
):
    """
    Retrieve all volunteer activity logs for the authenticated user that have not yet been evaluated."""
    registration_id = token_data.registration_id
    result = await sessions.ro.exec(
        VolunteerActivityLog.select_full_user_activities_unevaluated(registration_id)
    )
    logs = result.all()

    activities: list[UserActivityFullResponse] = []
    for log in logs:
        activity = VolunteerActivityLogPublic.model_validate(log)
        activity.media_path = generate_presigned_media_url(log.media_path)
        activities.append(UserActivityFullResponse(activity=activity, evaluation=None))
    return activities

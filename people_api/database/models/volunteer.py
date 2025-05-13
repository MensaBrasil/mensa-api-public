"""Models for the volunteer activity tracking system."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict
from sqlalchemy.sql.elements import ColumnElement
from sqlmodel import Column, Field, SQLModel, Text, col, desc, func, select
from sqlmodel.sql.expression import Select

from people_api.database.models.models import BaseSQLModel, Registration


class LeaderboardEntry(BaseModel):
    """Model for a single entry in the volunteer leaderboard."""

    registration_id: int
    volunteer_name: str
    total_points: int
    rank: int


class BaseVolunteerActivityCategory(BaseSQLModel):
    """Base model for a volunteer activity category."""

    name: str = Field(max_length=255, unique=True)
    description: str | None = Field(default=None, sa_column=Column(Text))
    points: int = Field(default=0)


class VolunteerActivityCategory(BaseVolunteerActivityCategory, table=True):
    """Model for a volunteer activity category."""

    __tablename__ = "volunteer_activity_category"
    id: int = Field(default=None, primary_key=True)


class VolunteerActivityCategoryCreate(BaseVolunteerActivityCategory):
    """Model for creating a new volunteer activity category."""


class VolunteerActivityCategoryPublic(BaseVolunteerActivityCategory):
    """Model for a public view of a volunteer activity category."""

    id: int


class VolunteerActivityCategoryUpdate(SQLModel):
    """Model for updating an existing volunteer activity category."""

    name: str | None = None
    description: str | None = None
    points: int | None = None


class BaseVolunteerActivityLog(BaseSQLModel):
    """Base model for a volunteer activity log."""

    registration_id: int | None = Field(
        default=None, foreign_key="registration.registration_id", exclude=True
    )
    category_id: int = Field(foreign_key="volunteer_activity_category.id")
    title: str = Field(max_length=255)
    description: str | None = Field(default=None, sa_column=Column(Text))
    activity_date: date | None = Field(default=None)
    media_path: str | None = Field(default=None, max_length=255)
    volunteer_name: str | None = Field(default=None, max_length=50)


class VolunteerActivityLog(BaseVolunteerActivityLog, table=True):
    """Model for a volunteer activity log."""

    __tablename__ = "volunteer_activity_log"
    id: int = Field(default=None, primary_key=True)

    @classmethod
    def select_unevaluated(cls):
        """
        Build a query that retrieves all unevaluated activities."""
        return (
            select(cls)
            .outerjoin(
                VolunteerActivityEvaluation,
                col(cls.id) == col(VolunteerActivityEvaluation.activity_id),
            )
            .where(VolunteerActivityEvaluation.id == None)  # noqa: E711
        )

    @classmethod
    def select_full_user_activities_approved(cls, registration_id: int):
        """
        Build a query that retrieves all approved activities for a member."""
        return (
            select(cls, VolunteerActivityEvaluation, col(VolunteerActivityCategory.points))
            .join(
                VolunteerActivityEvaluation, col(VolunteerActivityEvaluation.activity_id) == cls.id
            )
            .join(VolunteerActivityCategory, col(VolunteerActivityCategory.id) == cls.category_id)
            .where(
                cls.registration_id == registration_id,
                func.lower(VolunteerActivityEvaluation.status) == "approved",
            )
        )

    @classmethod
    def select_full_user_activities_rejected(cls, registration_id: int):
        """
        Build a query that retrieves all rejected activities for a member."""
        return (
            select(cls, VolunteerActivityEvaluation)
            .join(
                VolunteerActivityEvaluation, col(VolunteerActivityEvaluation.activity_id) == cls.id
            )
            .where(
                cls.registration_id == registration_id,
                func.lower(VolunteerActivityEvaluation.status) == "rejected",
            )
        )

    @classmethod
    def select_full_user_activities_unevaluated(cls, registration_id: int):
        """
        Build a query that retrieves all unevaluated activities for a member."""
        return (
            select(cls)
            .outerjoin(
                VolunteerActivityEvaluation, col(VolunteerActivityEvaluation.activity_id) == cls.id
            )
            .where(
                cls.registration_id == registration_id,
                col(VolunteerActivityEvaluation.id) == None,  # noqa: E711
            )
        )

    @classmethod
    def select_by_member(cls, registration_id: int):
        """
        Returns a SQLModel Select query for all activity logs for a specific member.
        """
        return select(cls).where(cls.registration_id == registration_id)

    @classmethod
    def select_by_member_and_id(cls, activity_id: int, registration_id: int):
        """
        Build a query to select a volunteer activity log by its id for a specific member.
        """
        return select(cls).where(cls.id == activity_id, cls.registration_id == registration_id)


class VolunteerActivityLogCreate(BaseVolunteerActivityLog):
    """Model for creating a new volunteer activity log."""

    media_file: str | None = None


class VolunteerActivityLogPublic(BaseVolunteerActivityLog):
    """Model for a public view of a volunteer activity log."""

    id: int


class BaseVolunteerActivityEvaluation(BaseSQLModel):
    """Base model for an activity evaluation"""

    activity_id: int = Field(foreign_key="volunteer_activity_log.id")
    evaluator_id: int | None = Field(default=None)
    status: str = Field(max_length=50, index=True)
    observation: str | None = Field(default=None, sa_column=Column(Text))


class VolunteerActivityEvaluation(BaseVolunteerActivityEvaluation, table=True):
    """Model for an activity evaluation"""

    __tablename__ = "activity_evaluation"
    id: int = Field(default=None, primary_key=True)

    @classmethod
    def select_evaluations_for_member(cls, registration_id: int):
        """Select all evaluations for a member."""
        return (
            select(cls)
            .join(VolunteerActivityLog)
            .where(VolunteerActivityLog.id == cls.activity_id)
            .where(VolunteerActivityLog.registration_id == registration_id)
        )

    @classmethod
    def select_evaluated_activities_for_member(cls, registration_id: int):
        """
        Build a query that retrieves evaluated activities for a member.
        Returns the VolunteerActivityLog object along with the evaluation status and observation.
        """

        return (
            select(VolunteerActivityLog, cls.status, cls.observation)
            .join(
                VolunteerActivityLog,
                col(VolunteerActivityLog.id) == col(cls.activity_id),
            )
            .where(VolunteerActivityLog.registration_id == registration_id)
        )


class VolunteerActivityEvaluationCreate(BaseVolunteerActivityEvaluation):
    """Model for creating a new activity evaluation"""


class VolunteerActivityEvaluationPublic(BaseVolunteerActivityEvaluation):
    """Model for a public view of an activity evaluation"""

    id: int


class BaseVolunteerPointTransaction(BaseSQLModel):
    """Base model for a volunteer point transaction."""

    registration_id: int = Field(foreign_key="registration.registration_id")
    activity_id: int | None = Field(default=None, foreign_key="volunteer_activity_log.id")
    points: int


class VolunteerPointTransaction(BaseVolunteerPointTransaction, table=True):
    """Model for a volunteer point transaction."""

    __tablename__ = "volunteer_point_transactions"
    id: int = Field(default=None, primary_key=True)

    @classmethod
    def prepare_transaction(
        cls, registration_id: int, activity_id: int, points: int
    ) -> "VolunteerPointTransaction":
        """Prepare a new point transaction for a volunteer activity."""
        return cls(
            registration_id=registration_id,
            activity_id=activity_id,
            points=points,
        )

    @classmethod
    def select_leaderboard_period(
        cls,
        start_date: datetime,
        end_date: datetime,
    ) -> Select:
        total_points: ColumnElement = func.sum(cls.points).label("total_points")
        rank = func.row_number().over(order_by=desc(total_points)).label("rank")

        return (
            select(
                cls.registration_id,
                col(Registration.name).label("full_name"),
                total_points,
                rank,
            )
            .select_from(cls)
            .join(
                VolunteerActivityEvaluation,
                col(VolunteerActivityEvaluation.activity_id) == cls.activity_id,
            )
            .where(
                VolunteerActivityEvaluation.created_at >= start_date,  # type: ignore
                VolunteerActivityEvaluation.created_at <= end_date,  # type: ignore
            )
            .join(
                Registration,
                col(Registration.registration_id) == cls.registration_id,
            )
            .group_by(col(cls.registration_id), col(Registration.name))
            .order_by(desc(total_points))
        )

    @classmethod
    def select_top_n(
        cls,
        start_date: datetime,
        end_date: datetime,
        n: int = 10,
    ) -> Select:
        """Top-n leaderboard between start/end dates."""
        return cls.select_leaderboard_period(start_date, end_date).limit(n)

    @classmethod
    def select_user_rank(
        cls, start_date: datetime, end_date: datetime, registration_id: int
    ) -> Select:
        """
        Returns a subquery‐filtered row (registration_id, full_name, total_points, rank)
        for the given member, if they have any approved points in the window.
        """
        subq = cls.select_leaderboard_period(start_date, end_date).subquery()
        return select(
            subq.c.registration_id,
            subq.c.full_name,
            subq.c.total_points,
            subq.c.rank,
        ).where(subq.c.registration_id == registration_id)

    @classmethod
    def total_points_query(cls, registration_id: int):
        """
        Build a query to calculate the total points for the given registration id.

        """
        return select(func.sum(cls.points)).where(cls.registration_id == registration_id)


class VolunteerPointTransactionCreate(BaseVolunteerPointTransaction):
    """Model for creating a new volunteer point transaction."""


class VolunteerPointTransactionPublic(BaseVolunteerPointTransaction):
    """Model for a public view of a volunteer point transaction."""

    id: int


class CombinedNamesResponse(BaseModel):
    """Model for a list of full names."""

    names: list[str]

    @classmethod
    def split_name(cls, full_name: str):
        """Helper method to split the full name into first and last names."""
        name_parts = full_name.split(" ")
        first_name = name_parts[0] if name_parts else ""
        last_name = name_parts[-1] if len(name_parts) > 1 else ""
        return first_name, last_name

    @classmethod
    def from_registration(cls, registration) -> str:
        """
        Build a full name string from a Registration instance,
        splitting it into first and last names.
        """
        if registration.name:
            first_name, last_name = cls.split_name(registration.name.strip())
            return f"{first_name} {last_name}"
        return ""

    @classmethod
    def from_legal_representative(cls, legal_rep) -> str:
        """
        Build a full name string from a LegalRepresentatives instance,
        splitting it into first and last names.
        """
        if legal_rep.full_name:
            first_name, last_name = cls.split_name(legal_rep.full_name.strip())
            return f"{first_name} {last_name}"
        return ""

    @classmethod
    def from_data(cls, registration, legal_reps: list) -> "CombinedNamesResponse":
        """
        Build the CombinedNamesResponse from a registration object and a list of legal representative objects.
        Splitting the names of both the registration and the legal representatives.
        """
        reg_full_name = cls.from_registration(registration)
        lr_full_names = [cls.from_legal_representative(lr) for lr in legal_reps]
        return cls(names=[reg_full_name] + lr_full_names)


class ActivityWithCategoryPublic(BaseModel):
    """Represents an activity plus its category name for evaluation."""

    activity: VolunteerActivityLogPublic
    category_name: str
    presigned_media_url: str | None = None


class UserActivityFullResponse(BaseModel):
    """Model for a full response of a user's activity log, without category."""

    activity: VolunteerActivityLogPublic
    evaluation: VolunteerActivityEvaluationPublic | None = None
    points: int | None = None

    model_config = ConfigDict(from_attributes=True)

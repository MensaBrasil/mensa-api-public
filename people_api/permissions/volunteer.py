"""All volunteer permissions are defined here."""

from enum import StrEnum


class VolunteerAdmin(StrEnum):
    """Volunteer recognition platform management permissions."""

    category_create = "VOLUNTEER.CATEGORY.CREATE"
    category_update = "VOLUNTEER.CATEGORY.UPDATE"
    category_delete = "VOLUNTEER.CATEGORY.DELETE"
    evaluation_create = "VOLUNTEER.EVALUATION.CREATE"
    evaluation_update = "VOLUNTEER.EVALUATION.UPDATE"


class VolunteerMember(StrEnum):
    """Volunteer permissions for members."""

    activity_create = "VOLUNTEER.ACTIVITY.CREATE"
    leaderboard_view = "VOLUNTEER.LEADERBOARD.VIEW"
    category_list = "VOLUNTEER.CATEGORY.LIST"
    evaluation_view = "VOLUNTEER.EVALUATION.VIEW"

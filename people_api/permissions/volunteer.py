"""All volunteer permissions are defined here."""

from enum import StrEnum

class Volunteer(StrEnum):
    """Volunteer recognition permissions."""
    category_create = "VOLUNTEER.CATEGORY.CREATE"
    category_update = "VOLUNTEER.CATEGORY.UPDATE"
    category_delete = "VOLUNTEER.CATEGORY.DELETE"
    evaluation_create = "VOLUNTEER.EVALUATION.CREATE"
    evaluation_update = "VOLUNTEER.EVALUATION.UPDATE"


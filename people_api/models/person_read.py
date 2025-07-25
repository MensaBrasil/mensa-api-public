# mypy: ignore-errors

"""MODELS - PERSON - READ
Person Read model. Inherits from PersonCreate and adds the person_id field, which is the _id field on Mongo documents
"""

# # Native # #
from datetime import datetime

# # Installed # #
import pydantic
from dateutil.relativedelta import relativedelta

from .fields import PersonFields

# # Package # #
from .person_create import PersonCreate

__all__ = ("PersonRead", "PeopleRead")


class PersonRead(PersonCreate):
    """Body of Person GET and POST responses"""

    person_id: str = PersonFields.person_id
    age: int | None = PersonFields.age
    created: int = PersonFields.created
    updated: int = PersonFields.updated

    @pydantic.model_validator(mode="before")
    def _set_person_id(self, data):
        """Swap the field _id to person_id (this could be done with field alias, by setting the field as "_id"
        and the alias as "person_id", but can be quite confusing)"""
        document_id = data.get("_id")
        if document_id:
            data["person_id"] = document_id
        return data

    @pydantic.model_validator(mode="before")
    def _set_age(self, data):
        """Calculate the current age of the person from the date of birth, if any"""
        birth = data.get("birth")
        if birth:
            today = datetime.now().date()
            data["age"] = relativedelta(today, birth).years
        return data

    # TODO[pydantic]: The `Config` class inherits from another class, please create the `model_config` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    class config:
        extra = "ignore"  # if a read document has extra fields, ignore them


PeopleRead = list[PersonRead]

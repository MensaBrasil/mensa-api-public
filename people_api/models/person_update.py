"""MODELS - PERSON - UPDATE
Person Update model. All attributes are set as Optional, as we use the PATCH method for update
(in which only the attributes to change are sent on request body)
"""

# # Native # #
from contextlib import suppress
from datetime import date

# # Package # #
from .common import BaseModel
from .fields import PersonFields
from .member_data import Address

__all__ = ("PersonUpdate",)


class PersonUpdate(BaseModel):
    """Body of Person PATCH requests"""

    name: str | None = PersonFields.name
    address: Address | None = PersonFields.address_update
    birth: date | None = PersonFields.birth

    def dict(self, **kwargs):
        # The "birth" field must be converted to string (isoformat) when exporting to dict (for Mongo)
        # TODO Better way to do this? (automatic conversion can be done with Config.json_encoders, but not available for dict
        d = super().dict(**kwargs)
        with suppress(KeyError):
            d["birth"] = d.pop("birth").isoformat()
        return d

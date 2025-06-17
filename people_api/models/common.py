"""MODELS - COMMON
Common variables and base classes for the models
"""

# # Installed # #
import pydantic
from pydantic import BaseModel
from pydantic import ConfigDict

__all__ = ("BaseModel",)


class BaseModel(BaseModel):
    """All data models inherit from this class"""

    @pydantic.model_validator(mode="before")
    def _min_properties(cls, data):
        """At least one property is required"""
        if not data:
            raise ValueError("At least one property is required")
        return data

    def dict(self, include_nulls=False, **kwargs):
        """Override the super dict method by removing null keys from the dict, unless include_nulls=True"""
        kwargs["exclude_none"] = not include_nulls
        return super().dict(**kwargs)
    model_config = ConfigDict(extra=pydantic.Extra.forbid, str_strip_whitespace=True)

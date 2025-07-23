"""Initialize the object by importing all available permissions from various modules."""

from .admin import AdminPermissions
from .volunteer import VolunteerAdmin, VolunteerMember

__all__ = ["VolunteerAdmin", "VolunteerMember", "AdminPermissions"]

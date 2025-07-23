"""This file defines the admin permissions for managing the API."""

from enum import StrEnum


class AdminPermissions(StrEnum):
    """Admin permissions for managing the api."""

    manage_workers = "ADMIN.MANAGE.WORKERS"

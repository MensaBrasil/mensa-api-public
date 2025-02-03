# type: ignore
# pylint: disable-all
# ruff: noqa

import logging
import sys
from .settings import get_settings

from .app import app

settings = get_settings()

logging.basicConfig(
    level=settings.api_log_level,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

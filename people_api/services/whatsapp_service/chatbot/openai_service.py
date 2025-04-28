"""Service for OpenAI API"""

from openai import AsyncOpenAI

from ....settings import get_settings

SETTINGS = get_settings()

openai_client = AsyncOpenAI(api_key=SETTINGS.openai_api_key)

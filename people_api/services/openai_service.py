"""Service for OpenAI API"""

from openai import OpenAI

from ..settings import get_settings

SETTINGS = get_settings()

openai_client = OpenAI(api_key=SETTINGS.openai_api_key)

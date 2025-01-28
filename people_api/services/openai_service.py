"""Service for OpenAI API"""

from openai import OpenAI

from ..settings import Settings

SETTINGS = Settings()

openai_client = OpenAI(api_key=SETTINGS.OPENAI_API_KEY)

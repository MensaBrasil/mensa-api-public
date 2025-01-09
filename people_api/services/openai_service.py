"""Service for OpenAI API"""

from openai import OpenAI

from ..settings import OpenAISettings

openai_client = OpenAI(api_key=OpenAISettings.openai_api_key)

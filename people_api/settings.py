"""Settings for the API using pydantic-settings module"""

from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ("Settings",)


class Settings(BaseSettings):
    """Settings for the API"""

    API_TITLE: str
    API_PORT: str
    API_HOST: str
    API_LOG_LEVEL: str

    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DATABASE: str

    DATA_ROUTE_API_KEY: str
    WHATSAPP_ROUTE_API_KEY: str

    GOOGLE_API_KEY: str

    OPENAI_API_KEY: str

    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_FROM_WHATSAPP_NUMBER: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

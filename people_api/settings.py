"""Settings for the API using pydantic-settings module"""

from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ("Settings",)


class Settings(BaseSettings):
    """Settings for the API"""

    api_title: str
    api_port: str
    api_host: str
    api_log_level: str

    postgres_host: str
    postgres_user: str
    postgres_password: str
    postgres_database: str

    data_route_api_key: str
    whatsapp_route_api_key: str

    google_api_key: str

    openai_api_key: str

    twilio_account_sid: str
    twilio_auth_token: str
    twilio_from_whatsapp_number: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

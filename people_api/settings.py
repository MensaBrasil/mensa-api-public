"""Settings for the API using pydantic-settings module"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for the API"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    api_title: str
    api_port: str
    api_host: str
    api_log_level: str

    postgres_host: str
    postgres_user: str
    postgres_password: str
    postgres_database: str

    site_ro_user: str
    site_ro_password: str
    site_database: str

    postgres_ro_user: str
    postgres_ro_password: str

    data_route_api_key: str
    whatsapp_route_api_key: str

    google_api_key: str

    openai_api_key: str
    chatgpt_assistant_id: str

    twilio_account_sid: str
    twilio_auth_token: str
    twilio_from_whatsapp_number: str

    redis_host: str = "redis"
    redis_port: int = 6379

    discord_client_id: str
    discord_client_secret: str
    discord_redirect_uri: str

    google_api_scopes: str
    google_service_account: str
    google_workspace_admin_account: str
    service_account_file: str

    region_name: str
    aws_access_key_id: str
    aws_secret_access_key: str
    volunteer_s3_bucket: str
    aws_sqs_access_key: str
    aws_sqs_secret_access_key: str

    private_internal_token_key: str
    public_internal_token_key: str


@lru_cache
def get_settings() -> Settings:
    """Returns a cached instance of Settings."""
    return Settings()  # type: ignore[call-arg]

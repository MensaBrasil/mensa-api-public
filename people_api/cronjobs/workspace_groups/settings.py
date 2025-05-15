"""Settings for the Google Workspace cronjob uptime check."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for the Google Workspace cronjob uptime check."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    google_workspace_cronjob_uptime_url: str
    workspace_managers_email_list: list[str] = []


@lru_cache
def get_settings() -> Settings:
    """Returns a cached instance of Settings."""
    return Settings()  # type: ignore[call-arg]

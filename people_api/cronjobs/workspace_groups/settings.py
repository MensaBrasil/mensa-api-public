"""Settings for the Google Workspace cronjob uptime check."""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for the Google Workspace cronjob uptime check."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    google_workspace_cronjob_uptime_url: str

    google_workspace_admin_emails: list[str] = Field(
        default_factory=list, alias="google_workspace_admin_emails_raw"
    )

    @field_validator("google_workspace_admin_emails", mode="before")
    @classmethod
    def parse_admin_emails(cls, v):
        if isinstance(v, str):
            return [email.strip() for email in v.split(",") if email.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    """Returns a cached instance of Settings."""
    return Settings()  # type: ignore[call-arg]

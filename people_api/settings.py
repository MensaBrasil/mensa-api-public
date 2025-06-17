"""SETTINGS
Settings loaders using Pydantic BaseSettings classes (load from environment variables / dotenv file)
"""

__all__ = ("api_settings", "postgres_settings")

from decouple import config


class APISettings:
    title: str = config("API_TITLE", default="Mensa API")
    port: int = config("API_PORT", default=5000, cast=int)
    host: str = config("API_HOST", default="0.0.0.0")
    log_level: str = config("API_LOG_LEVEL", default="DEBUG")


class PostgresSettings:
    host: str = config("POSTGRE_HOST", default="127.0.0.1")
    user: str = config("POSTGRE_USER", default="postgres")
    password: str = config("POSTGRE_PASSWORD", default="postgres")
    database: str = config("POSTGRES_DATABASE", default="stats")


class DataRouteSettings:
    """Settings for the data endpoint"""

    data_api_key: str = config("DATA_ROUTE_API_KEY", None)
    whatsapp_api_key: str = config("WHATSAPP_ROUTE_API_KEY", None)


api_settings = APISettings()
postgres_settings = PostgresSettings()

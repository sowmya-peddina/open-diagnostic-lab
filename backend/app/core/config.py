from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Open Diagnostic Lab"
    secret_key: str = "change-me-in-production-use-long-random-string"
    database_url: str = "postgresql+psycopg2://lab:lab@localhost:5432/diagnostic_lab"
    session_max_age_seconds: int = 60 * 60 * 12  # 12 hours
    cookie_secure: bool = False  # set True behind HTTPS
    cookie_samesite: str = "lax"
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://localhost"
    clinic_name: str = "Open Diagnostic Lab"
    clinic_address: str = ""
    clinic_phone: str = ""
    clinic_footer: str = "This report is computer generated."
    admin_username: str = "admin"
    admin_password: str = "admin123"


@lru_cache
def get_settings() -> Settings:
    return Settings()

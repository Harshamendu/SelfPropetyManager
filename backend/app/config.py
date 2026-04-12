import json
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://propmanager:propmanager@db:5432/propmanager"
    sync_database_url: str = "postgresql://propmanager:propmanager@db:5432/propmanager"

    # Document storage
    document_storage_path: str = "/data/documents"

    # Email / SMTP
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_use_tls: bool = True

    # App
    app_name: str = "Self Property Manager"
    cors_origins: str = '["http://localhost","http://localhost:4200"]'

    # Auth / JWT
    jwt_secret_key: str = "change-me-in-production-use-a-long-random-string"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440  # 24 hours

    # Scheduler
    reminder_check_interval_minutes: int = 15

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        return json.loads(self.cors_origins)


settings = Settings()

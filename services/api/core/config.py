import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve path to .env.local relative to this config file location
_env_path = Path(__file__).parent.parent / ".env.local"

class Settings(BaseSettings):
    project_name: str = "AgroSaaS"
    version: str = "0.1.0"

    database_url: str = "sqlite+aiosqlite:///./agrosaas.db"
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str = "super_secret_for_development_change_in_production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7 # 7 days

    # Stripe Config
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    frontend_url: str = "http://localhost:3000"
    allow_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://0.0.0.0:3000",
        "http://0.0.0.0:3001",
        "http://local.agrosass.com.br:3000",
        "http://local.agrosass.com.br:3001",
    ]

    # Storage Config (local | s3 | minio)
    storage_backend: str = "local"
    storage_local_path: str = "/tmp/agrosaas_uploads"
    s3_bucket: str = ""
    s3_region: str = "us-east-1"
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_endpoint_url: str = ""  # MinIO: http://localhost:9000
    storage_max_file_mb: int = 50

    # SMTP Config
    smtp_host: str = "smtp.mailtrap.io"
    smtp_port: int = 2525
    smtp_user: str = ""
    smtp_pass: str = ""
    mail_from: str = "noreply@agrosaas.com.br"

    model_config = SettingsConfigDict(
        env_file=str(_env_path),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

import os
from pydantic_settings import BaseSettings, SettingsConfigDict

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

    # SMTP Config
    smtp_host: str = "smtp.mailtrap.io"
    smtp_port: int = 2525
    smtp_user: str = ""
    smtp_pass: str = ""
    mail_from: str = "noreply@agrosaas.com.br"
    
    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

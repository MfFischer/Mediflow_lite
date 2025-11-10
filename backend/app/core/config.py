from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = "MediFlow Lite"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"  # development, staging, production

    # API
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str = "sqlite:///./mediflow.db"
    postgres_url: Optional[str] = None  # For cloud sync

    # Security
    secret_key: str = "CHANGE_THIS_IN_PRODUCTION_USE_OPENSSL_RAND_HEX_32"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3005",
        "http://127.0.0.1:3005",
        "http://localhost:8000",
    ]

    # Rate Limiting
    rate_limit_per_minute: int = 60

    # SendGrid
    sendgrid_api_key: Optional[str] = None
    sendgrid_from_email: Optional[str] = None

    # Gemini AI
    gemini_api_key: Optional[str] = None

    # AI Assistant Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 2000

    # Local LLM (offline fallback)
    local_llm_enabled: bool = True
    local_llm_model_path: str = "./models/phi-3-mini-4k-instruct.gguf"
    local_llm_context_size: int = 4096
    local_llm_threads: int = 4

    # AI Settings
    ai_fallback_to_local: bool = True
    ai_max_context_messages: int = 10
    ai_temperature: float = 0.1

    # File Upload
    max_upload_size_mb: int = 10
    upload_dir: str = "./uploads"

    # Logging
    log_level: str = "INFO"

    # Compliance
    data_retention_days: int = 2555  # 7 years for medical records
    enable_audit_log: bool = True

    # Password Policy
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_digit: bool = True
    password_require_special: bool = True
    max_login_attempts: int = 5
    account_lockout_minutes: int = 30

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


settings = Settings()

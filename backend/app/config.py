"""
Configuration management for TaxCompass backend
Uses Pydantic Settings for environment variable handling
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "TaxCompass"
    DEBUG: bool = False

    # API
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Database
    DATABASE_URL: str = "postgresql://taxcompass:taxcompass@localhost:5432/taxcompass"
    DB_ECHO: bool = False

    # Vector Store (Qdrant)
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_NAME: str = "tax_documents"

    # LLM Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:latest"

    # Azure OpenAI (Fallback)
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_DEPLOYMENT: str = "gpt-4"
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"

    # Security
    SECRET_KEY: str = "CHANGE_THIS_IN_PRODUCTION"
    JWT_SECRET: str = "CHANGE_THIS_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Encryption
    MASTER_ENCRYPTION_KEY: str = "CHANGE_THIS_IN_PRODUCTION"

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".jpg", ".png"]

    # Rate Limiting
    RATE_LIMIT_PER_HOUR: int = 5

    # Payment (Stripe)
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Email
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@taxcompass.io"

    # Observability
    SENTRY_DSN: str = ""
    PHOENIX_ENABLED: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


settings = Settings()

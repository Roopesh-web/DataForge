from functools import lru_cache
import json
import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


class Settings(BaseModel):
    app_name: str = Field(default="DataForge")
    app_version: str = Field(default="1.0.0")
    app_env: Literal["development", "staging", "production"] = Field(default="development")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    database_host: str = Field(default="localhost")
    database_port: int = Field(default=5432)
    database_user: str = Field(default="dataforge")
    database_password: str = Field(default="dataforge")
    database_name: str = Field(default="dataforge")

    upload_dir: str = Field(default="uploads")
    max_upload_size_mb: int = Field(default=100)

    api_prefix: str = Field(default="/api/v1")
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8000"]
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                return json.loads(value)
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            app_name=os.getenv("APP_NAME", "DataForge"),
            app_version=os.getenv("APP_VERSION", "1.0.0"),
            app_env=os.getenv("APP_ENV", "development"),  # type: ignore[arg-type]
            debug=os.getenv("DEBUG", "false").lower() in {"1", "true", "yes"},
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            database_host=os.getenv("DATABASE_HOST", "localhost"),
            database_port=int(os.getenv("DATABASE_PORT", "5432")),
            database_user=os.getenv("DATABASE_USER", "dataforge"),
            database_password=os.getenv("DATABASE_PASSWORD", "dataforge"),
            database_name=os.getenv("DATABASE_NAME", "dataforge"),
            upload_dir=os.getenv("UPLOAD_DIR", "uploads"),
            max_upload_size_mb=int(os.getenv("MAX_UPLOAD_SIZE_MB", "100")),
            api_prefix=os.getenv("API_PREFIX", "/api/v1"),
            cors_origins=os.getenv(
                "CORS_ORIGINS",
                '["http://localhost:3000","http://localhost:8000"]',
            ),
        )

    @property
    def database_url(self) -> str:
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            if database_url.startswith("postgres://"):
                return database_url.replace("postgres://", "postgresql+psycopg://", 1)
            return database_url

        return (
            f"postgresql+psycopg://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    @property
    def upload_path(self) -> Path:
        path = BASE_DIR / self.upload_dir
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()


settings = get_settings()

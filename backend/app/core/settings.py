from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvironment(StrEnum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class AppPaths(BaseModel):
    model_config = ConfigDict(frozen=True)

    app_path: Path
    templates: Path
    static: Path


class DocsConfig(BaseModel):
    docs_url: str | None = None
    redoc_url: str | None = None
    openapi_url: str | None = None
    swagger_ui_parameters: dict[str, Any] | None = {
        "tryItOutEnabled": True,
        "displayRequestDuration": True,
        "persistAuthorization": True,
    }


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore", frozen=True, env_file=".env")

    environment: AppEnvironment
    api_prefix: str = "/api"
    http_client_timeout: int = 10

    logfire_token: str
    secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire: int = 15 * 60  # 15 minutes
    refresh_token_expire: int = 7 * 24 * 60 * 60  # 7 days

    mongo_user: str
    mongo_password: str
    mongo_host: str
    mongo_database: str
    supports_transactions: bool = True
    mongo_local: bool = False

    gotenberg_host: str

    @computed_field
    @property
    def docs(self) -> dict[str, Any]:
        config = DocsConfig()

        if self.environment == AppEnvironment.DEVELOPMENT:
            return config.model_dump(exclude={"docs_url", "openapi_url"})

        return config.model_dump()

    @computed_field
    @property
    def paths(self) -> AppPaths:
        app_path = Path(__file__).resolve().parents[1]
        return AppPaths(
            app_path=app_path,
            templates=app_path / "templates",
            static=app_path / "static",
        )

    @computed_field
    @property
    def mongo_uri(self) -> str:
        if self.mongo_local:
            return "mongodb://localhost:27017?replicaSet=rs0"

        pattern = "mongodb+srv://{user}:{password}@{host}"
        return pattern.format(
            user=self.mongo_user,
            password=self.mongo_password,
            host=self.mongo_host,
        )

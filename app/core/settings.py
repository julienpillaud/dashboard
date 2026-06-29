from pathlib import Path

from pydantic import BaseModel, ConfigDict, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppPaths(BaseModel):
    model_config = ConfigDict(frozen=True)

    app_path: Path
    templates: Path
    static: Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        frozen=True,
        env_file=".env",
    )

    secret_key: str
    http_client_timeout: int = 10

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire: int

    mongo_user: str
    mongo_password: str
    mongo_host: str
    mongo_database: str
    mongo_local: bool = False

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

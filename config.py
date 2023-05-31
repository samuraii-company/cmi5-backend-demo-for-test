import enum
import os
from pathlib import Path
from pydantic import AnyUrl, BaseSettings


class Environment(enum.StrEnum):
    local = "local"


class BaseDsnSettings(BaseSettings):
    name: str = "postgres"
    host: str = "postgres"
    username: str = "postgres"
    password: str = "postgres"
    port: int = 5432
    scheme: str = "tba"

    def get_dsn(self, db_name: str | None = None):
        return AnyUrl.build(
            scheme=self.scheme,
            user=self.username,
            password=self.password,
            host=self.host,
            port=str(self.port),
            path=f"/{db_name or self.db}",
        )


class PostgresSettings(BaseDsnSettings):
    scheme: str = "postgresql+asyncpg"

    class Config:
        env_prefix = "postgres_"


class S3Settings(BaseSettings):
    access_key_id: str = "aimu7OhSh4zei"  # not secure but this demo
    secret_access_key: str = "Maebee0xaeX6ohc"  # not secure but this demo
    bucket_name: str = "secure-t"
    endpoint_url: str = "minio:9000"
    region_name: str = "ru-central1"


class Settings(BaseSettings):
    root_dir = Path(__file__).absolute().root
    local_storage_dir = os.path.join(root_dir, "secure_t")
    environment: str = "local"
    static_url: str = "http://127.0.0.1:5000"
    storage_url: str = "http://127.0.0.1:9000"
    tag: str = "local"
    postgres_settings: PostgresSettings = PostgresSettings()
    s3_settings: S3Settings = S3Settings()

    @property
    def is_local(self) -> bool:
        return self.environment == Environment.local


settings = Settings()


def get_settings() -> Settings:
    return Settings()

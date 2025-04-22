from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class S3Config(BaseModel):
    path: str
    region_name: str | None = None
    access_key_id: str | None = None
    secret_access_key: str | None = None
    bucket_name: str = "test_bucket"
    chunk_size: int = 5 * 1024 * 1024
    max_file_size: int = 20 * 1024 * 1024


class DBConfig(BaseModel):
    uri: str


class _Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="file_service_")

    s3: S3Config
    db: DBConfig


Config = _Settings()

import os
from typing import Tuple, Type

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


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


class CeleryConfig(BaseModel):
    broker: str


class _Settings(BaseSettings):
    model_config = SettingsConfigDict(
        yaml_file=os.getenv("CONFIG_FILE", "./configs/config.yaml"),
        yaml_file_encoding="utf-8",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (YamlConfigSettingsSource(settings_cls),)

    s3: S3Config
    db: DBConfig
    celery: CeleryConfig


Config = _Settings()

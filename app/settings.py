import os
from functools import lru_cache
from typing import Optional
from google.auth import default
from google.auth.credentials import Credentials
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Path:
    app_dir: str = os.path.dirname(os.path.abspath(__file__))
    root_dir: str = os.path.dirname(app_dir)
    env_file: str = os.path.join(app_dir, ".env")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path.env_file, extra="ignore")
    PROJECT_ID: str = Field()
    PROJECT_LOCATION: str = Field()
    CREDENTIALS: Optional[Credentials] = None

@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    credentials, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    settings.CREDENTIALS = credentials
    return settings

config = get_settings()

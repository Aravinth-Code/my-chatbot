from functools import lru_cache
from sqlalchemy import URL
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    app_name: str
    app_version: str
    environment: str

    # Database
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )
    
    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
from typing import Literal

from anyio import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "DocsBox"
    MODE: Literal["DEV", "TEST", "PROD"] = "DEV"
    PROJECT_DIR: Path = Path(__file__).parent

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5433
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "docsbox"

    SECRET_KEY: str = "secret"

    FILES_PATH: Path = Path(__file__).parent.parent.joinpath("data", "files")

    @property
    def DATABASE_DSN(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()

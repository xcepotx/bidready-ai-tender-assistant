import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = os.getenv("ENVIRONMENT", "development")

    postgres_db: str = os.getenv("POSTGRES_DB", "tender_ai")
    postgres_user: str = os.getenv("POSTGRES_USER", "tender_user")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "tender_dev_password_change_me")
    postgres_host: str = os.getenv("POSTGRES_HOST", "postgres")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    database_url_override: str | None = os.getenv("DATABASE_URL")

    upload_dir: str = os.getenv("UPLOAD_DIR", "/app/uploads")
    export_dir: str = os.getenv("EXPORT_DIR", "/app/exports")

    @property
    def database_url(self) -> str:
        if self.database_url_override and self.database_url_override.startswith(("postgresql://", "postgresql+")):
            return self.database_url_override

        return (
            f"postgresql+psycopg://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()

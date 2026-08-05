from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str
    API_VERSION: str
    DEBUG: bool

    HOST: str
    PORT: int

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_URL: str | None = None

    # Supports both `settings.chroma_path` and `settings.CHROMA_PATH`
    chroma_path: str = Field(
        default="./chroma_db",
        validation_alias=AliasChoices("CHROMA_PATH", "chroma_path"),
    )

    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    EMBEDDING_MODEL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",  # Prevents crashes if extra env vars exist
        case_sensitive=False,  # Allows case-insensitive matching
    )

    @property
    def CHROMA_PATH(self) -> str:
        """Alias for backwards compatibility with uppercase access."""
        return self.chroma_path

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            "postgresql+psycopg://"
            f"{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}"
            f"/{self.DATABASE_NAME}"
        )


settings = Settings()

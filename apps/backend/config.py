from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    DATABASE_URL: str = "computer_use_v2.db"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB in bytes
    UPLOAD_DIR: str = "uploads"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

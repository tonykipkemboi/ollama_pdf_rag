"""Configuration settings for FastAPI application."""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""

    # Paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    PDF_STORAGE_DIR: str = "data/pdfs/uploads"
    VECTOR_DB_DIR: str = "data/vectors"

    # Database
    DATABASE_URL: str = "sqlite:///./data/api.db"

    # Ollama
    OLLAMA_HOST: str = "http://localhost:11434"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    DEFAULT_CHAT_MODEL: str = "llama3.2"

    class Config:
        """Pydantic config."""
        env_file = ".env"


settings = Settings()

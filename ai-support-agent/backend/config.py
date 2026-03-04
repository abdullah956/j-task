"""
Configuration module for ShopNest AI Support Agent
Centralizes all environment variables and configuration settings
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables"""

    # ========================================
    # Groq API Configuration
    # ========================================
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    GROQ_TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE", "0.7"))
    GROQ_MAX_TOKENS: int = int(os.getenv("GROQ_MAX_TOKENS", "512"))

    # ========================================
    # Backend Server Configuration
    # ========================================
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    BACKEND_RELOAD: bool = os.getenv("BACKEND_RELOAD", "true").lower() == "true"
    BACKEND_LOG_LEVEL: str = os.getenv("BACKEND_LOG_LEVEL", "info")

    # ========================================
    # Frontend Configuration
    # ========================================
    FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", "5173"))
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", f"http://localhost:{int(os.getenv('FRONTEND_PORT', '5173'))}")

    # ========================================
    # CORS Configuration
    # ========================================
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS",
        f"http://localhost:{int(os.getenv('FRONTEND_PORT', '5173'))}"
    ).split(",")
    CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    CORS_ALLOW_METHODS: List[str] = os.getenv("CORS_ALLOW_METHODS", "*").split(",")
    CORS_ALLOW_HEADERS: List[str] = os.getenv("CORS_ALLOW_HEADERS", "*").split(",")

    # ========================================
    # RAG Configuration
    # ========================================
    RAG_CHUNK_SIZE: int = int(os.getenv("RAG_CHUNK_SIZE", "300"))
    RAG_CHUNK_OVERLAP: int = int(os.getenv("RAG_CHUNK_OVERLAP", "50"))
    RAG_RETRIEVAL_K: int = int(os.getenv("RAG_RETRIEVAL_K", "3"))
    RAG_EMBEDDING_MODEL: str = os.getenv("RAG_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    RAG_EMBEDDING_DEVICE: str = os.getenv("RAG_EMBEDDING_DEVICE", "cpu")

    # ========================================
    # Database Configuration
    # ========================================
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./shopnest.db")

    # ========================================
    # Cache Configuration
    # ========================================
    SENTENCE_TRANSFORMERS_HOME: str = os.getenv("SENTENCE_TRANSFORMERS_HOME", "/app/.cache")
    HF_HOME: str = os.getenv("HF_HOME", "/app/.cache")
    TRANSFORMERS_OFFLINE: bool = os.getenv("TRANSFORMERS_OFFLINE", "0") == "1"

    @classmethod
    def validate(cls) -> None:
        """
        Validate required configuration values

        Raises:
            ValueError: If required configuration is missing
        """
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required but not set in environment variables")

    @classmethod
    def get_uvicorn_config(cls) -> dict:
        """
        Get uvicorn server configuration

        Returns:
            dict: Configuration dictionary for uvicorn.run()
        """
        return {
            "host": cls.BACKEND_HOST,
            "port": cls.BACKEND_PORT,
            "reload": cls.BACKEND_RELOAD,
            "log_level": cls.BACKEND_LOG_LEVEL
        }


# Initialize and validate configuration on module import
Config.validate()

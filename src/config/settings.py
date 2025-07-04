"""
Application settings and configuration
"""

import os
from typing import Set


class Settings:
    """Application settings with environment variable support"""

    def __init__(self):
        # Server Configuration
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"

        # API Configuration
        self.title: str = "Indic-Seamless Speech-to-Text Service"
        self.description: str = (
            "A production-ready REST API service for speech-to-text conversion "
            "using the ai4bharat/indic-seamless model"
        )
        self.version: str = "1.0.0"
        self.docs_url: str = "/docs"
        self.redoc_url: str = "/redoc"

        # CORS Configuration
        self.cors_origins: list = ["*"]
        self.cors_allow_credentials: bool = True
        self.cors_allow_methods: list = ["*"]
        self.cors_allow_headers: list = ["*"]

        # Model Configuration
        self.model_name: str = os.getenv("MODEL_NAME", "ai4bharat/indic-seamless")
        self.trust_remote_code: bool = (
            os.getenv("TRUST_REMOTE_CODE", "true").lower() == "true"
        )

        # Audio Processing Configuration
        self.allowed_extensions: Set[str] = {"wav", "mp3", "flac", "m4a", "ogg"}
        self.max_content_length: int = int(
            os.getenv("MAX_CONTENT_LENGTH", str(50 * 1024 * 1024))
        )  # 50MB
        self.target_sample_rate: int = int(os.getenv("TARGET_SAMPLE_RATE", "16000"))

        # Logging Configuration
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


# Global settings instance
settings = Settings()

"""
Logging configuration utilities
"""

import logging
import sys
from src.config.settings import settings


def setup_logging() -> None:
    """
    Setup application logging configuration.
    """
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=settings.log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific logger levels
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {settings.log_level}")
    
    # Suppress some noisy third-party loggers
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)
    logging.getLogger("torchaudio").setLevel(logging.WARNING) 
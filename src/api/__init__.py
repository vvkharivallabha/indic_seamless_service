"""API module for Indic-Seamless Service"""

from .routes import router
from .app import create_app

__all__ = ["router", "create_app"]

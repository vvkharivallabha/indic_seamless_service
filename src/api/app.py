"""
FastAPI application factory
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import settings
from src.utils import setup_logging
from .routes import router


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    # Setup logging
    setup_logging()

    # Create FastAPI app
    app = FastAPI(
        title=settings.title,
        description=settings.description,
        version=settings.version,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    # Include routes
    app.include_router(router)

    return app

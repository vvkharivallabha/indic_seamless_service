#!/usr/bin/env python3
"""
Structured Indic-Seamless Speech-to-Text Service
A FastAPI-based REST API service with organized code structure.
"""

import uvicorn
from src.api import create_app
from src.config.settings import settings


def main():
    """Main entry point for the application."""
    # Create the FastAPI app
    app = create_app()
    
    # Run the application
    uvicorn.run(
        app, 
        host=settings.host, 
        port=settings.port,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main() 
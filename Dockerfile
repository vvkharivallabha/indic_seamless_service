# Use Python 3.10 slim image for better performance and smaller size
FROM python:3.10-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/root/.local/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    sox \
    ffmpeg \
    libavdevice-dev \
    libfreetype6 \
    libportaudio2 \
    portaudio19-dev \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Set working directory
WORKDIR /app

# Copy project files for dependency resolution
COPY pyproject.toml README.md ./
COPY env/requirements.txt ./env/

# Install Python dependencies with uv (much faster!)
RUN uv pip install --system -r env/requirements.txt

# Copy application code
COPY src/ ./src/
COPY start_service.py ./
COPY .env ./

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Set default environment variables
ENV HOST=0.0.0.0
ENV PORT=8000
ENV DEBUG=false
ENV LOG_LEVEL=INFO
ENV MODEL_LOAD_TIMEOUT=600

# Expose port (using 8000 to match app_structured default)
EXPOSE 8000

# Health check - be more lenient during startup for model loading
HEALTHCHECK --interval=60s --timeout=60s --start-period=600s --retries=5 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run the structured application
# Using start_service.py as it handles .env loading and better error handling
CMD ["python", "start_service.py"] 
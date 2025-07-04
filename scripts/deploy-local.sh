#!/bin/bash

# Docker Deployment Script
# Builds and runs the Indic-Seamless service using Docker with structured app
# For development without Docker, use: ./run-local.sh

set -e

# Configuration
SERVICE_NAME="indic-seamless-service"
CONTAINER_NAME="indic-seamless-local"
HOST_PORT="${PORT:-8000}"  # Use env variable or default to 8000
CONTAINER_PORT="8000"      # Container internal port (matches Dockerfile)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_status "🐳 Starting Docker Deployment with Structured App..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed."
    print_status "For production deployment, please install Docker first."
    print_status "For development, you can use: ./run-local.sh"
    print_status "See docs/DOCKER_TROUBLESHOOTING.md for installation help."
    exit 1
fi

# Check if Docker daemon is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker daemon is not running."
    print_status "Please start Docker daemon:"
    print_status "  sudo systemctl start docker"
    print_status "  # or"
    print_status "  sudo service docker start"
    print_status ""
    print_status "For development without Docker, use: ./run-local.sh"
    print_status "For Docker troubleshooting, see: docs/DOCKER_TROUBLESHOOTING.md"
    exit 1
fi

print_status "✅ Docker is available and running"

# Check if port is available
if lsof -i ":${HOST_PORT}" >/dev/null 2>&1; then
    print_warning "Port ${HOST_PORT} is already in use"
    print_status "You can use a different port: PORT=8001 ./scripts/deploy-local.sh"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Stop and remove existing container if it exists
if docker ps -a --format 'table {{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    print_status "Stopping and removing existing container..."
    docker stop "${CONTAINER_NAME}" || true
    docker rm "${CONTAINER_NAME}" || true
fi

# Build Docker image with better caching
print_status "Building Docker image with uv optimization..."
docker build -t "${SERVICE_NAME}:latest" \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    .

# Run container with environment variables
print_status "Starting container on port ${HOST_PORT}..."
docker run -d \
    --name "${CONTAINER_NAME}" \
    -p "${HOST_PORT}:${CONTAINER_PORT}" \
    -e PORT="${CONTAINER_PORT}" \
    -e HOST="0.0.0.0" \
    -e DEBUG="${DEBUG:-false}" \
    -e LOG_LEVEL="${LOG_LEVEL:-INFO}" \
    --restart unless-stopped \
    "${SERVICE_NAME}:latest"

# Wait for service to be ready
print_status "Waiting for service to be ready..."
print_status "⏳ Model loading may take 5-10 minutes (large model, CPU-only)..."
sleep 30

# Check if service is running with retries
max_attempts=60  # Increased from 12 to allow 5+ minutes
attempt=1

while [ ${attempt} -le ${max_attempts} ]; do
    if curl -f "http://localhost:${HOST_PORT}/health" >/dev/null 2>&1; then
        print_status "✅ Service is running successfully!"
        echo ""
        echo "🌐 Service URL: http://localhost:${HOST_PORT}"
        echo "📚 API Documentation: http://localhost:${HOST_PORT}/docs"
        echo "🔍 Health Check: http://localhost:${HOST_PORT}/health"
        echo "🗂️  Supported Languages: http://localhost:${HOST_PORT}/supported-languages"
        echo ""
        echo "📋 Container Management:"
        echo "  View logs: docker logs ${CONTAINER_NAME}"
        echo "  Follow logs: docker logs -f ${CONTAINER_NAME}"
        echo "  Stop service: docker stop ${CONTAINER_NAME}"
        echo "  Remove container: docker rm ${CONTAINER_NAME}"
        echo "  Restart: docker restart ${CONTAINER_NAME}"
        echo ""
        echo "🧪 Test the service:"
        echo "  curl http://localhost:${HOST_PORT}/health"
        echo "  python tests/workflow_test.py --url http://localhost:${HOST_PORT}"
        exit 0
    fi
    
    # Show progress differently for different phases
    if [ ${attempt} -le 20 ]; then
        print_status "Model downloading/loading... (attempt ${attempt}/${max_attempts})"
    elif [ ${attempt} -le 40 ]; then
        print_status "Model still loading... (attempt ${attempt}/${max_attempts})"
    else
        print_status "Service not ready yet (attempt ${attempt}/${max_attempts})..."
    fi
    
    sleep 10  # Increased from 5 to 10 seconds
    attempt=$((attempt + 1))
done

print_error "❌ Service failed to start properly within expected time"
print_status "Container logs:"
docker logs "${CONTAINER_NAME}"
print_status ""
print_status "Troubleshooting:"
print_status "  Check logs: docker logs ${CONTAINER_NAME}"
print_status "  Check container: docker ps -a"
print_status "  Try interactive mode: docker run -it --rm ${SERVICE_NAME}:latest /bin/bash"
print_status "  For development: ./scripts/run-local.sh"
print_status "  For help: see docs/DOCKER_TROUBLESHOOTING.md"
exit 1 
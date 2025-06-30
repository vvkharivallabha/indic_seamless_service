#!/bin/bash

# Docker Deployment Script
# Builds and runs the Indic-Seamless service using Docker
# For development without Docker, use: ./run-local.sh

set -e

# Configuration
SERVICE_NAME="indic-seamless-service"
CONTAINER_NAME="indic-seamless-local"
PORT="5000"

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

print_status "🐳 Starting Docker Deployment..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed."
    print_status "For production deployment, please install Docker first."
    print_status "For development, you can use: ./run-local.sh"
    print_status "See DOCKER_TROUBLESHOOTING.md for installation help."
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
    print_status "For Docker troubleshooting, see: DOCKER_TROUBLESHOOTING.md"
    exit 1
fi

print_status "✅ Docker is available and running"

# Stop and remove existing container if it exists
if docker ps -a --format 'table {{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    print_status "Stopping and removing existing container..."
    docker stop "${CONTAINER_NAME}" || true
    docker rm "${CONTAINER_NAME}" || true
fi

# Build Docker image
print_status "Building Docker image..."
docker build -t "${SERVICE_NAME}:latest" .

# Run container
print_status "Starting container..."
docker run -d \
    --name "${CONTAINER_NAME}" \
    -p "${PORT}:5000" \
    --restart unless-stopped \
    "${SERVICE_NAME}:latest"

# Wait for service to be ready
print_status "Waiting for service to be ready..."
sleep 10

# Check if service is running
if curl -f "http://localhost:${PORT}/health" >/dev/null 2>&1; then
    print_status "✅ Service is running successfully!"
    echo ""
    echo "🌐 Service URL: http://localhost:${PORT}"
    echo "📚 API Documentation: http://localhost:${PORT}/docs"
    echo "🔍 Health Check: http://localhost:${PORT}/health"
    echo ""
    echo "📋 Container Management:"
    echo "  View logs: docker logs ${CONTAINER_NAME}"
    echo "  Stop service: docker stop ${CONTAINER_NAME}"
    echo "  Remove container: docker rm ${CONTAINER_NAME}"
    echo "  Restart: docker restart ${CONTAINER_NAME}"
else
    print_error "❌ Service failed to start properly"
    print_status "Container logs:"
    docker logs "${CONTAINER_NAME}"
    print_status ""
    print_status "Troubleshooting:"
    print_status "  Check logs: docker logs ${CONTAINER_NAME}"
    print_status "  Check container: docker ps -a"
    print_status "  For development: ./run-local.sh"
    exit 1
fi 
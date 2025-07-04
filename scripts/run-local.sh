#!/bin/bash

# Direct local deployment script (no Docker required)
# This script runs the service directly using Python with uv virtual environment

set -e

# Configuration
PORT="${PORT:-8000}"
DEBUG="${DEBUG:-false}"

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

# Function to check if virtual environment exists
check_environment() {
    if [ -f "env/.venv/bin/activate" ]; then
        return 0
    fi
    return 1
}

# Function to activate environment
activate_environment() {
    if [ -f "env/.venv/bin/activate" ]; then
        print_status "Activating virtual environment..."
        source env/.venv/bin/activate
        print_status "✅ Virtual environment activated"
        print_status "🐍 Python: $(python --version)"
        return 0
    else
        print_error "Virtual environment not found at env/.venv"
        return 1
    fi
}

# Function to check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    local missing_deps=()
    
    # Check critical Python packages
    if ! python -c "import torch" 2>/dev/null; then
        missing_deps+=("torch")
    fi
    
    if ! python -c "import transformers" 2>/dev/null; then
        missing_deps+=("transformers")
    fi
    
    if ! python -c "import fastapi" 2>/dev/null; then
        missing_deps+=("fastapi")
    fi
    
    if ! python -c "import uvicorn" 2>/dev/null; then
        missing_deps+=("uvicorn")
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        print_status "Please run: make fix-deps"
        print_status "Or manually: cd env && source .venv/bin/activate && uv pip install -r requirements.txt"
        return 1
    fi
    
    print_status "✅ All dependencies are available"
    return 0
}

# Function to start the service
start_service() {
    print_status "Starting Indic-Seamless Service..."
    
    # Set environment variables
    export PORT="${PORT}"
    export DEBUG="${DEBUG}"
    
    # Check if port is available
    if lsof -i ":${PORT}" >/dev/null 2>&1; then
        print_error "Port ${PORT} is already in use"
        print_status "Available options:"
        print_status "1. Kill existing process: lsof -ti:${PORT} | xargs kill"
        print_status "2. Use different port: PORT=8001 ./run-local.sh"
        return 1
    fi
    
    print_status "Starting service on port ${PORT}..."
    print_status "Debug mode: ${DEBUG}"
    
    # Start the service
    python start_service.py --port "${PORT}" &
    SERVICE_PID=$!
    
    print_status "Service started with PID: ${SERVICE_PID}"
    
    # Wait for service to start
    print_status "Waiting for service to initialize..."
    sleep 5
    
    # Test if service is responding
    local max_attempts=12
    local attempt=1
    
    while [ ${attempt} -le ${max_attempts} ]; do
        if curl -f "http://localhost:${PORT}/health" >/dev/null 2>&1; then
            print_status "✅ Service is running successfully!"
            echo ""
            echo "🌐 Service URL: http://localhost:${PORT}"
            echo "📚 API Documentation: http://localhost:${PORT}/docs"
            echo "🔍 Health Check: http://localhost:${PORT}/health"
            echo "🔧 Process ID: ${SERVICE_PID}"
            echo ""
            echo "📋 To stop the service:"
            echo "   kill ${SERVICE_PID}"
            echo "   # or"
            echo "   pkill -f 'python start_service.py'"
            echo ""
            echo "📊 To monitor logs:"
            echo "   tail -f logs/service.log"
            echo ""
            return 0
        fi
        
        print_status "Service not ready yet (attempt ${attempt}/${max_attempts})..."
        sleep 5
        attempt=$((attempt + 1))
    done
    
    print_error "❌ Service failed to start within expected time"
    print_status "Checking if process is still running..."
    
    if kill -0 "${SERVICE_PID}" 2>/dev/null; then
        print_warning "Service process is running but not responding to health checks"
        print_status "Check logs for errors: tail -f logs/service.log"
    else
        print_error "Service process has died"
    fi
    
    return 1
}

# Main execution
print_status "🚀 Starting Direct Local Deployment (No Docker)"
echo "================================================"

# Check if environment setup is needed
if ! check_environment; then
    print_error "Virtual environment not found at env/.venv"
    print_status "Please run setup first:"
    print_status "  make setup"
    print_status "  # or"
    print_status "  cd env && ./setup.sh"
    exit 1
fi

# Activate environment
if ! activate_environment; then
    exit 1
fi

# Check dependencies
if ! check_dependencies; then
    exit 1
fi

# Start the service
if start_service; then
    print_status "🎉 Deployment successful!"
    
    # Keep script running to show it's active
    echo ""
    print_status "Press Ctrl+C to stop the service"
    
    # Wait for interrupt
    trap 'print_status "Stopping service..."; kill ${SERVICE_PID} 2>/dev/null; exit 0' INT TERM
    
    # Monitor the service
    while kill -0 "${SERVICE_PID}" 2>/dev/null; do
        sleep 10
    done
    
    print_warning "Service process has stopped"
else
    print_error "❌ Deployment failed"
    exit 1
fi 
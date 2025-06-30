# Makefile for Indic-Seamless Service
# Usage: make <target>

.PHONY: help setup clean test docker-build docker-run docker-stop deploy-local run-local lint format check-deps benchmark

# Default target
help:
	@echo "🚀 Indic-Seamless Service - Available Commands:"
	@echo ""
	@echo "📦 Environment & Setup:"
	@echo "  setup          - Setup conda environment and dependencies"
	@echo "  clean          - Clean cache files and temporary directories"
	@echo "  check-deps     - Check and validate dependencies"
	@echo ""
	@echo "🧪 Development & Testing:"
	@echo "  test           - Run all tests"
	@echo "  test-unit      - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  lint           - Run code linting"
	@echo "  format         - Format code with black"
	@echo "  benchmark      - Run performance benchmarks"
	@echo ""
	@echo "🚀 Deployment:"
	@echo "  run-local      - Run service locally (development mode)"
	@echo "  deploy-local   - Deploy with Docker locally"
	@echo "  docker-build   - Build Docker image"
	@echo "  docker-run     - Run Docker container"
	@echo "  docker-stop    - Stop Docker container"
	@echo ""
	@echo "📊 Monitoring:"
	@echo "  logs           - View service logs"
	@echo "  health         - Check service health"
	@echo "  status         - Show service status"
	@echo ""

# Environment Setup
setup:
	@echo "🔧 Setting up environment..."
	cd env && ./setup.sh

clean:
	@echo "🧹 Cleaning up..."
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	find . -name ".mypy_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	docker system prune -f 2>/dev/null || true

check-deps:
	@echo "📋 Checking dependencies..."
	cd env && python -c "import requirements; print('Dependencies OK')" 2>/dev/null || echo "❌ Dependencies check failed"

# Development & Testing
test: test-unit test-integration

test-unit:
	@echo "🧪 Running unit tests..."
	python -m pytest tests/test_service.py -v

test-integration:
	@echo "🔄 Running integration tests..."
	python tests/workflow_test.py

lint:
	@echo "🔍 Running linter..."
	python -m flake8 app.py start_service.py tests/ examples/ --max-line-length=88 --ignore=E203,W503

format:
	@echo "✨ Formatting code..."
	python -m black app.py start_service.py tests/ examples/ --line-length=88

benchmark:
	@echo "📊 Running benchmarks..."
	cd env && python benchmark.py

# Local Development
run-local:
	@echo "🚀 Starting local development server..."
	./scripts/run-local.sh

# Docker Operations
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t indic-seamless-service:latest .

docker-run: docker-build
	@echo "🚀 Running Docker container..."
	docker run -d --name indic-seamless-local -p 8000:5000 indic-seamless-service:latest

docker-stop:
	@echo "🛑 Stopping Docker container..."
	docker stop indic-seamless-local 2>/dev/null || true
	docker rm indic-seamless-local 2>/dev/null || true

deploy-local:
	@echo "🚀 Deploying locally with Docker..."
	./scripts/deploy-local.sh

# Monitoring
logs:
	@echo "📄 Viewing service logs..."
	docker logs indic-seamless-local 2>/dev/null || echo "❌ No container running"

health:
	@echo "🏥 Checking service health..."
	curl -s http://localhost:8000/health | python -m json.tool 2>/dev/null || echo "❌ Service not responding"

status:
	@echo "📊 Service status:"
	@docker ps | grep indic-seamless || echo "❌ No containers running"
	@lsof -i :8000 2>/dev/null | head -2 || echo "❌ Port 8000 not in use"

# Quick development cycle
dev: clean setup run-local

# Full test cycle
ci: clean setup test lint

# Production deployment check
prod-check: clean setup test docker-build
	@echo "✅ Production deployment ready!" 
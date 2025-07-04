# Makefile for Indic-Seamless Service
# Usage: make <target>

.PHONY: help setup clean test docker-build docker-run docker-stop deploy-local run-local lint format check-deps benchmark fix-deps activate

# Default target
help:
	@echo "🚀 Indic-Seamless Service - Available Commands:"
	@echo ""
	@echo "📦 Environment & Setup:"
	@echo "  setup          - Setup virtual environment and dependencies with uv"
	@echo "  setup-env      - Create .env file from template for configuration"
	@echo "  activate       - Show how to activate the virtual environment"
	@echo "  fix-deps       - Fix common dependency issues"
	@echo "  clean          - Clean cache files and temporary directories"
	@echo "  check-deps     - Check and validate dependencies"
	@echo "  check-auth     - Check Hugging Face authentication"
	@echo "  compile-deps   - Compile dependencies with uv"
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
	@echo "  run-structured - Run structured application"
	@echo "  deploy-local   - Deploy with Docker locally"
	@echo "  docker-build   - Build Docker image"
	@echo "  docker-run     - Run Docker container"
	@echo "  docker-stop    - Stop Docker container"
	@echo ""
	@echo "🔧 Troubleshooting:"
	@echo "  install-essentials - Install only essential packages"
	@echo "  setup-auth     - Setup Hugging Face authentication"
	@echo "  logs           - View service logs"
	@echo "  health         - Check service health"
	@echo "  status         - Show service status"
	@echo ""

# Environment Setup
setup:
	@echo "🔧 Setting up environment with uv..."
	cd env && ./setup.sh
	@echo ""
	@echo "🎉 Setup complete! Virtual environment is ready."
	@echo "To activate the environment, run:"
	@echo "   source env/.venv/bin/activate"
	@echo ""
	@echo "Or use this command to activate and start development:"
	@echo "   source env/.venv/bin/activate && python start_service.py"

activate:
	@echo "🔧 To activate the virtual environment, run:"
	@echo "   source env/.venv/bin/activate"
	@echo ""
	@echo "Or use this one-liner:"
	@echo "   cd env && source .venv/bin/activate"

compile-deps:
	@echo "📦 Compiling dependencies with uv..."
	@if command -v uv >/dev/null 2>&1; then \
		echo "⚡ Using uv for dependency compilation..."; \
		cd env && uv pip compile requirements.in --output-file requirements.txt; \
	else \
		echo "⚠️  uv not found, installing it first..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		export PATH="$$HOME/.local/bin:$$PATH"; \
		cd env && uv pip compile requirements.in --output-file requirements.txt; \
	fi

fix-deps:
	@echo "🔧 Fixing common dependency issues with uv..."
	@if [ ! -f "env/.venv/bin/activate" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@if command -v uv >/dev/null 2>&1; then \
		echo "⚡ Using uv for faster installation..."; \
		cd env && source .venv/bin/activate && \
		uv pip install torch==2.7.1 || echo "❌ Failed to install torch"; \
		uv pip install torchaudio==2.7.1 || echo "❌ Failed to install torchaudio"; \
		uv pip install transformers==4.53.1 || echo "❌ Failed to install transformers"; \
		uv pip install fastapi==0.115.14 || echo "❌ Failed to install fastapi"; \
		uv pip install 'uvicorn[standard]==0.35.0' || echo "❌ Failed to install uvicorn"; \
		uv pip install python-multipart==0.0.20 || echo "❌ Failed to install python-multipart"; \
		uv pip install librosa==0.11.0 || echo "❌ Failed to install librosa"; \
		uv pip install numpy==1.26.4 || echo "❌ Failed to install numpy"; \
		uv pip install requests==2.32.4 || echo "❌ Failed to install requests"; \
		uv pip install huggingface-hub==0.33.2 || echo "❌ Failed to install huggingface-hub"; \
	else \
		echo "⚠️  uv not found, please run 'make setup' first"; \
		exit 1; \
	fi
	@echo "✅ Essential packages installation completed"

install-essentials:
	@echo "🔧 Installing only essential packages for basic functionality..."
	@if [ ! -f "env/.venv/bin/activate" ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@if command -v uv >/dev/null 2>&1; then \
		echo "⚡ Using uv for faster installation..."; \
		cd env && source .venv/bin/activate && \
		uv pip install torch torchaudio transformers fastapi 'uvicorn[standard]' python-multipart librosa numpy requests huggingface-hub; \
	else \
		echo "⚠️  uv not found, please run 'make setup' first"; \
		exit 1; \
	fi
	@echo "✅ Essential packages installed"

clean:
	@echo "🧹 Cleaning up..."
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	find . -name ".mypy_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	# Clean uv cache
	@if command -v uv >/dev/null 2>&1; then \
		echo "🧹 Cleaning uv cache..."; \
		uv cache clean; \
	fi
	# Remove virtual environment
	@if [ -d "env/.venv" ]; then \
		echo "🧹 Removing virtual environment..."; \
		rm -rf env/.venv; \
	fi
	docker system prune -f 2>/dev/null || true

check-deps:
	@echo "📋 Checking dependencies..."
	@echo "Checking uv installation..."
	@if command -v uv >/dev/null 2>&1; then \
		echo "✅ uv: $$(uv --version)"; \
	else \
		echo "❌ uv not installed - run 'make setup'"; \
		exit 1; \
	fi
	@echo "Checking virtual environment..."
	@if [ -f "env/.venv/bin/activate" ]; then \
		echo "✅ Virtual environment exists at env/.venv"; \
		cd env && source .venv/bin/activate && echo "✅ Python: $$(python --version)"; \
	else \
		echo "❌ Virtual environment not found - run 'make setup'"; \
		exit 1; \
	fi
	@echo "Checking essential packages..."
	@cd env && source .venv/bin/activate && \
	python -c "import torch; print('✅ torch:', torch.__version__)" || echo "❌ torch not found"; \
	python -c "import transformers; print('✅ transformers:', transformers.__version__)" || echo "❌ transformers not found"; \
	python -c "import fastapi; print('✅ fastapi:', fastapi.__version__)" || echo "❌ fastapi not found"; \
	python -c "import uvicorn; print('✅ uvicorn:', uvicorn.__version__)" || echo "❌ uvicorn not found"; \
	python -c "import librosa; print('✅ librosa:', librosa.__version__)" || echo "❌ librosa not found"

check-auth:
	@echo "🔍 Checking Hugging Face authentication..."
	@if [ -f "env/.venv/bin/activate" ]; then \
		cd env && source .venv/bin/activate && \
		python -c "from huggingface_hub import HfApi; print('✅ Authenticated as:', HfApi().whoami()['name'])" || echo "❌ Not authenticated or huggingface-hub not installed"; \
	else \
		echo "❌ Virtual environment not found - run 'make setup'"; \
	fi

setup-auth:
	@echo "🔐 Setting up Hugging Face authentication..."
	@echo "1. Visit: https://huggingface.co/ai4bharat/indic-seamless"
	@echo "2. Request access to the model"
	@echo "3. Make sure huggingface-hub is installed:"
	@echo "   source env/.venv/bin/activate && uv pip install huggingface-hub"
	@echo "4. Run the following command and enter your token:"
	@echo "   huggingface-cli login"

setup-env:
	@echo "📝 Setting up .env file..."
	@if [ ! -f ".env" ]; then \
		echo "Creating .env from env.example..."; \
		cp env.example .env; \
		echo "✅ .env file created from env.example"; \
		echo ""; \
		echo "📝 Next steps:"; \
		echo "1. Edit .env file and set your HF_TOKEN:"; \
		echo "   nano .env"; \
		echo "2. Get your token from: https://huggingface.co/settings/tokens"; \
		echo "3. Set: HF_TOKEN=your_token_here"; \
		echo "4. Request access: https://huggingface.co/ai4bharat/indic-seamless"; \
	else \
		echo "✅ .env file already exists"; \
		echo "💡 Edit it to update your configuration: nano .env"; \
	fi

# Development & Testing
test: test-unit test-integration

test-unit:
	@echo "🧪 Running unit tests..."
	@cd env && source .venv/bin/activate && cd .. && python -m pytest tests/test_service.py -v

test-integration:
	@echo "🔄 Running integration tests..."
	@cd env && source .venv/bin/activate && cd .. && python tests/workflow_test.py

lint:
	@echo "🔍 Running linter..."
	@cd env && source .venv/bin/activate && cd .. && python -m flake8 start_service.py tests/ examples/ src/ --max-line-length=88 --ignore=E203,W503

format:
	@echo "✨ Formatting code..."
	@cd env && source .venv/bin/activate && cd .. && python -m black start_service.py tests/ examples/ src/ --line-length=88

benchmark:
	@echo "📊 Running benchmarks..."
	@cd env && source .venv/bin/activate && python benchmark.py

# Local Development
run-local:
	@echo "🚀 Starting local development server..."
	@echo "Checking dependencies first..."
	@make check-deps
	@echo "Starting service..."
	@cd env && source .venv/bin/activate && cd .. && ./scripts/run-local.sh

run-service:
	@echo "🚀 Starting service launcher..."
	@echo "Checking dependencies first..."
	@make check-deps
	@echo "Starting service..."
	@echo "⚠️  If you see model loading errors, run: make setup-auth"
	@cd env && source .venv/bin/activate && cd .. && python start_service.py

# Docker Operations
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t indic-seamless-service:latest .

docker-run:
	@echo "Running Docker container..."
	docker run -d --name indic-seamless-local -p 8000:8000 indic-seamless-service:latest

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

# Quick fix for common issues
quick-fix: clean fix-deps
	@echo "🔧 Quick fix completed. Try running the service again." 
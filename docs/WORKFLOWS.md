# Development Workflows

This document outlines recommended workflows for developing and maintaining the Indic-Seamless service.

## Daily Development Workflow

### 1. Environment Setup (One-time)
```bash
# Initial setup with uv
cd env
./setup.sh

# Verify installation
source .venv/bin/activate
python --version
```

### 2. Daily Development Start
```bash
# Activate environment
source env/.venv/bin/activate

# Or use the helper script
source env/activate.sh

# Start development server
python start_service.py
```

### 3. Development Cycle

#### Code Changes
```bash
# Make your changes
nano start_service.py

# Test changes
python tests/workflow_test.py

# Or run specific tests
python tests/test_service.py
```

#### Environment Management
```bash
# Check environment status
make check-deps

# Install new dependencies
uv pip install some-package

# Update requirements
cd env
uv pip compile requirements.in --output-file requirements.txt
```

### 4. Testing Workflow

#### Unit Tests
```bash
# Run all tests
make test

# Run specific test file
python -m pytest tests/test_service.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

#### Integration Tests
```bash
# Test the complete workflow
python tests/workflow_test.py

# Test with specific audio file
python tests/workflow_test.py --audio sample.wav

# Test different service endpoint
python tests/workflow_test.py --url http://localhost:8001
```

## Production Deployment Workflow

### 1. Local Testing
```bash
# Test Docker build
make docker-build

# Test deployment
make deploy-local

# Verify service
curl http://localhost:8000/health
```

### 2. Environment Preparation
```bash
# Clean environment
make clean

# Fresh setup
make setup

# Verify all dependencies
make check-deps
```

### 3. Docker Deployment
```bash
# Build production image
docker build -t indic-seamless-service:latest .

# Run container
docker run -d \
  --name indic-seamless-prod \
  -p 8000:5000 \
  -e DEBUG=false \
  indic-seamless-service:latest

# Monitor logs
docker logs -f indic-seamless-prod
```

### 4. AWS Deployment
```bash
# Deploy to ECS
cd aws
./deploy.sh

# Monitor deployment
aws ecs describe-services \
  --cluster indic-seamless-cluster \
  --services indic-seamless-service
```

## Maintenance Workflow

### 1. Dependency Updates
```bash
# Activate environment
source env/.venv/bin/activate

# Update dependencies with uv
cd env
uv pip compile requirements.in --upgrade --output-file requirements.txt
uv pip install -r requirements.txt

# Test after updates
make test
```

### 2. Security Updates
```bash
# Check for vulnerabilities
uv pip audit

# Update specific packages
uv pip install --upgrade package-name

# Verify fixes
python tests/workflow_test.py
```

### 3. Performance Monitoring
```bash
# Run performance benchmark
source env/.venv/bin/activate
python env/benchmark.py

# Check resource usage
docker stats indic-seamless-prod

# Monitor service health
curl http://localhost:8000/health
```

## Troubleshooting Workflow

### 1. Environment Issues
```bash
# Check environment
source env/.venv/bin/activate
python --version
which python

# Check dependencies
make check-deps

# Reset environment if needed
make clean setup
```

### 2. Service Issues
```bash
# Check if service is running
lsof -i :8000

# Check logs
tail -f logs/service.log

# Debug mode
export DEBUG=true
python start_service.py
```

### 3. Model Issues
```bash
# Check authentication
make check-auth

# Setup authentication
make setup-auth
huggingface-cli login

# Test model loading
python -c "from transformers import AutoProcessor; AutoProcessor.from_pretrained('ai4bharat/indic-seamless')"
```

## Emergency Procedures

### 1. Service Down
```bash
# Check if process is running
ps aux | grep python

# Kill hanging processes
pkill -f "python start_service.py"

# Restart service
source env/.venv/bin/activate
python start_service.py &
```

### 2. High Resource Usage
```bash
# Check system resources
top
df -h

# Clean up
make clean
docker system prune -f

# Restart with resource limits
docker run -d \
  --name indic-seamless-prod \
  --memory=4g \
  --cpus=2 \
  -p 8000:5000 \
  indic-seamless-service:latest
```

### 3. Dependency Conflicts
```bash
# Clean environment
make clean

# Fresh setup
make setup

# Install minimal dependencies
make install-essentials

# Test basic functionality
python tests/workflow_test.py
```

## Quality Assurance Workflow

### 1. Code Quality
```bash
# Run linter
make lint

# Format code
make format

# Type checking
mypy src/ --ignore-missing-imports
```

### 2. Testing
```bash
# Run all tests
make test

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=term-missing

# Performance tests
python env/benchmark.py
```

### 3. Documentation
```bash
# Update documentation
nano docs/README.md

# Generate API docs
python -c "import app; print(app.app.openapi())" > docs/openapi.json

# Test documentation links
markdown-link-check docs/*.md
```

## Quick Reference

### Essential Commands
| Task | Command |
|------|---------|
| **Setup** | `make setup` |
| **Activate** | `source env/.venv/bin/activate` |
| **Start Service** | `python start_service.py` |
| **Run Tests** | `make test` |
| **Build Docker** | `make docker-build` |
| **Deploy Local** | `make deploy-local` |
| **Check Health** | `curl http://localhost:8000/health` |
| **View Logs** | `docker logs -f indic-seamless-local` |
| **Clean Up** | `make clean` |

### Environment Variables
```bash
# Development
export DEBUG=true
export PORT=8001

# Production
export DEBUG=false
export PORT=8000
export MODEL_CACHE_DIR=/opt/models
```

### Common Issues
- **Import errors**: Run `make fix-deps`
- **Service won't start**: Check `lsof -i :8000`
- **Model loading fails**: Run `make setup-auth`
- **Performance issues**: Run `python env/benchmark.py`

## Pre-deployment Checklist

- [ ] Environment setup completed with `make setup`
- [ ] All tests passing with `make test`
- [ ] Dependencies checked with `make check-deps`
- [ ] Authentication configured with `make setup-auth`
- [ ] Docker build successful
- [ ] Service responds to health checks
- [ ] Performance benchmarks acceptable
- [ ] Documentation updated
- [ ] Security scan completed 
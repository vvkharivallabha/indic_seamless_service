# Indic-Seamless Speech-to-Text Service

A production-ready REST API service for speech-to-text conversion using the [ai4bharat/indic-seamless](https://huggingface.co/ai4bharat/indic-seamless) model. This service provides high-quality speech recognition for 100+ languages, with special focus on Indian languages.

---

## 🚀 Quick Start

> 💡 **Pro Tip**: Use `make help` to see all available commands!

> ⚡ **Performance Boost**: This project uses [uv](https://github.com/astral-sh/uv) for lightning-fast package management and virtual environments!

### **🚀 Option 1: Using Makefile (Recommended)**

```bash
# Setup environment with uv (much faster!)
make setup

# Setup environment variables for gated model access
make setup-env
# Edit the .env file and add your HuggingFace token
nano .env

# Deploy and run
make deploy-local

# Or for development mode
source env/.venv/bin/activate
python start_service.py       # Production service launcher

# Run tests
make test

# View all available commands
make help
```

### **🔧 Option 2: Manual Setup**

1. **Set up your environment:**

   ```bash
   cd env
   ./setup.sh
   ```

   This will install uv (if needed), create a virtual environment, and install all dependencies.

2. **Configure environment variables (Important for gated models!):**

   ```bash
   # Create .env file from template
   cp env.example .env

   # Edit .env and add your HuggingFace token
   nano .env
   # Set: HF_TOKEN=your_huggingface_token
   ```

3. **To activate the environment later:**

   ```bash
   source env/.venv/bin/activate
   # or use the helper script
   source env/activate.sh
   ```

4. **Start the service:**

   ```bash
   python start_service.py      # Production launcher
   # or with custom port
   python start_service.py --port 8001
   ```

   The service will start on `http://localhost:8000`

5. **Test the service:**
   ```bash
   python tests/workflow_test.py
   # or
   python examples/client_example.py
   ```

### **🔑 Authentication Setup (Required for gated models)**

The `ai4bharat/indic-seamless` model is gated and requires authentication:

1. **Get HuggingFace Access:**

   - Visit: https://huggingface.co/ai4bharat/indic-seamless
   - Request access to the model
   - Get your token from: https://huggingface.co/settings/tokens

2. **Configure Authentication (Choose one method):**

   **Method 1: Using .env file (Recommended)**

   ```bash
   make setup-env
   nano .env
   # Set: HF_TOKEN=your_token_here
   ```

   **Method 2: Using huggingface-cli**

   ```bash
   source env/.venv/bin/activate
   huggingface-cli login
   # Enter your token when prompted
   ```

3. **Verify Authentication:**
   ```bash
   python start_service.py --check-only
   # Should show: ✅ Authenticated as: your_username
   ```

---

## ⚡ uv Package Manager

This project uses [uv](https://github.com/astral-sh/uv) for **both virtual environment management and package installation**:

### Benefits:

- **10-100x faster** than pip for package installation
- **Blazing fast virtual environment creation** (seconds instead of minutes)
- **Better dependency resolution** with fewer conflicts
- **Automatic virtual environment management**
- **Compatible with pip** - drop-in replacement
- **Lockfile support** for reproducible builds
- **No conda needed** - simplified toolchain

### uv Commands:

```bash
# Create virtual environment
uv venv .venv --python 3.10

# Install dependencies (much faster than pip)
uv pip install -r requirements.txt

# Install from pyproject.toml
uv pip install -e .

# Install with specific extras
uv pip install -e ".[dev]"

# Install specific packages
uv pip install torch transformers

# Clean cache
uv cache clean
```

### Environment Management:

```bash
# Activate virtual environment
source env/.venv/bin/activate

# Deactivate
deactivate

# Quick activation helper
source env/activate.sh
```

---

## 📋 API Endpoints

| Endpoint               | Method | Description              |
| ---------------------- | ------ | ------------------------ |
| `/`                    | GET    | Service information      |
| `/health`              | GET    | Health check             |
| `/supported-languages` | GET    | List supported languages |
| `/speech-to-text`      | POST   | Convert speech to text   |

### Example: Speech-to-Text

**Python:**

```python
import requests
with open('audio.wav', 'rb') as audio_file:
    files = {'audio': audio_file}
    data = {'source_lang': 'eng'}
    response = requests.post('http://localhost:8000/speech-to-text', files=files, data=data)
    print(response.json())
```

**cURL:**

```bash
curl -X POST "http://localhost:8000/speech-to-text" \
  -F "audio=@audio.wav" \
  -F "source_lang=eng"
```

---

## 🌐 Supported Languages & Formats

- **Audio formats:** WAV, MP3, FLAC, M4A, OGG
- **Languages:** 100+ including all major Indian and many international languages
- **FastAPI Docs:** Interactive dropdown now shows full language names (e.g., "Hindi", "Bengali", "Tamil") instead of codes

---

## 🧪 Testing

- Place audio files in the service directory (e.g., `test_audio.wav`, `sample.mp3`)
- Run:
  ```bash
  python tests/workflow_test.py
  # or test a specific file
  python tests/workflow_test.py --audio your_audio.wav
  # or test a different service URL
  python tests/workflow_test.py --url http://localhost:8001
  ```

---

## 🐳 Docker & Local Deployment

> 🔧 **Docker Issues?** See [`DOCKER_TROUBLESHOOTING.md`](DOCKER_TROUBLESHOOTING.md) for solutions.

### Docker Deployment

```bash
# Automated Docker deployment
./scripts/deploy-local.sh

# Manual Docker build and run
docker build -t indic-seamless-stt .
docker run -p 8000:5000 indic-seamless-stt
```

### Direct Python (Development)

```bash
# For development without Docker
./scripts/run-local.sh

# Or manually
source env/.venv/bin/activate
python start_service.py
```

---

## ☁️ AWS & SageMaker Deployment

### AWS Lambda (Serverless) ⚡

```bash
# Set HuggingFace token
export HF_TOKEN="your_token_here"

# Deploy to Lambda
./aws/lambda/deploy-lambda.sh

# Test deployment
curl https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/health
```

📋 **Lambda Guide**: See [`LAMBDA_DEPLOYMENT.md`](docs/LAMBDA_DEPLOYMENT.md) for complete Lambda deployment instructions.

### ECS with CloudFormation

```bash
aws cloudformation create-stack \
  --stack-name indic-seamless-stt \
  --template-body file://aws/cloudformation.yaml \
  --capabilities CAPABILITY_IAM
```

### ECS with Terraform

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### SageMaker

```bash
python sagemaker/deploy.py
```

---

## 🔧 Troubleshooting

### Quick Fixes

```bash
# Fix common dependency issues
make fix-deps

# Setup .env file for authentication
make setup-env

# Check if everything is working
make check-deps

# Check authentication
make check-auth

# Complete reset if needed
make clean setup
```

### Common Issues

1. **Missing dependencies** (uvicorn, torch, python-multipart)

   ```bash
   make fix-deps
   ```

2. **Virtual environment not found**

   ```bash
   make setup
   ```

3. **Model loading fails** (authentication issue)

   ```bash
   make setup-env
   # Edit .env and set HF_TOKEN=your_token
   # Or use: make setup-auth
   ```

4. **Service won't start**

   ```bash
   python start_service.py --check-only
   lsof -i :8000
   ```

5. **Audio processing errors**
   - Verify audio file format is supported
   - Check file is not corrupted
   - Ensure audio has speech content

**Debug mode:**

```bash
export DEBUG=true
python start_service.py
```

📋 **Detailed troubleshooting**: See [`TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) for complete solutions.

---

## 🔄 Recommended Workflows

> 📋 **Quick Reference**: See [`WORKFLOWS.md`](WORKFLOWS.md) for a printable workflow cheat sheet.

### **Development Workflow**

#### Initial Setup (One-time)

```bash
# Clone and setup environment
git clone <repository-url>
cd indic_seamless_service
cd env && ./setup.sh
```

#### Daily Development

```bash
# Activate environment
source env/.venv/bin/activate
# or use helper script
source env/activate.sh

# Start development server
python start_service.py

# In another terminal, test your changes
python tests/workflow_test.py
```

#### Environment Management

```bash
# Check environment status
make check-deps

# Update dependencies with uv (super fast!)
make compile-deps
source env/.venv/bin/activate
uv pip install -r env/requirements.txt

# Or install from pyproject.toml
uv pip install -e .

# Benchmark performance
python benchmark.py
```

### **Local Testing Workflow**

#### Test Docker Build Locally

```bash
# Build and run with Docker
./scripts/deploy-local.sh

# Check service status
curl http://localhost:5000/health

# View logs
docker logs indic-seamless-local

# Stop service
docker stop indic-seamless-local
```

#### Manual Docker Testing

```bash
# Build image
docker build -t indic-seamless-service:latest .

# Run with custom settings
docker run -d \
  --name indic-seamless-test \
  -p 8000:5000 \
  -e DEBUG=true \
  indic-seamless-service:latest

# Test the service
python examples/client_example.py
```

### **Production Deployment Workflow**

#### AWS Lambda Deployment (Serverless)

```bash
# Set HuggingFace token
export HF_TOKEN="your_token_here"

# Deploy to Lambda
./aws/lambda/deploy-lambda.sh

# Test deployment
curl https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/health

# View logs
./aws/lambda/deploy-lambda.sh logs
```

#### AWS ECS Deployment

```bash
# Deploy to AWS
cd aws
./deploy.sh

# Monitor deployment
aws ecs describe-services \
  --cluster indic-seamless-cluster \
  --services indic-seamless-service

# Check logs
aws logs tail /ecs/indic-seamless-service --follow
```

#### Terraform Deployment

```bash
# Initialize and deploy
cd terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan

# Check deployment
terraform output service_url
```

#### SageMaker Deployment

```bash
# Deploy to SageMaker
cd sagemaker
python deploy.py

# Test endpoint
python test_endpoint.py
```

### **Maintenance Workflow**

#### Environment Updates

```bash
# Activate environment
source env/.venv/bin/activate

# Update dependencies with uv (fast!)
cd env
uv pip compile requirements.in --output-file requirements.txt
uv pip install -r requirements.txt

# Test after updates
python workflow_test.py
```

#### Performance Monitoring

```bash
# Run performance benchmark
source env/.venv/bin/activate
python env/benchmark.py

# Check service metrics
curl http://localhost:8000/health
```

#### Troubleshooting

```bash
# Check environment
source env/.venv/bin/activate
python -c "import torch; print(torch.__version__)"
python -c "import transformers; print(transformers.__version__)"

# Debug mode
export DEBUG=true
python start_service.py

# Check logs
tail -f logs/service.log
```

### **CI/CD Integration**

#### GitHub Actions Example

```yaml
name: Test and Deploy
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Environment
        run: |
          cd env && ./setup.sh
      - name: Run Tests
        run: |
          source env/.venv/bin/activate
          python workflow_test.py
      - name: Build Docker
        run: docker build -t indic-seamless-service .
```

#### Pre-commit Hooks

```bash
# Install pre-commit
uv pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## 📚 More Information

- **Model:** ai4bharat/indic-seamless
- **Framework:** FastAPI
- **Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## Project Structure

> 📋 **Detailed Structure**: See [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md) for comprehensive project organization.

```
indic_seamless_service/
├── 📄 README.md              # This file - main documentation
├── 📄 PROJECT_STRUCTURE.md   # Detailed project organization
├── 📄 start_service.py       # Service startup script
├── 📄 Dockerfile             # Docker configuration
├── 📄 .gitignore             # Git ignore rules
│
├── 📁 docs/                  # Documentation
│   ├── WORKFLOWS.md          # Development workflows
│   ├── DEPENDENCIES.md       # Dependency management
│   ├── TROUBLESHOOTING.md    # General troubleshooting
│   └── DOCKER_TROUBLESHOOTING.md # Docker help
│
├── 📁 env/                   # Environment management
│   ├── setup.sh              # Environment setup with uv
│   ├── activate.sh           # Quick activation
│   ├── benchmark.py          # Performance testing
│   ├── requirements.in       # Dependencies
│   └── requirements.txt      # Pinned versions
│
├── 📁 scripts/               # Deployment scripts
│   ├── deploy-local.sh       # Docker deployment
│   └── run-local.sh          # Development mode
│
├── 📁 tests/                 # Test suite
│   ├── test_service.py       # Unit tests
│   └── workflow_test.py      # Integration tests
│
├── 📁 examples/              # Usage examples
│   └── client_example.py     # Client implementation
│
├── 📁 aws/                   # AWS deployment
├── 📁 terraform/             # Infrastructure as code
└── 📁 sagemaker/             # SageMaker deployment
```

## Development & Contribution

1. Fork the repository
2. Create a feature branch
3. Implement changes
4. Add tests
5. Submit pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [AI4Bharat](https://ai4bharat.org/) for the indic-seamless model
- [Hugging Face](https://huggingface.co/) for model hosting
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [uv](https://github.com/astral-sh/uv) for blazing-fast package management

## 📋 Quick Reference

### Common Commands

```bash
# Environment setup
cd env && ./setup.sh
source env/.venv/bin/activate

# Start service
python start_service.py
python start_service.py --port 8001

# Testing
python tests/workflow_test.py
python examples/client_example.py
curl http://localhost:8000/health

# Docker
./scripts/deploy-local.sh
docker build -t indic-seamless-service .
docker run -p 8000:8000 indic-seamless-service

# Development (no Docker)
./scripts/run-local.sh

# Performance
python env/benchmark.py
make check-deps
```

### Environment Variables

```bash
export DEBUG=true          # Enable debug logging
export PORT=8001           # Custom port
export MODEL_CACHE_DIR=./models  # Model cache directory
```

### Useful URLs

- **Service**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Supported Languages**: http://localhost:8000/supported-languages

## Support

- Check the troubleshooting guide
- Review the test scripts
- Open an issue on GitHub
- Contact the development team

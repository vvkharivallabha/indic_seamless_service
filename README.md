# Indic-Seamless Speech-to-Text Service

A production-ready REST API service for speech-to-text conversion using the [ai4bharat/indic-seamless](https://huggingface.co/ai4bharat/indic-seamless) model. This service provides high-quality speech recognition for 100+ languages, with special focus on Indian languages.

---

## 🚀 Quick Start

> 💡 **Pro Tip**: Use `make help` to see all available commands!

### **🚀 Option 1: Using Makefile (Recommended)**

```bash
# Setup environment and deploy with Docker
make setup
make deploy-local

# Or for development mode
make setup
make run-local

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
   This will install Miniconda (if needed), create a conda environment named `indic-seamless`, and install all dependencies.

   **To activate the environment later:**
   ```bash
   conda activate indic-seamless
   # or use the helper script
   source env/activate.sh
   ```

2. **Start the service:**
   ```bash
   python start_service.py
   # or
   python app.py
   # or with custom port
   python start_service.py --port 8001
   ```
   The service will start on `http://localhost:8000`

3. **Test the service:**
   ```bash
   python tests/workflow_test.py
   # or
   python examples/client_example.py
   ```

---

## 📋 API Endpoints

| Endpoint                | Method | Description                |
|------------------------|--------|----------------------------|
| `/`                    | GET    | Service information        |
| `/health`              | GET    | Health check               |
| `/supported-languages` | GET    | List supported languages   |
| `/speech-to-text`      | POST   | Convert speech to text     |

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
conda activate indic-seamless
python start_service.py
```

---

## ☁️ AWS & SageMaker Deployment

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

1. **Service won't start**
   ```bash
   python start_service.py --check-only
   lsof -i :8000
   ```
2. **Model loading fails**
   - Ensure sufficient memory (4GB+ recommended)
   - Check internet connection for model download
   - Verify disk space (~2GB for model)
3. **Audio processing errors**
   - Verify audio file format is supported
   - Check file is not corrupted
   - Ensure audio has speech content

**Debug mode:**
```bash
export DEBUG=true
python app.py
```

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
conda activate indic-seamless
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
conda info --envs
conda list

# Update dependencies
cd env
pip-compile requirements.in
pip install -r requirements.txt

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
conda activate indic-seamless

# Update dependencies
cd env
pip-compile --upgrade requirements.in
pip install -r requirements.txt

# Test after updates
python workflow_test.py
```

#### Performance Monitoring
```bash
# Run performance benchmark
conda activate indic-seamless
python env/benchmark.py

# Check service metrics
curl http://localhost:8000/health
```

#### Troubleshooting
```bash
# Check environment
conda activate indic-seamless
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
          conda activate indic-seamless
          python workflow_test.py
      - name: Build Docker
        run: docker build -t indic-seamless-service .
```

#### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

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
├── 📄 app.py                 # Main FastAPI application
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
│   ├── setup.sh              # Environment setup
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

## 📋 Quick Reference

### Common Commands
```bash
# Environment setup
cd env && ./setup.sh
conda activate indic-seamless

# Start service
python start_service.py
python start_service.py --port 8001

# Testing
python workflow_test.py
python client_example.py
curl http://localhost:8000/health

# Docker
./deploy-local.sh
docker build -t indic-seamless-service .
docker run -p 8000:5000 indic-seamless-service

# Development (no Docker)
./run-local.sh

# Performance
python env/benchmark.py
conda list
conda info --envs

# Deployment
cd aws && ./deploy.sh
cd terraform && terraform apply
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
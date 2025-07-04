# Troubleshooting Guide

This guide helps you resolve common issues when setting up and running the Indic Seamless Service.

## 🔧 Quick Fixes

### Most Common Issues
```bash
# If you have dependency issues, try:
make fix-deps

# Or for a complete clean setup:
make clean setup

# Check if everything is working:
make check-deps
```

---

## ⚡ uv Package Manager

This project now uses [uv](https://github.com/astral-sh/uv) for faster package management.

### Benefits of uv:
- **10-100x faster** than pip for installations
- **Better dependency resolution** with fewer conflicts
- **Automatic fallback** to pip if uv is unavailable
- **Compatible with pip** commands and workflows

### uv Commands:
```bash
# Check if uv is installed
make check-deps

# Install dependencies with uv (fast!)
uv pip install -r env/requirements.txt

# Compile dependencies
make compile-deps

# Install with extras
uv pip install ".[dev]"
uv pip install ".[aws,prod]"

# Clean cache
uv cache clean
```

### Common uv Issues:

#### Problem: `uv` command not found
**Solution:**
```bash
# Install uv automatically via setup
make setup

# Or install manually
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
```

#### Problem: uv installation fails
**Solution:**
```bash
# The system automatically falls back to pip
# All commands work the same way, just slower
pip install -r env/requirements.txt
```

---

## 📦 Dependency Issues

### Problem: `ModuleNotFoundError: No module named 'uvicorn'`
**Solution:**
```bash
# With uv (fast)
uv pip install 'uvicorn[standard]==0.35.0'

# Or with pip (fallback)
pip install 'uvicorn[standard]==0.35.0'
```

### Problem: `ModuleNotFoundError: No module named 'torch'`
**Solution:**
```bash
# With uv (fast)
uv pip install torch==2.7.1 torchaudio==2.7.1

# Or with pip (fallback)
pip install torch==2.7.1 torchaudio==2.7.1
```

### Problem: `Form data requires "python-multipart" to be installed`
**Solution:**
```bash
# With uv (fast)
uv pip install python-multipart==0.0.20

# Or with pip (fallback)
pip install python-multipart==0.0.20
```

### Problem: `antlr4-python3-runtime` version conflicts
**Symptoms:**
- `pip install -r requirements.txt` fails
- `TypeError: canonicalize_version() got an unexpected keyword argument 'strip_trailing_zero'`

**Solution:**
```bash
# Use the fixed requirements.txt or install essential packages manually
make fix-deps

# Or regenerate requirements with uv
make compile-deps
```

---

## 🔐 Authentication Issues

### Problem: Gated Repository Error
**Symptoms:**
```
You are trying to access a gated repo.
Access to model ai4bharat/indic-seamless is restricted.
```

**Solution:**
1. Visit: https://huggingface.co/ai4bharat/indic-seamless
2. Click "Request Access" and wait for approval
3. Get your access token from: https://huggingface.co/settings/tokens
4. Login with the token:
   ```bash
   huggingface-cli login
   # Enter your token when prompted
   ```

### Check Authentication Status
```bash
# Check if you're authenticated
make check-auth

# Or manually:
python -c "from huggingface_hub import HfApi; print(HfApi().whoami())"
```

---

## 🚀 Service Issues

### Problem: Service won't start
**Diagnosis:**
```bash
# Check if port is in use
lsof -i :8000

# Check dependencies
make check-deps

# Check conda environment
conda info --envs
```

**Solutions:**
```bash
# Try different port
python start_service.py --port 8001

# Or kill existing process
kill -9 $(lsof -t -i:8000)

# Or restart from clean state
make clean setup
```

### Problem: Model loading fails
**Symptoms:**
- Service starts but model endpoints don't work
- "Failed to load model" errors in logs

**Solutions:**
1. **Check authentication** (most common):
   ```bash
   make setup-auth
   ```

2. **Check memory** (need 4GB+ RAM):
   ```bash
   # Check available memory
   free -h  # Linux
   # or
   vm_stat | grep free  # macOS
   ```

3. **Check disk space** (need 2GB+ for model):
   ```bash
   df -h
   ```

---

## 🐳 Docker Issues

### Problem: Docker build fails
**Solutions:**
```bash
# Clean up Docker
docker system prune -f

# Build with more memory
docker build --memory=4g -t indic-seamless-service .

# Or use local development instead
make run-local
```

### Problem: Container crashes
**Diagnosis:**
```bash
# Check logs
docker logs indic-seamless-local

# Check container status
docker ps -a
```

---

## 🌐 Network Issues

### Problem: Can't download models
**Symptoms:**
- Timeouts when loading models
- Connection errors during setup

**Solutions:**
```bash
# Check internet connection
ping huggingface.co

# Use proxy if needed
export https_proxy=your-proxy-url
export http_proxy=your-proxy-url

# Or download models manually
python -c "from transformers import AutoModel; AutoModel.from_pretrained('ai4bharat/indic-seamless')"
```

---

## 💻 Environment Issues

### Problem: Conda environment not found
**Solutions:**
```bash
# Check if conda is installed
which conda

# Install conda if missing
cd env && ./setup.sh

# Create environment manually
conda create -n indic-seamless python=3.10
conda activate indic-seamless
```

### Problem: Wrong Python version
**Solutions:**
```bash
# Check Python version
python --version

# Should be 3.10.x, if not:
conda install python=3.10
```

---

## 🧪 Testing Issues

### Problem: Tests fail
**Diagnosis:**
```bash
# Run tests with verbose output
python -m pytest tests/ -v

# Or run specific test
python tests/workflow_test.py
```

**Common Solutions:**
```bash
# Make sure service is running
make run-structured

# Or test against different URL
python tests/workflow_test.py --url http://localhost:8001
```

---

## 🔍 Debugging Steps

### 1. Environment Check
```bash
# Check all dependencies
make check-deps

# Check authentication
make check-auth

# Check service status
make status
```

### 2. Clean Installation
```bash
# Nuclear option - start fresh
make clean
conda remove -n indic-seamless --all
make setup
```

### 3. Manual Installation
```bash
# Install only essentials with uv (fast)
make install-essentials

# Then add others as needed
uv pip install librosa soundfile
```

### 4. Debug Mode
```bash
# Run with debug logging
export DEBUG=true
python start_service.py
```

---

## 📋 Environment Variables

Useful environment variables for debugging:

```bash
# Enable debug logging
export DEBUG=true

# Use different port
export PORT=8001

# Custom model cache directory
export MODEL_CACHE_DIR=./models

# Proxy settings
export https_proxy=your-proxy-url
export http_proxy=your-proxy-url
```

---

## 🆘 Getting Help

### 1. Check Logs
```bash
# Service logs
tail -f logs/service.log

# Docker logs
docker logs indic-seamless-local

# System logs
journalctl -u your-service
```

### 2. System Information
```bash
# Gather system info for bug reports
echo "OS: $(uname -a)"
echo "Python: $(python --version)"
echo "Conda: $(conda --version)"
echo "uv: $(uv --version)"
echo "Docker: $(docker --version)"
echo "Memory: $(free -h)"
echo "Disk: $(df -h)"
```

### 3. Common Commands
```bash
# All-in-one health check
make check-deps && make check-auth && make status

# Quick fix for most issues
make quick-fix

# Complete reset
make clean setup
```

---

## 📚 Additional Resources

- [Dependencies Guide](DEPENDENCIES.md)
- [Docker Troubleshooting](DOCKER_TROUBLESHOOTING.md)
- [Workflows Guide](WORKFLOWS.md)
- [Project Structure](../PROJECT_STRUCTURE.md)
- [uv Documentation](https://github.com/astral-sh/uv)

---

## 🐛 Reporting Issues

When reporting issues, please include:

1. **Error message** (full traceback)
2. **System information** (OS, Python version, etc.)
3. **Package manager used** (uv or pip)
4. **Steps to reproduce** the issue
5. **Output of diagnostic commands**:
   ```bash
   make check-deps
   make check-auth
   make status
   ```

This helps us help you faster! 🚀 
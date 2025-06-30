# 🔄 Indic-Seamless Service Workflows

Quick reference guide for common development, testing, and deployment workflows.

---

## 🏗️ **SETUP** (One-time)

```bash
# Initial setup
git clone <repository-url>
cd indic_seamless_service
cd env && ./setup.sh

# Verify setup
conda activate indic-seamless
python -c "import torch, transformers; print('✅ Setup successful')"
```

---

## 💻 **DEVELOPMENT** (Daily)

```bash
# Start development session
conda activate indic-seamless
# or: source env/activate.sh

# Start service
python start_service.py

# Test in another terminal
python workflow_test.py
```

**Environment Management:**
```bash
conda info --envs              # List environments
conda list                     # List packages
cd env && pip-compile requirements.in  # Update deps
python env/benchmark.py        # Performance check
```

---

## 🧪 **TESTING**

### Local Testing
```bash
# Quick tests
python workflow_test.py
python client_example.py
curl http://localhost:8000/health

# Comprehensive testing
python test_service.py
```

### Docker Testing
```bash
# Automated Docker deployment
./deploy-local.sh

# Manual Docker test
docker build -t indic-seamless-service .
docker run -p 8000:5000 indic-seamless-service
curl http://localhost:5000/health
```

### Development Testing (No Docker)
```bash
# For development environments where Docker isn't available
./run-local.sh

# Quick development test
conda activate indic-seamless
python start_service.py
curl http://localhost:8000/health
```

---

## 🚀 **DEPLOYMENT**

### AWS ECS
```bash
cd aws
./deploy.sh

# Monitor
aws ecs describe-services --cluster indic-seamless-cluster --services indic-seamless-service
aws logs tail /ecs/indic-seamless-service --follow
```

### Terraform
```bash
cd terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan
terraform output service_url
```

### SageMaker
```bash
cd sagemaker
python deploy.py
python test_endpoint.py
```

---

## 🔧 **MAINTENANCE**

### Update Dependencies
```bash
conda activate indic-seamless
cd env
pip-compile --upgrade requirements.in
pip install -r requirements.txt
python ../workflow_test.py  # Test after update
```

### Performance Monitoring
```bash
python env/benchmark.py
curl http://localhost:8000/health
```

### Troubleshooting
```bash
# Check environment
conda activate indic-seamless
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"

# Debug mode
export DEBUG=true
python start_service.py

# Check logs
tail -f logs/service.log
docker logs indic-seamless-local
```

---

## 🚨 **EMERGENCY FIXES**

### Service Won't Start
```bash
# Check port conflicts
lsof -i :8000
python start_service.py --check-only

# Reset environment
conda deactivate
conda activate indic-seamless
python start_service.py
```

### Docker Issues
```bash
# If Docker daemon is not running
sudo systemctl start docker  # or sudo service docker start

# Clean Docker
docker stop indic-seamless-local
docker rm indic-seamless-local
docker system prune -f

# Rebuild with Docker
./deploy-local.sh
```

### Development Issues (No Docker)
```bash
# For development environments
./run-local.sh

# Or manual setup
conda activate indic-seamless
python start_service.py
```

### Model Loading Errors
```bash
# Clear model cache
rm -rf ~/.cache/huggingface/
python -c "from transformers import AutoModel; AutoModel.from_pretrained('ai4bharat/indic-seamless')"
```

---

## 📋 **QUICK COMMANDS**

| Task | Command |
|------|---------|
| **Setup** | `cd env && ./setup.sh` |
| **Activate** | `conda activate indic-seamless` |
| **Start** | `python start_service.py` |
| **Test** | `python workflow_test.py` |
| **Docker** | `./deploy-local.sh` |
| **Dev (No Docker)** | `./run-local.sh` |
| **Deploy AWS** | `cd aws && ./deploy.sh` |
| **Deploy Terraform** | `cd terraform && terraform apply` |
| **Benchmark** | `python env/benchmark.py` |
| **Debug** | `DEBUG=true python start_service.py` |
| **Health** | `curl http://localhost:8000/health` |

---

## 🌐 **USEFUL URLS**

- **Service**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs  
- **Health**: http://localhost:8000/health
- **Languages**: http://localhost:8000/supported-languages

---

## 📞 **SUPPORT CHECKLIST**

Before asking for help:
- [ ] Checked `TROUBLESHOOTING.md`
- [ ] Ran `python env/benchmark.py`
- [ ] Tested with `python workflow_test.py`
- [ ] Checked logs with `DEBUG=true`
- [ ] Verified environment with `conda list`

---

*Last updated: $(date)* 
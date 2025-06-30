# 🐳 Docker Troubleshooting Guide

This guide helps you resolve common Docker issues and provides alternatives when Docker isn't available.

---

## 🚨 **Common Docker Issues**

### 1. **Docker Daemon Not Running**

**Error:** `Cannot connect to the Docker daemon at unix:///var/run/docker.sock`

**Solutions:**

#### For systemd-based systems:
```bash
# Start Docker service
sudo systemctl start docker

# Enable Docker to start on boot
sudo systemctl enable docker

# Check Docker status
sudo systemctl status docker
```

#### For non-systemd systems:
```bash
# Start Docker service
sudo service docker start

# Check if Docker is running
sudo service docker status
```

#### Manual Docker daemon start:
```bash
# Start Docker daemon manually
sudo dockerd &

# Wait a few seconds, then test
sleep 5
docker ps
```

### 2. **Permission Denied**

**Error:** `permission denied while trying to connect to the Docker daemon socket`

**Solutions:**

#### Add user to docker group:
```bash
# Add current user to docker group
sudo usermod -aG docker $USER

# Log out and log back in, or run:
newgrp docker

# Test Docker without sudo
docker ps
```

#### Temporary fix with sudo:
```bash
# Use sudo for Docker commands
sudo docker ps
sudo docker build -t myapp .
sudo docker run myapp
```

### 3. **Docker Not Installed**

**Error:** `docker: command not found`

**Solutions:**

#### Install Docker on Ubuntu/Debian:
```bash
# Update packages
sudo apt update

# Install Docker
sudo apt install docker.io

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker
```

#### Install Docker on CentOS/RHEL:
```bash
# Install Docker
sudo yum install docker

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### 4. **Docker in Remote/Container Environment**

**Issue:** Running in a remote development environment or container where Docker isn't available.

**Solution:** Use the development deployment method:
```bash
# For development environments where Docker isn't available
./run-local.sh

# Or manually
conda activate indic-seamless
python start_service.py
```

---

## 🔧 **Environment-Specific Solutions**

### **AWS Cloud9 / Remote Development**
```bash
# Install Docker if not available
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker $USER

# If Docker still doesn't work, use development deployment
./run-local.sh
```

### **GitHub Codespaces**
```bash
# Docker is usually pre-installed, but if not working:
sudo systemctl start docker

# Alternative: Use development deployment
./run-local.sh
```

### **WSL (Windows Subsystem for Linux)**
```bash
# Install Docker Desktop on Windows first
# Then in WSL:
sudo service docker start

# Or use direct deployment
./run-local.sh
```

### **Containerized Environments**
If you're already inside a container, Docker-in-Docker might not be available:
```bash
# Use development deployment instead
./run-local.sh

# Or deploy to external Docker host
export DOCKER_HOST=tcp://remote-docker-host:2376
docker build -t myapp .
```

---

## 🛠️ **Automated Solutions**

### **Docker Deployment Script**
The `deploy-local.sh` script handles Docker deployment:

```bash
# Docker-only deployment script
./deploy-local.sh
```

### **Development Deployment Script**
For development environments where Docker isn't available:

```bash
# This script runs the service directly with Python for development
./run-local.sh
```

---

## 🔍 **Diagnostic Commands**

### **Check Docker Status**
```bash
# Check if Docker command exists
command -v docker

# Check Docker version
docker --version

# Check if daemon is running
docker info

# List running containers
docker ps

# Check Docker system info
docker system info
```

### **Check System Resources**
```bash
# Check available disk space
df -h

# Check memory usage
free -h

# Check if port is available
lsof -i :5000
```

### **Check Logs**
```bash
# Docker daemon logs (systemd)
sudo journalctl -u docker.service

# Docker daemon logs (manual start)
sudo tail -f /var/log/docker.log

# Container logs
docker logs <container-name>
```

---

## 🚀 **Alternative Deployment Methods**

### **1. Direct Python Deployment**
```bash
# Activate environment and run directly
conda activate indic-seamless
python start_service.py --port 5000
```

### **2. Cloud Deployment**
```bash
# Deploy to AWS ECS
cd aws && ./deploy.sh

# Deploy with Terraform
cd terraform && terraform apply

# Deploy to SageMaker
cd sagemaker && python deploy.py
```

### **3. Remote Docker Host**
```bash
# Use remote Docker daemon
export DOCKER_HOST=tcp://remote-host:2376
docker build -t indic-seamless-service .
docker run -p 5000:5000 indic-seamless-service
```

---

## 📋 **Quick Fixes Checklist**

When Docker isn't working, try these in order:

- [ ] **Check if Docker is installed**: `docker --version`
- [ ] **Start Docker daemon**: `sudo systemctl start docker`
- [ ] **Add user to docker group**: `sudo usermod -aG docker $USER`
- [ ] **Try with sudo**: `sudo docker ps`
- [ ] **Check disk space**: `df -h`
- [ ] **Restart Docker**: `sudo systemctl restart docker`
- [ ] **Use development deployment**: `./run-local.sh`
- [ ] **Check logs**: `sudo journalctl -u docker.service`

---

## 🆘 **Emergency Fallback**

If nothing works, you can always run the service directly:

```bash
# Quick fallback deployment
conda activate indic-seamless
python start_service.py

# Or with custom port
python start_service.py --port 8001

# Check if it's working
curl http://localhost:8000/health
```

---

## 📞 **Getting Help**

If you're still having issues:

1. **Check the main troubleshooting guide**: `TROUBLESHOOTING.md`
2. **Run diagnostics**: `python env/benchmark.py`
3. **Check environment**: `conda list`
4. **Use debug mode**: `DEBUG=true ./run-local.sh`
5. **Check logs**: `tail -f logs/service.log`

---

*Remember: The service works perfectly without Docker using `./run-local.sh`!* 
#!/usr/bin/env python3
"""
Startup script for Indic-Seamless Speech-to-Text Service
Handles environment setup and service startup.
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'torch', 'transformers', 'fastapi', 'uvicorn', 
        'librosa', 'soundfile', 'numpy', 'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} (missing)")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("   Install with: pip install -r env/requirements.txt")
        return False
    
    return True

def setup_environment():
    """Setup environment variables."""
    # Set default environment variables
    os.environ.setdefault('PORT', '8000')
    os.environ.setdefault('HOST', '0.0.0.0')
    os.environ.setdefault('MODEL_NAME', 'ai4bharat/indic-seamless')
    
    print("✅ Environment variables set")
    print(f"   PORT: {os.environ.get('PORT')}")
    print(f"   HOST: {os.environ.get('HOST')}")
    print(f"   MODEL_NAME: {os.environ.get('MODEL_NAME')}")

def check_port_availability(port: int) -> bool:
    """Check if the port is available."""
    import socket
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def wait_for_service(url: str, max_wait: int = 60) -> bool:
    """Wait for the service to be ready."""
    print(f"⏳ Waiting for service to be ready at {url}...")
    
    for i in range(max_wait):
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('model_loaded', False):
                    print("✅ Service is ready!")
                    return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(1)
        if (i + 1) % 10 == 0:
            print(f"   Still waiting... ({i + 1}s)")
    
    print("❌ Service did not become ready in time")
    return False

def start_service():
    """Start the service."""
    print("🚀 Starting Indic-Seamless Speech-to-Text Service...")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        return False
    
    # Setup environment
    print("\n🔧 Setting up environment...")
    setup_environment()
    
    # Check port availability
    port = int(os.environ.get('PORT', 8000))
    if not check_port_availability(port):
        print(f"❌ Port {port} is already in use")
        print("   Try a different port: PORT=8001 python start_service.py")
        return False
    
    print(f"✅ Port {port} is available")
    
    # Start the service
    print(f"\n🎯 Starting service on port {port}...")
    print("   Press Ctrl+C to stop the service")
    print("   Service will be available at:")
    print(f"   - Local: http://localhost:{port}")
    print(f"   - Network: http://0.0.0.0:{port}")
    print(f"   - API Docs: http://localhost:{port}/docs")
    print()
    
    try:
        # Import and run the app
        from app import app
        import uvicorn
        
        uvicorn.run(
            app,
            host=os.environ.get('HOST', '0.0.0.0'),
            port=port,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Service stopped by user")
        return True
    except Exception as e:
        print(f"\n❌ Error starting service: {e}")
        return False

def main():
    """Main function."""
    print("=" * 60)
    print("🎤 Indic-Seamless Speech-to-Text Service")
    print("=" * 60)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Start Indic-Seamless Speech-to-Text Service")
    parser.add_argument("--port", type=int, help="Port to run the service on")
    parser.add_argument("--host", help="Host to bind to")
    parser.add_argument("--check-only", action="store_true", help="Only check dependencies and exit")
    
    args = parser.parse_args()
    
    # Set environment variables from command line
    if args.port:
        os.environ['PORT'] = str(args.port)
    if args.host:
        os.environ['HOST'] = args.host
    
    if args.check_only:
        print("🔍 Running dependency check only...")
        check_python_version()
        print("\n📦 Checking dependencies...")
        check_dependencies()
        print("\n✅ Check completed")
        return
    
    # Start the service
    success = start_service()
    
    if not success:
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure all dependencies are installed: pip install -r env/requirements.txt")
        print("   2. Check if the port is available")
        print("   3. Ensure you have sufficient memory (4GB+ recommended)")
        print("   4. Check the logs for detailed error messages")
        sys.exit(1)

if __name__ == "__main__":
    main() 
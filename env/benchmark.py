#!/usr/bin/env python3
"""
Performance benchmark for the Indic Seamless service setup.
This script measures installation and import times for critical dependencies.
"""

import time
import subprocess
import sys
import os
import platform
from pathlib import Path
from typing import Dict, Any, List

def run_command(cmd: str, timeout: int = 300) -> Dict[str, Any]:
    """Run a command and measure its execution time."""
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=timeout
        )
        end_time = time.time()
        return {
            'success': result.returncode == 0,
            'duration': end_time - start_time,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'command': cmd
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'duration': timeout,
            'stdout': '',
            'stderr': f'Command timed out after {timeout} seconds',
            'command': cmd
        }

def check_uv_installation() -> bool:
    """Check if uv is installed and working."""
    print("🔍 Checking uv installation...")
    
    # Check if uv is available
    uv_check = run_command("uv --version", timeout=10)
    if uv_check['success']:
        print(f"✅ uv is available: {uv_check['stdout'].strip()}")
        return True
    else:
        print("❌ uv is not available")
        return False

def check_python_environment() -> None:
    """Check Python environment details."""
    print("\n🐍 Python Environment Information:")
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Platform: {platform.system()} {platform.release()}")
    
    # Check if we're in a virtual environment
    venv_path = os.environ.get('VIRTUAL_ENV')
    if venv_path:
        print(f"Virtual Environment: {venv_path}")
        print("✅ Running in virtual environment")
    else:
        print("⚠️  Not running in virtual environment")
    
    # Check if we're in the expected uv environment
    expected_venv = Path(__file__).parent / ".venv"
    if expected_venv.exists():
        print(f"✅ uv virtual environment exists at: {expected_venv}")
    else:
        print("⚠️  uv virtual environment not found")

def benchmark_package_installation() -> None:
    """Benchmark package installation speeds."""
    print("\n⚡ Benchmarking Package Installation:")
    
    # Test packages (lightweight ones for quick testing)
    test_packages = [
        "requests==2.32.4",
        "numpy==1.26.4",
        "fastapi==0.115.14"
    ]
    
    uv_available = check_uv_installation()
    
    if uv_available:
        print("\n📦 Testing uv installation speed:")
        for package in test_packages:
            print(f"  Installing {package} with uv...")
            result = run_command(f"uv pip install {package}", timeout=60)
            if result['success']:
                print(f"  ✅ {package}: {result['duration']:.2f}s")
            else:
                print(f"  ❌ {package}: Failed ({result['stderr'][:100]}...)")
    
    print("\n📦 Testing pip installation speed (for comparison):")
    for package in test_packages:
        print(f"  Installing {package} with pip...")
        result = run_command(f"pip install {package}", timeout=60)
        if result['success']:
            print(f"  ✅ {package}: {result['duration']:.2f}s")
        else:
            print(f"  ❌ {package}: Failed ({result['stderr'][:100]}...)")

def benchmark_imports() -> None:
    """Benchmark import times for critical packages."""
    print("\n📥 Benchmarking Import Performance:")
    
    critical_packages = [
        "torch",
        "transformers",
        "fastapi",
        "uvicorn",
        "librosa",
        "numpy"
    ]
    
    for package in critical_packages:
        start_time = time.time()
        try:
            __import__(package)
            end_time = time.time()
            print(f"  ✅ {package}: {(end_time - start_time) * 1000:.2f}ms")
        except ImportError as e:
            print(f"  ❌ {package}: Not available ({str(e)})")
        except Exception as e:
            print(f"  ⚠️  {package}: Import error ({str(e)})")

def check_service_dependencies() -> None:
    """Check if all service dependencies are available."""
    print("\n🔍 Checking Service Dependencies:")
    
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
        
        # Check for CUDA availability
        if torch.cuda.is_available():
            print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
        else:
            print("⚠️  CUDA not available (CPU-only)")
            
    except ImportError:
        print("❌ PyTorch not available")
    
    try:
        import transformers
        print(f"✅ Transformers: {transformers.__version__}")
    except ImportError:
        print("❌ Transformers not available")
    
    try:
        import fastapi  # type: ignore
        print(f"✅ FastAPI: {fastapi.__version__}")
    except ImportError:
        print("❌ FastAPI not available")
    
    try:
        import uvicorn  # type: ignore
        print(f"✅ Uvicorn: {uvicorn.__version__}")
    except ImportError:
        print("❌ Uvicorn not available")

def performance_recommendations() -> None:
    """Provide performance recommendations."""
    print("\n💡 Performance Recommendations:")
    
    uv_available = check_uv_installation()
    
    if uv_available:
        print("✅ uv is available - excellent for fast package management!")
        print("  - Use 'uv pip install' instead of 'pip install'")
        print("  - Use 'uv pip compile' for dependency management")
        print("  - Consider 'uv cache clean' to free up disk space")
    else:
        print("⚠️  uv is not available - consider installing for better performance")
        print("  - Install: curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("  - 10-100x faster than pip")
    
    # Check virtual environment
    venv_path = os.environ.get('VIRTUAL_ENV')
    if venv_path:
        print("✅ Virtual environment is active")
    else:
        print("⚠️  Consider activating virtual environment for isolation")
        print("  - Activate: source env/.venv/bin/activate")
    
    # System-specific recommendations
    system = platform.system()
    if system == "Darwin":  # macOS
        print("📱 macOS detected:")
        print("  - Consider using Apple Silicon optimized packages")
        print("  - Use 'uv pip install' for better ARM64 support")
    elif system == "Linux":
        print("🐧 Linux detected:")
        print("  - Consider using system package manager for base dependencies")
        print("  - Use 'uv pip install' for Python packages")

def main() -> None:
    """Main benchmark function."""
    print("🚀 Indic Seamless Service - Performance Benchmark")
    print("=" * 50)
    
    # Check environment
    check_python_environment()
    
    # Check service dependencies
    check_service_dependencies()
    
    # Benchmark imports
    benchmark_imports()
    
    # Benchmark installations (optional - can be slow)
    benchmark_choice = input("\n❓ Run package installation benchmark? (y/N): ").lower()
    if benchmark_choice == 'y':
        benchmark_package_installation()
    
    # Provide recommendations
    performance_recommendations()
    
    print("\n🎉 Benchmark complete!")
    print("💡 For the fastest setup, use: make setup (uses uv)")

if __name__ == "__main__":
    main() 
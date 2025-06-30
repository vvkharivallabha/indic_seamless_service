#!/usr/bin/env python3
"""
Benchmark script to compare environment performance
"""

import time
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, timeout=300):
    """Run command and return execution time"""
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
        return end_time - start_time, result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return timeout, False, "", "Timeout"

def benchmark_import_times():
    """Benchmark import times for key ML libraries"""
    libraries = [
        "torch",
        "transformers", 
        "torchaudio",
        "numpy",
        "scipy",
        "librosa",
        "fastapi"
    ]
    
    results = {}
    
    for lib in libraries:
        print(f"Benchmarking {lib} import...")
        cmd = f"python -c 'import time; start=time.time(); import {lib}; print(f\"{{time.time()-start:.4f}}\")'"
        duration, success, stdout, stderr = run_command(cmd, timeout=60)
        
        if success and stdout.strip():
            try:
                import_time = float(stdout.strip())
                results[lib] = import_time
                print(f"  ✅ {lib}: {import_time:.4f}s")
            except ValueError:
                results[lib] = "error"
                print(f"  ❌ {lib}: Parse error")
        else:
            results[lib] = "failed"
            print(f"  ❌ {lib}: Import failed - {stderr}")
    
    return results

def benchmark_model_loading():
    """Benchmark model loading time"""
    print("Benchmarking model loading...")
    
    test_script = '''
import time
start_time = time.time()

try:
    from transformers import AutoProcessor, AutoModel
    
    # Load processor and model
    processor = AutoProcessor.from_pretrained("ai4bharat/indic-seamless")
    model = AutoModel.from_pretrained("ai4bharat/indic-seamless")
    
    load_time = time.time() - start_time
    print(f"{load_time:.4f}")
except Exception as e:
    print(f"ERROR: {e}")
'''
    
    with open("/tmp/model_benchmark.py", "w") as f:
        f.write(test_script)
    
    duration, success, stdout, stderr = run_command("python /tmp/model_benchmark.py", timeout=300)
    
    os.remove("/tmp/model_benchmark.py")
    
    if success and stdout.strip() and not stdout.startswith("ERROR"):
        try:
            load_time = float(stdout.strip())
            print(f"  ✅ Model loading: {load_time:.4f}s")
            return load_time
        except ValueError:
            print(f"  ❌ Model loading: Parse error - {stdout}")
            return None
    else:
        print(f"  ❌ Model loading failed: {stderr}")
        return None

def main():
    print("🚀 Environment Performance Benchmark")
    print("=" * 50)
    
    # Check current environment
    conda_env = os.environ.get('CONDA_DEFAULT_ENV', 'None')
    virtual_env = os.environ.get('VIRTUAL_ENV', 'None')
    
    print(f"Current Conda Environment: {conda_env}")
    print(f"Current Virtual Environment: {virtual_env}")
    print(f"Python Path: {sys.executable}")
    print("-" * 50)
    
    # Benchmark imports
    print("\n📦 Import Performance:")
    import_results = benchmark_import_times()
    
    # Benchmark model loading
    print("\n🤖 Model Loading Performance:")
    model_time = benchmark_model_loading()
    
    # Summary
    print("\n📊 Summary:")
    print("-" * 30)
    
    total_import_time = sum(t for t in import_results.values() if isinstance(t, float))
    print(f"Total import time: {total_import_time:.4f}s")
    
    if model_time:
        print(f"Model loading time: {model_time:.4f}s")
        print(f"Total startup time: {total_import_time + model_time:.4f}s")
    
    print("\n💡 Recommendations:")
    if total_import_time > 10:
        print("- Consider using conda for better ML library optimization")
    if model_time and model_time > 30:
        print("- Consider model caching or using a model server")
    
    print("- Use Docker for consistent deployment environments")
    print("- Consider using conda-pack for environment distribution")

if __name__ == "__main__":
    main() 
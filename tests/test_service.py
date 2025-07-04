#!/usr/bin/env python3
"""
Test script for the Indic-Seamless Service (FastAPI)
This script tests all endpoints of the service to ensure they work correctly.
"""

import os
import tempfile
import time

import numpy as np
import requests
import soundfile as sf

# Configuration
BASE_URL = "http://localhost:8000"  # Updated to match structured app default port
TEST_AUDIO_DURATION = 3  # seconds
SAMPLE_RATE = 16000


def create_test_audio(duration=TEST_AUDIO_DURATION, sample_rate=SAMPLE_RATE):
    """Create a test audio file with a simple tone."""
    # Generate a simple sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio = 0.3 * np.sin(2 * np.pi * 440 * t)  # 440 Hz tone

    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        sf.write(temp_file.name, audio, sample_rate)
        return temp_file.name


def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check...")

    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()

        data = response.json()
        print("✓ Health check passed")
        print(f"  Status: {data['status']}")
        print(f"  Model loaded: {data['model_loaded']}")
        print(f"  Device: {data['device']}")
        print(f"  Supported languages: {len(data['supported_languages'])}")

        return True

    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False


def test_supported_languages():
    """Test the supported languages endpoint."""
    print("\nTesting supported languages...")

    try:
        response = requests.get(f"{BASE_URL}/supported-languages")
        response.raise_for_status()

        data = response.json()
        print("✓ Supported languages endpoint passed")
        print(f"  Total languages: {data['count']}")
        print(f"  Languages: {list(data['languages'].keys())}")

        return True

    except Exception as e:
        print(f"✗ Supported languages test failed: {e}")
        return False


def test_root_endpoint():
    """Test the root endpoint."""
    print("\nTesting root endpoint...")

    try:
        response = requests.get(f"{BASE_URL}/")
        response.raise_for_status()

        data = response.json()
        print("✓ Root endpoint passed")
        print(f"  Service: {data['service']}")
        print(f"  Version: {data['version']}")
        print(f"  Endpoints: {list(data['endpoints'].keys())}")

        return True

    except Exception as e:
        print(f"✗ Root endpoint test failed: {e}")
        return False


def test_speech_to_text():
    """Test the speech-to-text endpoint."""
    print("\nTesting speech-to-text...")

    # Create test audio file
    audio_file = create_test_audio()

    try:
        print("  Creating test audio file...")

        with open(audio_file, "rb") as f:
            files = {"audio": f}
            data = {"target_lang": "English"}  # Updated to match current API parameter

            response = requests.post(
                f"{BASE_URL}/speech-to-text", files=files, data=data
            )
            response.raise_for_status()

            result = response.json()
            print(f"    ✓ Transcription: {result['transcription']}")

    except Exception as e:
        print(f"    ✗ Speech-to-text test failed: {e}")
        return False
    finally:
        # Clean up
        if os.path.exists(audio_file):
            os.unlink(audio_file)

    return True


def test_error_handling():
    """Test error handling for invalid requests."""
    print("\nTesting error handling...")

    # Test invalid audio file
    try:
        response = requests.post(
            f"{BASE_URL}/speech-to-text",
            files={"audio": ("test.txt", b"invalid audio content")},
            data={"target_lang": "English"},
        )

        if response.status_code == 400:
            print("  ✓ Invalid audio file error handled correctly")
        else:
            print(f"  ✗ Expected 400 error, got {response.status_code}")
            return False

    except Exception as e:
        print(f"  ✗ Error handling test failed: {e}")
        return False

    return True


def test_documentation():
    """Test that documentation endpoints are accessible."""
    print("\nTesting documentation endpoints...")

    try:
        # Test OpenAPI docs
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("  ✓ OpenAPI documentation accessible")
        else:
            print(f"  ✗ OpenAPI docs returned {response.status_code}")
            return False

        # Test ReDoc
        response = requests.get(f"{BASE_URL}/redoc")
        if response.status_code == 200:
            print("  ✓ ReDoc documentation accessible")
        else:
            print(f"  ✗ ReDoc returned {response.status_code}")
            return False

        # Test root endpoint
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("  ✓ Root endpoint accessible")
        else:
            print(f"  ✗ Root endpoint returned {response.status_code}")
            return False

        return True

    except Exception as e:
        print(f"  ✗ Documentation test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Indic-Seamless Service Test Suite (FastAPI)")
    print("=" * 60)

    # Wait for service to be ready
    print("Waiting for service to be ready...")
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print("Service is ready!")
                break
        except Exception:
            if attempt < max_attempts - 1:
                print(
                    f"Service not ready yet (attempt {attempt + 1}/{max_attempts})..."
                )
                time.sleep(10)
            else:
                print("Service failed to start within expected time.")
                return False

    # Run tests
    tests = [
        ("Health Check", test_health_check),
        ("Supported Languages", test_supported_languages),
        ("Root Endpoint", test_root_endpoint),
        ("Speech-to-Text", test_speech_to_text),
        ("Error Handling", test_error_handling),
        ("Documentation", test_documentation),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Service is working correctly.")
        print(f"📚 API Documentation: {BASE_URL}/docs")
        return True
    else:
        print("❌ Some tests failed. Please check the service configuration.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

#!/usr/bin/env python3
"""
Workflow Test for Indic-Seamless Speech-to-Text Service
This script provides a step-by-step workflow to test the service.
"""

import requests
import json
import os
import time
import sys
from typing import Dict, Any, Optional

class STTServiceWorkflow:
    """Workflow class for testing the Speech-to-Text service."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.test_results = {}
    
    def step_1_check_service_health(self) -> bool:
        """Step 1: Check if the service is running and healthy."""
        print("🔍 Step 1: Checking service health...")
        
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            print(f"   ✅ Service is running")
            print(f"   📊 Status: {data['status']}")
            print(f"   🤖 Model loaded: {data['model_loaded']}")
            print(f"   💻 Device: {data['device']}")
            
            self.test_results['health'] = {
                'status': 'passed',
                'model_loaded': data['model_loaded'],
                'device': data['device']
            }
            
            if not data['model_loaded']:
                print("   ⚠️  Warning: Model is not loaded")
                return False
            
            return True
            
        except requests.exceptions.ConnectionError:
            print("   ❌ Error: Could not connect to service")
            print("   💡 Make sure the service is running: python app.py")
            self.test_results['health'] = {'status': 'failed', 'error': 'connection_error'}
            return False
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.test_results['health'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def step_2_get_supported_languages(self) -> bool:
        """Step 2: Get list of supported languages."""
        print("\n🌍 Step 2: Getting supported languages...")
        
        try:
            response = self.session.get(f"{self.base_url}/supported-languages")
            response.raise_for_status()
            data = response.json()
            
            print(f"   ✅ Retrieved {data['count']} supported languages")
            
            # Show key Indian languages
            indian_languages = ['eng', 'hin', 'tel', 'ben', 'tam', 'mar', 'guj', 'kan', 'mal', 'urd']
            print("   🇮🇳 Key Indian languages:")
            for lang in indian_languages:
                if lang in data['languages']:
                    print(f"      {lang}: {data['languages'][lang]}")
            
            self.test_results['languages'] = {
                'status': 'passed',
                'count': data['count'],
                'languages': data['languages']
            }
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.test_results['languages'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def step_3_test_root_endpoint(self) -> bool:
        """Step 3: Test the root endpoint."""
        print("\n🏠 Step 3: Testing root endpoint...")
        
        try:
            response = self.session.get(f"{self.base_url}/")
            response.raise_for_status()
            data = response.json()
            
            print(f"   ✅ Root endpoint working")
            print(f"   📝 Service: {data['service']}")
            print(f"   🔢 Version: {data['version']}")
            print(f"   🔗 Available endpoints: {list(data['endpoints'].keys())}")
            
            self.test_results['root'] = {
                'status': 'passed',
                'service': data['service'],
                'version': data['version']
            }
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.test_results['root'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def step_4_test_speech_to_text(self, audio_file: Optional[str] = None) -> bool:
        """Step 4: Test speech-to-text functionality."""
        print("\n🎤 Step 4: Testing speech-to-text...")
        
        # Look for audio files
        if audio_file is None:
            test_files = ["test_audio.wav", "sample.mp3", "audio.flac", "test.wav", "speech.wav"]
            for test_file in test_files:
                if os.path.exists(test_file):
                    audio_file = test_file
                    break
        
        if audio_file is None or not os.path.exists(audio_file):
            print("   ⚠️  No audio file found for testing")
            print("   📁 Place an audio file in the current directory:")
            print("      - test_audio.wav")
            print("      - sample.mp3") 
            print("      - audio.flac")
            print("      - test.wav")
            print("      - speech.wav")
            print("   💡 Or provide a custom audio file path")
            
            self.test_results['speech_to_text'] = {'status': 'skipped', 'reason': 'no_audio_file'}
            return True  # Not a failure, just no file to test
        
        try:
            print(f"   📁 Testing with: {audio_file}")
            
            with open(audio_file, 'rb') as audio_f:
                files = {'audio': audio_f}
                data = {'source_lang': 'eng'}
                
                start_time = time.time()
                response = self.session.post(
                    f"{self.base_url}/speech-to-text",
                    files=files,
                    data=data,
                    timeout=60  # Longer timeout for audio processing
                )
                end_time = time.time()
                
                response.raise_for_status()
                result = response.json()
                
                print(f"   ✅ Speech-to-text successful")
                print(f"   📝 Transcription: '{result['transcription']}'")
                print(f"   🌍 Language: {result['source_language']}")
                print(f"   ⏱️  Processing time: {end_time - start_time:.2f} seconds")
                
                self.test_results['speech_to_text'] = {
                    'status': 'passed',
                    'transcription': result['transcription'],
                    'processing_time': end_time - start_time
                }
                
                return True
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.test_results['speech_to_text'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def step_5_test_different_languages(self) -> bool:
        """Step 5: Test with different languages (if audio file available)."""
        print("\n🌐 Step 5: Testing different languages...")
        
        # Look for audio files
        test_files = ["test_audio.wav", "sample.mp3", "audio.flac", "test.wav", "speech.wav"]
        audio_file = None
        for test_file in test_files:
            if os.path.exists(test_file):
                audio_file = test_file
                break
        
        if audio_file is None:
            print("   ⚠️  No audio file found for language testing")
            self.test_results['language_testing'] = {'status': 'skipped', 'reason': 'no_audio_file'}
            return True
        
        # Test with different languages
        test_languages = ['eng', 'hin', 'tel', 'ben', 'tam']
        successful_tests = 0
        
        for lang in test_languages:
            try:
                print(f"   🌍 Testing {lang}...")
                
                with open(audio_file, 'rb') as audio_f:
                    files = {'audio': audio_f}
                    data = {'source_lang': lang}
                    
                    response = self.session.post(
                        f"{self.base_url}/speech-to-text",
                        files=files,
                        data=data,
                        timeout=60
                    )
                    
                    response.raise_for_status()
                    result = response.json()
                    
                    print(f"      ✅ {lang}: '{result['transcription']}'")
                    successful_tests += 1
                    
            except Exception as e:
                print(f"      ❌ {lang}: {e}")
        
        print(f"   📊 Language tests: {successful_tests}/{len(test_languages)} successful")
        
        self.test_results['language_testing'] = {
            'status': 'passed' if successful_tests > 0 else 'failed',
            'successful_tests': successful_tests,
            'total_tests': len(test_languages)
        }
        
        return successful_tests > 0
    
    def run_full_workflow(self, audio_file: Optional[str] = None) -> Dict[str, Any]:
        """Run the complete workflow."""
        print("=" * 60)
        print("🚀 Indic-Seamless Speech-to-Text Service Workflow Test")
        print("=" * 60)
        
        steps = [
            ("Health Check", self.step_1_check_service_health),
            ("Supported Languages", self.step_2_get_supported_languages),
            ("Root Endpoint", self.step_3_test_root_endpoint),
            ("Speech-to-Text", lambda: self.step_4_test_speech_to_text(audio_file)),
            ("Language Testing", self.step_5_test_different_languages)
        ]
        
        passed_steps = 0
        total_steps = len(steps)
        
        for step_name, step_func in steps:
            try:
                if step_func():
                    passed_steps += 1
            except Exception as e:
                print(f"   ❌ Unexpected error in {step_name}: {e}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 WORKFLOW SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {passed_steps}/{total_steps} steps")
        
        if passed_steps == total_steps:
            print("🎉 All tests passed! Service is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the details above.")
        
        # Detailed results
        print("\n📋 Detailed Results:")
        for step_name, step_func in steps:
            step_key = step_name.lower().replace(" ", "_")
            if step_key in self.test_results:
                result = self.test_results[step_key]
                status = result.get('status', 'unknown')
                print(f"   {step_name}: {status}")
        
        print("=" * 60)
        
        return {
            'passed_steps': passed_steps,
            'total_steps': total_steps,
            'success': passed_steps == total_steps,
            'results': self.test_results
        }

def main():
    """Main function to run the workflow."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Indic-Seamless Speech-to-Text Service")
    parser.add_argument("--url", default="http://localhost:8000", help="Service URL")
    parser.add_argument("--audio", help="Path to audio file for testing")
    
    args = parser.parse_args()
    
    # Create workflow instance
    workflow = STTServiceWorkflow(args.url)
    
    # Run workflow
    results = workflow.run_full_workflow(args.audio)
    
    # Exit with appropriate code
    sys.exit(0 if results['success'] else 1)

if __name__ == "__main__":
    main() 
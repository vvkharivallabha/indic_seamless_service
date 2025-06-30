#!/usr/bin/env python3
"""
SageMaker Client Example for Indic-Seamless Model
This script demonstrates how to use the SageMaker endpoint.
"""

import json
import base64
import requests
import boto3
import sagemaker
from sagemaker.predictor import Predictor
import numpy as np
import soundfile as sf
import tempfile
import os

class SageMakerIndicSeamlessClient:
    """Client for the SageMaker Indic-Seamless endpoint."""
    
    def __init__(self, endpoint_name: str, region: str = "us-east-1"):
        """
        Initialize the client.
        
        Args:
            endpoint_name: Name of the SageMaker endpoint
            region: AWS region
        """
        self.endpoint_name = endpoint_name
        self.region = region
        
        # Initialize SageMaker predictor
        self.predictor = Predictor(
            endpoint_name=endpoint_name,
            sagemaker_session=sagemaker.Session(),
            serializer=sagemaker.serializers.JSONSerializer(),
            deserializer=sagemaker.deserializers.JSONDeserializer()
        )
    
    def translate_text(self, text: str, source_lang: str = "en", target_lang: str = "hi"):
        """
        Translate text between languages.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translation result
        """
        payload = {
            "task_type": "translate",
            "text": text,
            "source_lang": source_lang,
            "target_lang": target_lang
        }
        
        response = self.predictor.predict(payload)
        return response
    
    def text_to_speech(self, text: str, target_lang: str = "en", output_file: str = None):
        """
        Convert text to speech.
        
        Args:
            text: Text to convert to speech
            target_lang: Target language code
            output_file: Optional file path to save audio
            
        Returns:
            Audio data as bytes
        """
        payload = {
            "task_type": "text_to_speech",
            "text": text,
            "target_lang": target_lang
        }
        
        response = self.predictor.predict(payload)
        
        # Decode audio from base64
        audio_bytes = base64.b64decode(response["audio_base64"])
        
        if output_file:
            with open(output_file, 'wb') as f:
                f.write(audio_bytes)
            print(f"Audio saved to: {output_file}")
        
        return audio_bytes
    
    def speech_to_text(self, audio_file: str, source_lang: str = "en"):
        """
        Convert speech to text.
        
        Args:
            audio_file: Path to audio file
            source_lang: Source language code
            
        Returns:
            Transcription result
        """
        # Read and encode audio file
        with open(audio_file, 'rb') as f:
            audio_bytes = f.read()
        
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        payload = {
            "task_type": "speech_to_text",
            "audio_base64": audio_b64,
            "source_lang": source_lang
        }
        
        response = self.predictor.predict(payload)
        return response
    
    def speech_to_speech(self, audio_file: str, source_lang: str, target_lang: str, 
                        output_file: str = None):
        """
        Convert speech from one language to another.
        
        Args:
            audio_file: Path to input audio file
            source_lang: Source language code
            target_lang: Target language code
            output_file: Optional file path to save output audio
            
        Returns:
            Translated audio data as bytes
        """
        # Read and encode audio file
        with open(audio_file, 'rb') as f:
            audio_bytes = f.read()
        
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        payload = {
            "task_type": "speech_to_speech",
            "audio_base64": audio_b64,
            "source_lang": source_lang,
            "target_lang": target_lang
        }
        
        response = self.predictor.predict(payload)
        
        # Decode audio from base64
        audio_bytes = base64.b64decode(response["audio_base64"])
        
        if output_file:
            with open(output_file, 'wb') as f:
                f.write(audio_bytes)
            print(f"Translated audio saved to: {output_file}")
        
        return audio_bytes

def create_test_audio(duration=3, sample_rate=16000, output_file="test_audio.wav"):
    """Create a test audio file."""
    # Generate a simple sine wave
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio = 0.3 * np.sin(2 * np.pi * 440 * t)  # 440 Hz tone
    
    # Save audio
    sf.write(output_file, audio, sample_rate)
    return output_file

def main():
    """Example usage of the SageMaker client."""
    
    # Configuration
    ENDPOINT_NAME = "indic-seamless-endpoint"  # Update with your endpoint name
    REGION = "us-east-1"
    
    print("=" * 60)
    print("SageMaker Indic-Seamless Client Example")
    print("=" * 60)
    
    try:
        # Initialize client
        client = SageMakerIndicSeamlessClient(ENDPOINT_NAME, REGION)
        
        # Test 1: Text Translation
        print("\n1. Testing text translation...")
        translations = [
            ("Hello, how are you?", "en", "hi"),
            ("Good morning", "en", "te"),
            ("Thank you", "en", "bn"),
        ]
        
        for text, src_lang, tgt_lang in translations:
            result = client.translate_text(text, src_lang, tgt_lang)
            print(f"   {src_lang} -> {tgt_lang}: '{text}' -> '{result['translated_text']}'")
        
        # Test 2: Text-to-Speech
        print("\n2. Testing text-to-speech...")
        tts_examples = [
            ("Hello, this is a test.", "en", "test_english_sm.wav"),
            ("नमस्ते, यह एक परीक्षण है।", "hi", "test_hindi_sm.wav"),
        ]
        
        for text, lang, filename in tts_examples:
            print(f"   Generating speech for '{text}' in {lang}...")
            audio_data = client.text_to_speech(text, lang, filename)
            print(f"   Audio generated: {len(audio_data)} bytes")
        
        # Test 3: Speech-to-Text
        print("\n3. Testing speech-to-text...")
        if os.path.exists("test_english_sm.wav"):
            result = client.speech_to_text("test_english_sm.wav", "en")
            print(f"   Transcription: '{result['transcription']}'")
        
        # Test 4: Speech-to-Speech
        print("\n4. Testing speech-to-speech translation...")
        if os.path.exists("test_english_sm.wav"):
            print("   Translating English speech to Hindi...")
            audio_data = client.speech_to_speech(
                "test_english_sm.wav", "en", "hi", "translated_speech_sm.wav"
            )
            print(f"   Translated audio generated: {len(audio_data)} bytes")
        
        print("\n" + "=" * 60)
        print("Example completed successfully!")
        print("=" * 60)
        
        # Clean up generated files
        cleanup_files = ["test_english_sm.wav", "test_hindi_sm.wav", "translated_speech_sm.wav"]
        for filename in cleanup_files:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"Cleaned up: {filename}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure:")
        print("1. The SageMaker endpoint is deployed and running")
        print("2. You have the correct endpoint name")
        print("3. Your AWS credentials are configured")
        print("4. You have the necessary permissions")

if __name__ == "__main__":
    main() 
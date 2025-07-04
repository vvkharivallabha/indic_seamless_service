#!/usr/bin/env python3
"""
Client Example for Indic-Seamless Speech-to-Text Service
This script demonstrates how to use the speech-to-text service from Python code.
"""

import os
from typing import Any, Dict

import requests


class IndicSeamlessSTTClient:
    """Client for the Indic-Seamless Speech-to-Text Service."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client.

        Args:
            base_url: Base URL of the service
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def get_supported_languages(self) -> Dict[str, Any]:
        """Get list of supported languages."""
        response = self.session.get(f"{self.base_url}/supported-languages")
        response.raise_for_status()
        return response.json()

    def speech_to_text(
        self, audio_file: str, target_lang: str = "English"
    ) -> Dict[str, Any]:
        """
        Convert speech to text.

        Args:
            audio_file: Path to audio file
            target_lang: Target language for transcription

        Returns:
            Transcription result
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        with open(audio_file, "rb") as audio_f:
            files = {"audio": audio_f}
            data = {"target_lang": target_lang}

            response = self.session.post(
                f"{self.base_url}/speech-to-text", files=files, data=data
            )
            response.raise_for_status()
            return response.json()


def main():
    """Example usage of the Indic-Seamless Speech-to-Text client."""

    # Initialize client
    client = IndicSeamlessSTTClient()

    print("=" * 60)
    print("Indic-Seamless Speech-to-Text Service Client Example")
    print("=" * 60)

    try:
        # Check service health
        print("1. Checking service health...")
        health = client.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Model loaded: {health['model_loaded']}")
        print(f"   Device: {health['device']}")

        # Get supported languages
        print("\n2. Getting supported languages...")
        languages = client.get_supported_languages()
        print(f"   Total languages: {languages['count']}")

        # Show some key Indian languages
        indian_languages = [
            "eng",
            "hin",
            "tel",
            "ben",
            "tam",
            "mar",
            "guj",
            "kan",
            "mal",
            "urd",
        ]
        print("   Key Indian languages:")
        for lang_code in indian_languages:
            if lang_code in languages["languages"]:
                print(f"     {lang_code}: {languages['languages'][lang_code]}")

        # Speech-to-text example
        print("\n3. Speech-to-text example...")
        print("   Note: This requires an actual audio file.")
        print(
            "   You can test with any audio file in supported formats "
            "(wav, mp3, flac, m4a, ogg)"
        )

        # Example usage instructions
        print("\n4. Usage instructions:")
        print("   To test speech-to-text:")
        print("   - Place an audio file in the current directory")
        print("   - Update the audio_file variable below")
        print("   - Run the script")

        # Example with a test file (if it exists)
        test_files = ["test_audio.wav", "sample.mp3", "audio.flac"]
        for test_file in test_files:
            if os.path.exists(test_file):
                print(f"\n   Testing with {test_file}...")
                try:
                    result = client.speech_to_text(test_file, "English")
                    print(f"   Transcription: '{result['transcription']}'")
                    break
                except Exception as e:
                    print(f"   Error processing {test_file}: {e}")

        print("\n" + "=" * 60)
        print("Example completed successfully!")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the service.")
        print("   Make sure the service is running on http://localhost:8000")
        print("   Run: python start_service.py")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
SageMaker Inference Script for Indic-Seamless Model
This script handles model loading and inference for SageMaker endpoints.
"""

import os
import json
import logging
import tempfile
import base64
from typing import Dict, Any, List
import traceback

import torch
import numpy as np
from transformers import AutoProcessor, AutoModel
import soundfile as sf
import librosa

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model variables
model = None
processor = None
device = None

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi', 
    'bn': 'Bengali',
    'te': 'Telugu',
    'ta': 'Tamil',
    'mr': 'Marathi',
    'gu': 'Gujarati',
    'kn': 'Kannada',
    'ml': 'Malayalam',
    'pa': 'Punjabi',
    'or': 'Odia',
    'as': 'Assamese'
}

def model_fn(model_dir: str) -> None:
    """
    Load the model for inference.
    
    Args:
        model_dir: Directory containing the model files
    """
    global model, processor, device
    
    try:
        logger.info(f"Loading model from {model_dir}")
        
        # Set device
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {device}")
        
        # Load model and processor
        model_name = "ai4bharat/indic-seamless"
        processor = AutoProcessor.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)
        
        # Move model to device
        model = model.to(device)
        model.eval()
        
        logger.info("Model loaded successfully!")
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def preprocess_audio(audio_data: bytes, target_sr: int = 16000):
    """Preprocess audio data to the required format."""
    try:
        # Save audio data to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_file.flush()
            
            # Load audio
            audio, sr = librosa.load(temp_file.name, sr=target_sr)
            os.unlink(temp_file.name)
        
        # Ensure mono channel
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)
        
        # Normalize audio
        audio = audio / np.max(np.abs(audio))
        
        return audio, target_sr
        
    except Exception as e:
        logger.error(f"Error preprocessing audio: {str(e)}")
        raise

def postprocess_audio(audio_array: np.ndarray, sample_rate: int = 16000) -> bytes:
    """Convert audio array to bytes."""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            sf.write(temp_file.name, audio_array, sample_rate)
            temp_file.seek(0)
            audio_bytes = temp_file.read()
        
        # Clean up
        os.unlink(temp_file.name)
        
        return audio_bytes
        
    except Exception as e:
        logger.error(f"Error postprocessing audio: {str(e)}")
        raise

def input_fn(request_body: bytes, request_content_type: str) -> Dict[str, Any]:
    """
    Parse input data from the request.
    
    Args:
        request_body: Raw request body
        request_content_type: Content type of the request
        
    Returns:
        Parsed input data
    """
    if request_content_type == "application/json":
        input_data = json.loads(request_body.decode('utf-8'))
        return input_data
    else:
        raise ValueError(f"Unsupported content type: {request_content_type}")

def predict_fn(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform inference on the input data.
    
    Args:
        input_data: Parsed input data
        
    Returns:
        Prediction results
    """
    try:
        task_type = input_data.get("task_type")
        
        if task_type == "translate":
            return _translate_text(input_data)
        elif task_type == "text_to_speech":
            return _text_to_speech(input_data)
        elif task_type == "speech_to_text":
            return _speech_to_text(input_data)
        elif task_type == "speech_to_speech":
            return _speech_to_speech(input_data)
        else:
            raise ValueError(f"Unsupported task type: {task_type}")
            
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def _translate_text(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Translate text between languages."""
    text = input_data["text"]
    source_lang = input_data.get("source_lang", "en")
    target_lang = input_data.get("target_lang", "en")
    
    # Validate languages
    if source_lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported source language: {source_lang}")
    if target_lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported target language: {target_lang}")
    
    # Prepare input
    inputs = processor(
        text=text,
        return_tensors="pt",
        src_lang=source_lang
    ).to(device)
    
    # Generate translation
    with torch.no_grad():
        generated_ids = model.generate(
            **inputs,
            forced_bos_token_id=processor.tokenizer.lang_code_to_token[target_lang]
        )
    
    # Decode translation
    translation = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    return {
        "task_type": "translate",
        "original_text": text,
        "translated_text": translation,
        "source_language": source_lang,
        "target_language": target_lang
    }

def _text_to_speech(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert text to speech."""
    text = input_data["text"]
    target_lang = input_data.get("target_lang", "en")
    
    # Validate language
    if target_lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {target_lang}")
    
    # Prepare input
    inputs = processor(
        text=text,
        return_tensors="pt",
        src_lang=target_lang
    ).to(device)
    
    # Generate speech
    with torch.no_grad():
        speech = model.generate_speech(
            **inputs,
            vocoder=None,
            src_lang=target_lang
        )
    
    # Convert to audio bytes
    speech = speech.cpu().numpy()
    audio_bytes = postprocess_audio(speech)
    
    # Encode as base64 for JSON response
    audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
    
    return {
        "task_type": "text_to_speech",
        "text": text,
        "target_language": target_lang,
        "audio_base64": audio_b64,
        "audio_format": "wav"
    }

def _speech_to_text(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert speech to text."""
    audio_b64 = input_data["audio_base64"]
    source_lang = input_data.get("source_lang", "en")
    
    # Validate language
    if source_lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {source_lang}")
    
    # Decode audio
    audio_bytes = base64.b64decode(audio_b64)
    audio_data, sr = preprocess_audio(audio_bytes)
    
    # Prepare input
    inputs = processor(
        audio=audio_data,
        sampling_rate=sr,
        return_tensors="pt",
        src_lang=source_lang
    ).to(device)
    
    # Generate transcription
    with torch.no_grad():
        generated_ids = model.generate(
            **inputs,
            forced_bos_token_id=processor.tokenizer.lang_code_to_token[source_lang]
        )
    
    # Decode transcription
    transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    return {
        "task_type": "speech_to_text",
        "transcription": transcription,
        "source_language": source_lang,
        "confidence": 1.0
    }

def _speech_to_speech(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert speech from one language to another."""
    audio_b64 = input_data["audio_base64"]
    source_lang = input_data["source_lang"]
    target_lang = input_data["target_lang"]
    
    # Validate languages
    if source_lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported source language: {source_lang}")
    if target_lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported target language: {target_lang}")
    
    # Decode audio
    audio_bytes = base64.b64decode(audio_b64)
    audio_data, sr = preprocess_audio(audio_bytes)
    
    # Prepare input
    inputs = processor(
        audio=audio_data,
        sampling_rate=sr,
        return_tensors="pt",
        src_lang=source_lang
    ).to(device)
    
    # Generate speech in target language
    with torch.no_grad():
        speech = model.generate_speech(
            **inputs,
            vocoder=None,
            src_lang=source_lang,
            tgt_lang=target_lang
        )
    
    # Convert to audio bytes
    speech = speech.cpu().numpy()
    audio_bytes = postprocess_audio(speech)
    
    # Encode as base64 for JSON response
    audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
    
    return {
        "task_type": "speech_to_speech",
        "source_language": source_lang,
        "target_language": target_lang,
        "audio_base64": audio_b64,
        "audio_format": "wav"
    }

def output_fn(prediction: Dict[str, Any], content_type: str) -> bytes:
    """
    Format the prediction output.
    
    Args:
        prediction: Prediction results
        content_type: Expected content type
        
    Returns:
        Formatted output
    """
    if content_type == "application/json":
        return json.dumps(prediction).encode('utf-8')
    else:
        raise ValueError(f"Unsupported content type: {content_type}")

# For local testing
if __name__ == "__main__":
    # Test the model loading
    model_fn("/tmp")
    
    # Test translation
    test_input = {
        "task_type": "translate",
        "text": "Hello, how are you?",
        "source_lang": "en",
        "target_lang": "hi"
    }
    
    result = predict_fn(test_input)
    print(json.dumps(result, indent=2)) 
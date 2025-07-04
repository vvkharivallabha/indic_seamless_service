"""
API routes for Indic-Seamless Service
"""

import os
import logging
import tempfile
import traceback
import torch
from fastapi import APIRouter, File, UploadFile, Form, HTTPException

from src.config import TargetLanguage, LANGUAGE_NAME_TO_CODE, SUPPORTED_LANGUAGES
from src.config.settings import settings
from src.types import STTResponse, HealthResponse, LanguagesResponse, ModelState
from src.utils import preprocess_audio, allowed_file, load_model, safe_decode_tokens

logger = logging.getLogger(__name__)

# Global model state
model_state = ModelState()

# Create router
router = APIRouter()


@router.on_event("startup")
async def startup_event():
    """Load model on startup."""
    if not load_model(model_state):
        logger.error("Failed to load model. Service may not function correctly.")


@router.get("/", tags=["Info"])
async def root():
    """Root endpoint with service information."""
    return {
        "service": settings.title,
        "version": settings.version,
        "description": settings.description,
        "documentation": settings.docs_url,
        "health": "/health",
        "supported_languages": "/supported-languages",
        "endpoints": {
            "speech_to_text": "/speech-to-text",
            "health": "/health",
            "supported_languages": "/supported-languages"
        }
    }


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        model_loaded=model_state.is_ready(),
        device=str(model_state.device) if model_state.device else None,
        supported_languages=SUPPORTED_LANGUAGES
    )


@router.get("/supported-languages", response_model=LanguagesResponse, tags=["Info"])
async def get_supported_languages():
    """Get list of supported languages."""
    return LanguagesResponse(
        languages=SUPPORTED_LANGUAGES,
        count=len(SUPPORTED_LANGUAGES)
    )


@router.post("/speech-to-text", response_model=STTResponse, tags=["Speech Processing"])
async def speech_to_text(
    audio: UploadFile = File(..., description="Audio file (wav, mp3, flac, m4a, ogg)"),
    target_lang: TargetLanguage = Form(default=TargetLanguage.English, description="Target language for transcription")
):
    """Convert speech to text (ASR)."""
    try:
        # Check if model is loaded
        if not model_state.is_ready():
            raise HTTPException(status_code=503, detail="Model not loaded. Please try again later.")
        
        # Validate file
        if not allowed_file(audio.filename or ""):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file format. Allowed: {', '.join(settings.allowed_extensions)}"
            )
        
        # Convert full language name to language code for the model
        language_code = LANGUAGE_NAME_TO_CODE.get(target_lang.value)
        if not language_code:
            raise HTTPException(status_code=400, detail=f"Unsupported language: {target_lang.value}")
        
        logger.info(f"Processing audio with target language: {target_lang.value} (code: {language_code})")
        
        # Save and preprocess audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            content = await audio.read()
            temp_file.write(content)
            temp_file.flush()
            
            audio_data, sr = preprocess_audio(temp_file.name)
            os.unlink(temp_file.name)
        
        # Prepare input using feature extractor for audio
        inputs = model_state.processor(
            audio_data,
            sampling_rate=sr,
            return_tensors="pt"
        ).to(model_state.device)
        
        # Generate transcription using the correct method for SeamlessM4Tv2
        with torch.no_grad():
            text_out = model_state.model.generate(
                **inputs,
                tgt_lang=language_code  # Use the language code for the model
            )
        
        # Decode transcription
        transcription = model_state.tokenizer.decode(
            text_out[0].cpu().numpy().squeeze(), 
            clean_up_tokenization_spaces=True, 
            skip_special_tokens=True
        )
        
        return STTResponse(transcription=transcription)
        
    except Exception as e:
        logger.error(f"Error in speech-to-text: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e)) 
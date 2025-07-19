"""
API routes for Indic-Seamless Service
"""

import logging
import os
import tempfile
import traceback

import torch
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from src.config import LANGUAGE_NAME_TO_CODE, SUPPORTED_LANGUAGES, TargetLanguage
from src.config.settings import settings
from src.types import HealthResponse, LanguagesResponse, STTResponse
from src.utils import allowed_file, preprocess_audio
from src.utils.model import load_model, model_state

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


def ensure_model_loaded() -> None:
    """Ensure model is loaded (load on first request if needed)."""
    if model_state.model is None:
        logger.info("Model not loaded, loading now...")
        try:
            load_model()
            logger.info("✅ Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise HTTPException(
                status_code=503,
                detail="Failed to load model. Please try again later.",
            )


def is_model_ready() -> bool:
    """Check if model is ready for inference."""
    return (
        model_state.model is not None
        and model_state.processor is not None
        and model_state.tokenizer is not None
        and model_state.device is not None
    )


@router.get("/", tags=["Info"])
async def root() -> dict:
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
            "supported_languages": "/supported-languages",
        },
    }


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    # Try to load model if not already loaded
    try:
        ensure_model_loaded()
    except HTTPException:
        # Model loading failed, but we still return health info
        pass

    return HealthResponse(
        status="healthy",
        model_loaded=is_model_ready(),
        device=str(model_state.device) if model_state.device else None,
        supported_languages=SUPPORTED_LANGUAGES,
    )


@router.get(
    "/supported-languages",
    response_model=LanguagesResponse,
    tags=["Info"],
)
async def get_supported_languages() -> LanguagesResponse:
    """Get list of supported languages."""
    return LanguagesResponse(
        languages=SUPPORTED_LANGUAGES, count=len(SUPPORTED_LANGUAGES)
    )


@router.post(
    "/speech-to-text",
    response_model=STTResponse,
    tags=["Speech Processing"],
)
async def speech_to_text(
    audio: UploadFile = File(..., description="Audio file (wav, mp3, flac, m4a, ogg)"),
    target_lang: TargetLanguage = Form(
        default=TargetLanguage.English,
        description="Target language for transcription",
    ),
) -> STTResponse:
    """Convert speech to text (ASR)."""
    try:
        # Ensure model is loaded (load on first request if needed)
        ensure_model_loaded()

        # Type assertions for linter - guaranteed by is_ready() check
        assert model_state.model is not None
        assert model_state.processor is not None
        assert model_state.tokenizer is not None

        # Validate file
        if not allowed_file(audio.filename or ""):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file format. Allowed: "
                f"{', '.join(settings.allowed_extensions)}",
            )

        # Convert full language name to language code for the model
        language_code = LANGUAGE_NAME_TO_CODE.get(target_lang.value)
        if not language_code:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language: {target_lang.value}",
            )

        logger.info(
            f"Processing audio with target language: {target_lang.value} "
            f"(code: {language_code})"
        )

        # Save and preprocess audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio.read()
            temp_file.write(content)
            temp_file.flush()

            audio_data, sr = preprocess_audio(temp_file.name)
            os.unlink(temp_file.name)

        # Prepare input using feature extractor for audio
        # Convert tensor to numpy array for processor
        audio_array = (
            audio_data.numpy() if isinstance(audio_data, torch.Tensor) else audio_data
        )
        inputs = model_state.processor(
            audio_array, sampling_rate=sr, return_tensors="pt"
        ).to(model_state.device)

        # Generate transcription using the correct method for SeamlessM4Tv2
        with torch.no_grad():
            text_out = model_state.model.generate(**inputs, tgt_lang=language_code)

        # Decode transcription
        transcription = model_state.tokenizer.decode(
            text_out[0].cpu().numpy().squeeze(),
            clean_up_tokenization_spaces=True,
            skip_special_tokens=True,
        )

        return STTResponse(transcription=transcription)

    except Exception as e:
        logger.error(f"Error in speech-to-text: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

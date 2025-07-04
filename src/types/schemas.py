"""
Pydantic schemas for API request and response models
"""

from typing import Dict, Optional
from pydantic import BaseModel, Field


class STTRequest(BaseModel):
    """Speech-to-text request model"""

    target_lang: str = Field(..., description="Target language for transcription")

    class Config:
        json_schema_extra = {"example": {"target_lang": "English"}}


class STTResponse(BaseModel):
    """Speech-to-text response model"""

    transcription: str = Field(..., description="Transcribed text from audio")

    class Config:
        json_schema_extra = {
            "example": {"transcription": "Hello, this is a sample transcription."}
        }


class HealthResponse(BaseModel):
    """Health check response model"""

    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether the ML model is loaded")
    device: Optional[str] = Field(None, description="Device being used (CPU/CUDA)")
    supported_languages: Dict[str, str] = Field(
        ..., description="Mapping of language codes to names"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "model_loaded": True,
                "device": "cuda:0",
                "supported_languages": {
                    "eng": "English",
                    "hin": "Hindi",
                    "ben": "Bengali",
                },
            }
        }


class LanguagesResponse(BaseModel):
    """Supported languages response model"""

    languages: Dict[str, str] = Field(
        ..., description="Mapping of language codes to names"
    )
    count: int = Field(..., description="Total number of supported languages")

    class Config:
        json_schema_extra = {
            "example": {
                "languages": {
                    "eng": "English",
                    "hin": "Hindi",
                    "ben": "Bengali",
                    "tam": "Tamil",
                },
                "count": 98,
            }
        }

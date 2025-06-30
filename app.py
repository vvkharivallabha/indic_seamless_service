#!/usr/bin/env python3
"""
Indic-Seamless Speech-to-Text Service
A FastAPI-based REST API service for hosting the ai4bharat/indic-seamless model for speech-to-text conversion.
"""

import os
import logging
import tempfile
from typing import Dict, List, Optional
import traceback
from enum import Enum

import torchaudio
import torch
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import SeamlessM4Tv2ForSpeechToText, SeamlessM4TTokenizer, SeamlessM4TFeatureExtractor
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class STTResponse(BaseModel):
    transcription: str

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    device: Optional[str]
    supported_languages: Dict[str, str]

class LanguagesResponse(BaseModel):
    languages: Dict[str, str]
    count: int

# Supported languages enum for dropdown in FastAPI docs
class TargetLanguage(str, Enum):
    Afrikaans = "afr"
    Amharic = "amh"
    Modern_Standard_Arabic = "arb"
    Moroccan_Arabic = "ary"
    Egyptian_Arabic = "arz"
    Assamese = "asm"
    North_Azerbaijani = "azj"
    Belarusian = "bel"
    Bengali = "ben"
    Bosnian = "bos"
    Bulgarian = "bul"
    Catalan = "cat"
    Cebuano = "ceb"
    Czech = "ces"
    Central_Kurdish = "ckb"
    Mandarin_Chinese = "cmn"
    Traditional_Chinese = "cmn_Hant"
    Welsh = "cym"
    Danish = "dan"
    German = "deu"
    Greek = "ell"
    English = "eng"
    Estonian = "est"
    Basque = "eus"
    Finnish = "fin"
    French = "fra"
    Nigerian_Fulfulde = "fuv"
    West_Central_Oromo = "gaz"
    Irish = "gle"
    Galician = "glg"
    Gujarati = "guj"
    Hebrew = "heb"
    Hindi = "hin"
    Croatian = "hrv"
    Hungarian = "hun"
    Armenian = "hye"
    Igbo = "ibo"
    Indonesian = "ind"
    Icelandic = "isl"
    Italian = "ita"
    Javanese = "jav"
    Japanese = "jpn"
    Kannada = "kan"
    Georgian = "kat"
    Kazakh = "kaz"
    Halh_Mongolian = "khk"
    Khmer = "khm"
    Kyrgyz = "kir"
    Korean = "kor"
    Lao = "lao"
    Lithuanian = "lit"
    Ganda = "lug"
    Luo = "luo"
    Standard_Latvian = "lvs"
    Maithili = "mai"
    Malayalam = "mal"
    Marathi = "mar"
    Macedonian = "mkd"
    Maltese = "mlt"
    Manipuri = "mni"
    Burmese = "mya"
    Dutch = "nld"
    Norwegian_Nynorsk = "nno"
    Norwegian_Bokmal = "nob"
    Nepali = "npi"
    Nyanja = "nya"
    Odia = "ory"
    Punjabi = "pan"
    Southern_Pashto = "pbt"
    Western_Persian = "pes"
    Polish = "pol"
    Portuguese = "por"
    Romanian = "ron"
    Russian = "rus"
    Santali = "sat"
    Slovak = "slk"
    Slovenian = "slv"
    Shona = "sna"
    Sindhi = "snd"
    Somali = "som"
    Spanish = "spa"
    Serbian = "srp"
    Swedish = "swe"
    Swahili = "swh"
    Tamil = "tam"
    Telugu = "tel"
    Tajik = "tgk"
    Tagalog = "tgl"
    Thai = "tha"
    Turkish = "tur"
    Ukrainian = "ukr"
    Urdu = "urd"
    Northern_Uzbek = "uzn"
    Vietnamese = "vie"
    Yoruba = "yor"
    Cantonese = "yue"
    Colloquial_Malay = "zlm"
    Zulu = "zul"

# Initialize FastAPI app
app = FastAPI(
    title="Indic-Seamless Speech-to-Text Service",
    description="A production-ready REST API service for speech-to-text conversion using the ai4bharat/indic-seamless model",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model variables
model = None
processor = None
tokenizer = None
device = None

# Configuration
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac', 'm4a', 'ogg'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
SUPPORTED_LANGUAGES = {
    'afr': 'Afrikaans',
    'amh': 'Amharic',
    'arb': 'Modern Standard Arabic',
    'ary': 'Moroccan Arabic',
    'arz': 'Egyptian Arabic',
    'asm': 'Assamese',
    'azj': 'North Azerbaijani',
    'bel': 'Belarusian',
    'ben': 'Bengali',
    'bos': 'Bosnian',
    'bul': 'Bulgarian',
    'cat': 'Catalan',
    'ceb': 'Cebuano',
    'ces': 'Czech',
    'ckb': 'Central Kurdish',
    'cmn': 'Mandarin Chinese',
    'cmn_Hant': 'Traditional Chinese',
    'cym': 'Welsh',
    'dan': 'Danish',
    'deu': 'German',
    'ell': 'Greek',
    'eng': 'English',
    'est': 'Estonian',
    'eus': 'Basque',
    'fin': 'Finnish',
    'fra': 'French',
    'fuv': 'Nigerian Fulfulde',
    'gaz': 'West Central Oromo',
    'gle': 'Irish',
    'glg': 'Galician',
    'guj': 'Gujarati',
    'heb': 'Hebrew',
    'hin': 'Hindi',
    'hrv': 'Croatian',
    'hun': 'Hungarian',
    'hye': 'Armenian',
    'ibo': 'Igbo',
    'ind': 'Indonesian',
    'isl': 'Icelandic',
    'ita': 'Italian',
    'jav': 'Javanese',
    'jpn': 'Japanese',
    'kan': 'Kannada',
    'kat': 'Georgian',
    'kaz': 'Kazakh',
    'khk': 'Halh Mongolian',
    'khm': 'Khmer',
    'kir': 'Kyrgyz',
    'kor': 'Korean',
    'lao': 'Lao',
    'lit': 'Lithuanian',
    'lug': 'Ganda',
    'luo': 'Luo',
    'lvs': 'Standard Latvian',
    'mai': 'Maithili',
    'mal': 'Malayalam',
    'mar': 'Marathi',
    'mkd': 'Macedonian',
    'mlt': 'Maltese',
    'mni': 'Manipuri',
    'mya': 'Burmese',
    'nld': 'Dutch',
    'nno': 'Norwegian Nynorsk',
    'nob': 'Norwegian Bokmål',
    'npi': 'Nepali',
    'nya': 'Nyanja',
    'ory': 'Odia',
    'pan': 'Punjabi',
    'pbt': 'Southern Pashto',
    'pes': 'Western Persian',
    'pol': 'Polish',
    'por': 'Portuguese',
    'ron': 'Romanian',
    'rus': 'Russian',
    'sat': 'Santali',
    'slk': 'Slovak',
    'slv': 'Slovenian',
    'sna': 'Shona',
    'snd': 'Sindhi',
    'som': 'Somali',
    'spa': 'Spanish',
    'srp': 'Serbian',
    'swe': 'Swedish',
    'swh': 'Swahili',
    'tam': 'Tamil',
    'tel': 'Telugu',
    'tgk': 'Tajik',
    'tgl': 'Tagalog',
    'tha': 'Thai',
    'tur': 'Turkish',
    'ukr': 'Ukrainian',
    'urd': 'Urdu',
    'uzn': 'Northern Uzbek',
    'vie': 'Vietnamese',
    'yor': 'Yoruba',
    'yue': 'Cantonese',
    'zlm': 'Colloquial Malay',
    'zul': 'Zulu'
}

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_model():
    """Load the indic-seamless model."""
    global model, processor, tokenizer, device
    
    try:
        logger.info("Loading indic-seamless model...")
        
        # Set device
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {device}")
        
        # Load model and processor with trust_remote_code=True
        model_name = "ai4bharat/indic-seamless"
        processor = SeamlessM4TFeatureExtractor.from_pretrained(
            model_name, 
            trust_remote_code=True
        )
        tokenizer = SeamlessM4TTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        model = SeamlessM4Tv2ForSpeechToText.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        
        # Move model to device
        model = model.to(device)
        model.eval()
        
        logger.info("Model loaded successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def preprocess_audio(audio_file: str, target_sr: int = 16000):
    """Preprocess audio file to the required format."""
    try:
        audio, orig_freq = torchaudio.load(audio_file)
        audio = torchaudio.functional.resample(audio, orig_freq=orig_freq, new_freq=target_sr)
        return audio, target_sr
        
    except Exception as e:
        logger.error(f"Error preprocessing audio: {str(e)}")
        raise

def safe_decode_tokens(tokenizer, generated_ids, skip_special_tokens=True):
    """Safely decode token IDs to text."""
    try:
        # Handle different output formats
        if isinstance(generated_ids, torch.Tensor):
            if generated_ids.dim() == 2:
                # Batch of sequences - take the first sequence
                return tokenizer.batch_decode(generated_ids, skip_special_tokens=skip_special_tokens)[0]
            else:
                # Single sequence
                return tokenizer.batch_decode([generated_ids], skip_special_tokens=skip_special_tokens)[0]
        elif isinstance(generated_ids, list):
            # Check if it's a list of lists (batch) or list of integers (single sequence)
            if generated_ids and isinstance(generated_ids[0], list):
                # List of lists - take the first sequence
                return tokenizer.batch_decode(generated_ids, skip_special_tokens=skip_special_tokens)[0]
            else:
                # Single list of token IDs
                return tokenizer.batch_decode([generated_ids], skip_special_tokens=skip_special_tokens)[0]
        else:
            # Try to convert to list
            if hasattr(generated_ids, 'tolist'):
                ids_list = generated_ids.tolist()
            else:
                ids_list = list(generated_ids)
            
            # Handle the converted list
            if ids_list and isinstance(ids_list[0], list):
                # List of lists - take the first sequence
                return tokenizer.batch_decode(ids_list, skip_special_tokens=skip_special_tokens)[0]
            else:
                # Single list of token IDs
                return tokenizer.batch_decode([ids_list], skip_special_tokens=skip_special_tokens)[0]
                
    except Exception as e:
        logger.error(f"Error decoding tokens: {str(e)}")
        logger.error(f"Generated IDs type: {type(generated_ids)}")
        logger.error(f"Generated IDs shape: {getattr(generated_ids, 'shape', 'N/A')}")
        if isinstance(generated_ids, list):
            logger.error(f"Generated IDs length: {len(generated_ids)}")
            if generated_ids:
                logger.error(f"First element type: {type(generated_ids[0])}")
                logger.error(f"First element: {generated_ids[0]}")
        raise

@app.on_event("startup")
async def startup_event():
    """Load model on startup."""
    if not load_model():
        logger.error("Failed to load model. Service may not function correctly.")

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        model_loaded=model is not None and processor is not None and tokenizer is not None,
        device=str(device) if device else None,
        supported_languages=SUPPORTED_LANGUAGES
    )

@app.get("/supported-languages", response_model=LanguagesResponse, tags=["Info"])
async def get_supported_languages():
    """Get list of supported languages."""
    return LanguagesResponse(
        languages=SUPPORTED_LANGUAGES,
        count=len(SUPPORTED_LANGUAGES)
    )

@app.post("/speech-to-text", response_model=STTResponse, tags=["Speech Processing"])
async def speech_to_text(
    audio: UploadFile = File(..., description="Audio file (wav, mp3, flac, m4a, ogg)"),
    target_lang: TargetLanguage = Form(default=TargetLanguage.English, description="Target language for transcription")
):
    """Convert speech to text (ASR)."""
    try:
        # Check if model is loaded
        if model is None or processor is None or tokenizer is None:
            raise HTTPException(status_code=503, detail="Model not loaded. Please try again later.")
        
        # Validate file
        if not allowed_file(audio.filename or ""):
            raise HTTPException(status_code=400, detail=f"Invalid file format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
        
        # Note: target_lang validation is now handled by the TargetLanguage enum
        
        # Save and preprocess audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            content = await audio.read()
            temp_file.write(content)
            temp_file.flush()
            
            audio_data, sr = preprocess_audio(temp_file.name)
            os.unlink(temp_file.name)
        
        # Prepare input using feature extractor for audio
        inputs = processor(
            audio_data,
            sampling_rate=sr,
            return_tensors="pt"
        ).to(device)
        
        # Generate transcription using the correct method for SeamlessM4Tv2
        with torch.no_grad():
            text_out = model.generate(
                **inputs,
                tgt_lang=target_lang
            )
        
        # Decode transcription
        transcription = tokenizer.decode(text_out[0].cpu().numpy().squeeze(), clean_up_tokenization_spaces=True, skip_special_tokens=True)
        
        return STTResponse(
            transcription=transcription
        )
        
    except Exception as e:
        logger.error(f"Error in speech-to-text: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Indic-Seamless Speech-to-Text Service",
        "version": "1.0.0",
        "description": "A production-ready REST API service for speech-to-text conversion using the ai4bharat/indic-seamless model",
        "documentation": "/docs",
        "health": "/health",
        "supported_languages": "/supported-languages",
        "endpoints": {
            "speech_to_text": "/speech-to-text",
            "health": "/health",
            "supported_languages": "/supported-languages"
        }
    }

if __name__ == "__main__":
    # Run the app
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Starting Indic-Seamless Speech-to-Text service on {host}:{port}")
    uvicorn.run(app, host=host, port=port) 
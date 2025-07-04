"""
Model loading and processing utilities
"""

import logging
import traceback

import torch
from transformers import (
    SeamlessM4TFeatureExtractor,
    SeamlessM4TTokenizer,
    SeamlessM4Tv2ForSpeechToText,
)

from src.config.settings import settings
from src.types import ModelState

logger = logging.getLogger(__name__)


def load_model(model_state: ModelState) -> bool:
    """
    Load the indic-seamless model and update model state.

    Args:
        model_state: ModelState object to update

    Returns:
        True if model loaded successfully, False otherwise
    """
    try:
        logger.info("Loading indic-seamless model...")
        logger.info("⏳ This may take several minutes for first-time download...")

        # Set device
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {device}")

        # Load model components
        logger.info(f"Loading model from: {settings.model_name}")

        logger.info("📥 Loading feature extractor...")
        processor = SeamlessM4TFeatureExtractor.from_pretrained(
            settings.model_name, trust_remote_code=settings.trust_remote_code
        )
        logger.info("✅ Feature extractor loaded")

        logger.info("📥 Loading tokenizer...")
        tokenizer = SeamlessM4TTokenizer.from_pretrained(
            settings.model_name, trust_remote_code=settings.trust_remote_code
        )
        logger.info("✅ Tokenizer loaded")

        logger.info("📥 Loading main model (this is the largest component)...")
        model = SeamlessM4Tv2ForSpeechToText.from_pretrained(
            settings.model_name, trust_remote_code=settings.trust_remote_code
        )
        logger.info("✅ Main model loaded")

        # Move model to device
        logger.info(f"📤 Moving model to {device}...")
        model = model.to(device)  # type: ignore[assignment]
        model.eval()
        logger.info("✅ Model moved to device and set to eval mode")

        # Update model state
        model_state.model = model
        model_state.processor = processor
        model_state.tokenizer = tokenizer
        model_state.device = device
        model_state.is_loaded = True

        logger.info("🎉 Model loaded successfully!")
        return True

    except Exception as e:
        logger.error(f"💥 Error loading model: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(traceback.format_exc())
        model_state.reset()
        return False


def safe_decode_tokens(
    tokenizer, generated_ids, skip_special_tokens: bool = True
) -> str:
    """
    Safely decode token IDs to text.

    Args:
        tokenizer: The tokenizer to use for decoding
        generated_ids: Token IDs to decode
        skip_special_tokens: Whether to skip special tokens

    Returns:
        Decoded text string

    Raises:
        Exception: If decoding fails
    """
    try:
        # Handle different output formats
        if isinstance(generated_ids, torch.Tensor):
            if generated_ids.dim() == 2:
                # Batch of sequences - take the first sequence
                return tokenizer.batch_decode(
                    generated_ids, skip_special_tokens=skip_special_tokens
                )[0]
            else:
                # Single sequence
                return tokenizer.batch_decode(
                    [generated_ids], skip_special_tokens=skip_special_tokens
                )[0]
        elif isinstance(generated_ids, list):
            # Check if it's a list of lists (batch) or list of integers
            # (single sequence)
            if generated_ids and isinstance(generated_ids[0], list):
                # List of lists - take the first sequence
                return tokenizer.batch_decode(
                    generated_ids, skip_special_tokens=skip_special_tokens
                )[0]
            else:
                # Single list of token IDs
                return tokenizer.batch_decode(
                    [generated_ids], skip_special_tokens=skip_special_tokens
                )[0]
        else:
            # Try to convert to list
            if hasattr(generated_ids, "tolist"):
                ids_list = generated_ids.tolist()
            else:
                ids_list = list(generated_ids)

            # Handle the converted list
            if ids_list and isinstance(ids_list[0], list):
                # List of lists - take the first sequence
                return tokenizer.batch_decode(
                    ids_list, skip_special_tokens=skip_special_tokens
                )[0]
            else:
                # Single list of token IDs
                return tokenizer.batch_decode(
                    [ids_list], skip_special_tokens=skip_special_tokens
                )[0]

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

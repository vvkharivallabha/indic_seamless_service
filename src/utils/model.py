"""
Model loading and processing utilities
"""

import logging
import os
from typing import Any, Optional, Tuple

import torch
from transformers import (
    SeamlessM4TFeatureExtractor,
    SeamlessM4TTokenizer,
    SeamlessM4Tv2ForSpeechToText,
)

from src.config.settings import settings

logger = logging.getLogger(__name__)


class ModelState:
    """Global model state to avoid reloading."""

    def __init__(self):
        self.model: Optional[SeamlessM4Tv2ForSpeechToText] = None
        self.processor: Optional[SeamlessM4TFeatureExtractor] = None
        self.tokenizer: Optional[SeamlessM4TTokenizer] = None
        self.device: Optional[str] = None


# Global model state
model_state = ModelState()


def get_optimal_device() -> str:
    """Get the optimal device for inference."""
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def load_model() -> Tuple[SeamlessM4Tv2ForSpeechToText, Any, Any, str]:
    """
    Load the SeamlessM4T model with memory optimizations.

    Returns:
        Tuple of (model, processor, tokenizer, device)
    """
    try:
        device = get_optimal_device()
        logger.info(f"🎯 Using device: {device}")
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

        logger.info("📥 Loading main model with aggressive memory optimizations...")
        logger.info("🔧 Using: Disk offloading, state dict offloading, minimal memory")

        # Create offload directory for model parts
        offload_dir = "/tmp/model_offload"
        os.makedirs(offload_dir, exist_ok=True)
        logger.info(f"💾 Offload directory: {offload_dir}")

        # Most aggressive memory optimization parameters
        model_kwargs = {
            "trust_remote_code": settings.trust_remote_code,
            "low_cpu_mem_usage": True,  # Reduce CPU memory during loading
            "torch_dtype": torch.float32,  # Keep as float32 for stability
            "offload_folder": offload_dir,  # Offload to disk
            "offload_state_dict": True,  # Offload state dict to disk
            "device_map": "cpu",  # Use CPU
        }

        try:
            model = SeamlessM4Tv2ForSpeechToText.from_pretrained(
                settings.model_name, **model_kwargs
            )
        except Exception as e:
            logger.warning(f"Failed with disk offloading: {e}")
            logger.info(
                "🔄 Trying alternative approach with manual memory management..."
            )

            # Alternative: try loading without memory mapping
            model_kwargs = {
                "trust_remote_code": settings.trust_remote_code,
                "low_cpu_mem_usage": True,
                "torch_dtype": torch.float32,
                "device_map": {"": "cpu"},  # Force everything to CPU
                "load_in_8bit": False,  # Disable quantization
                "offload_folder": offload_dir,
            }

            model = SeamlessM4Tv2ForSpeechToText.from_pretrained(
                settings.model_name, **model_kwargs
            )

        logger.info("✅ Main model loaded with optimizations")

        # Don't move to device if using device_map="auto"
        if "device_map" not in model_kwargs or model_kwargs["device_map"] != "auto":
            logger.info(f"📤 Moving model to {device}...")
            model = model.to(device)  # type: ignore[assignment]

        model.eval()
        logger.info("✅ Model set to eval mode")

        # Update model state
        model_state.model = model
        model_state.processor = processor
        model_state.tokenizer = tokenizer
        model_state.device = device

        logger.info("🎉 Model loading completed successfully!")
        return model, processor, tokenizer, device

    except Exception as e:
        logger.error("💥 Error loading model: %s", str(e))
        logger.error("Error type: %s", type(e).__name__)
        logger.error("Traceback:", exc_info=True)
        raise


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

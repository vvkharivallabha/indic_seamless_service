"""
Audio processing utilities
"""

import logging
from typing import Tuple
import torchaudio
import torch

from src.config.settings import settings

logger = logging.getLogger(__name__)


def allowed_file(filename: str) -> bool:
    """
    Check if file extension is allowed.

    Args:
        filename: Name of the file to check

    Returns:
        True if file extension is allowed, False otherwise
    """
    if not filename:
        return False
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in settings.allowed_extensions
    )


def preprocess_audio(
    audio_file: str, target_sr: int = None
) -> Tuple[torch.Tensor, int]:
    """
    Preprocess audio file to the required format.

    Args:
        audio_file: Path to the audio file
        target_sr: Target sample rate (defaults to settings.target_sample_rate)

    Returns:
        Tuple of (audio_tensor, sample_rate)

    Raises:
        Exception: If audio preprocessing fails
    """
    if target_sr is None:
        target_sr = settings.target_sample_rate

    try:
        logger.info(f"Preprocessing audio file: {audio_file}")
        audio, orig_freq = torchaudio.load(audio_file)

        # Resample if necessary
        if orig_freq != target_sr:
            logger.info(f"Resampling from {orig_freq}Hz to {target_sr}Hz")
            audio = torchaudio.functional.resample(
                audio, orig_freq=orig_freq, new_freq=target_sr
            )

        logger.info(f"Audio preprocessing completed. Shape: {audio.shape}")
        return audio, target_sr

    except Exception as e:
        logger.error(f"Error preprocessing audio: {str(e)}")
        raise

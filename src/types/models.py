"""
Type definitions for model state and internal data structures
"""

from typing import Optional, Any
from dataclasses import dataclass
import torch


@dataclass
class ModelState:
    """Model state container"""

    model: Optional[Any] = None
    processor: Optional[Any] = None
    tokenizer: Optional[Any] = None
    device: Optional[torch.device] = None
    is_loaded: bool = False

    def is_ready(self) -> bool:
        """Check if all model components are loaded and ready"""
        return (
            self.model is not None
            and self.processor is not None
            and self.tokenizer is not None
            and self.device is not None
            and self.is_loaded
        )

    def reset(self) -> None:
        """Reset model state"""
        self.model = None
        self.processor = None
        self.tokenizer = None
        self.device = None
        self.is_loaded = False

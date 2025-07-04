"""Configuration module for Indic-Seamless Service"""

from .settings import Settings
from .languages import TargetLanguage, LANGUAGE_NAME_TO_CODE, SUPPORTED_LANGUAGES

__all__ = [
    "Settings",
    "TargetLanguage", 
    "LANGUAGE_NAME_TO_CODE",
    "SUPPORTED_LANGUAGES"
] 
"""
CSS Framework for KamDental Email Templates
Modular, maintainable, and email-client compatible CSS system
"""

from .base import get_base_styles
from .components import get_component_styles
from .themes import get_theme_styles, THEME_REGISTRY
from .utilities import get_utility_styles
from .email_compatibility import apply_email_compatibility_fixes

__all__ = [
    "get_base_styles",
    "get_component_styles", 
    "get_theme_styles",
    "get_utility_styles",
    "apply_email_compatibility_fixes",
    "THEME_REGISTRY",
]
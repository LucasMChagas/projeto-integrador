"""
Backend Package
Sistema de gerenciamento de precificação para marketplaces
"""

from .auth import AuthManager
from .database import DatabaseManager
from .utils import (
    apply_custom_theme,
    format_currency,
    format_percentage,
    calculate_price,
    validate_email
)

__version__ = "1.0.0"
__all__ = [
    'AuthManager',
    'DatabaseManager',
    'apply_custom_theme',
    'format_currency',
    'format_percentage',
    'calculate_price',
    'validate_email'
]
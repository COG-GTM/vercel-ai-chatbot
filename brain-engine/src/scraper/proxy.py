"""Oxylabs proxy configuration and utilities."""

from typing import Dict, Optional
from src.config import settings, COUNTRY_CONFIG


def get_proxy_config(country_code: str) -> Dict[str, str]:
    """
    Generate Oxylabs proxy configuration for a specific country.
    
    Args:
        country_code: Two-letter country code (e.g., 'in', 'mx', 'br')
        
    Returns:
        Proxy configuration dictionary for Playwright
    """
    return {
        "server": f"http://{settings.oxylabs_endpoint}",
        "username": f"{settings.oxylabs_username}-cc-{country_code}",
        "password": settings.oxylabs_password,
    }


def get_country_info(country_code: str) -> Dict[str, str]:
    """
    Get country information for display and localization.
    
    Args:
        country_code: Two-letter country code
        
    Returns:
        Country information dictionary
    """
    return COUNTRY_CONFIG.get(country_code, {
        "name": country_code.upper(),
        "currency": "USD",
        "locale": "en-US"
    })


def validate_country_code(country_code: str) -> bool:
    """
    Validate if a country code is supported.
    
    Args:
        country_code: Two-letter country code
        
    Returns:
        True if supported, False otherwise
    """
    return country_code.lower() in COUNTRY_CONFIG

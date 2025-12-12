"""Configuration management for Brain Engine."""

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_key: str
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    
    # Oxylabs Proxy Configuration
    oxylabs_username: str
    oxylabs_password: str
    oxylabs_endpoint: str = "pr.oxylabs.io:7777"
    
    # Search Configuration
    search_countries: List[str] = ["in", "mx", "br", "th", "tr"]
    max_results_per_country: int = 10
    request_timeout: int = 30000  # milliseconds
    
    # Caching (Optional)
    redis_url: Optional[str] = None
    cache_ttl: int = 900  # 15 minutes
    
    # Browser Configuration
    headless: bool = True
    browser_timeout: int = 30000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


# Country configuration with display names
COUNTRY_CONFIG = {
    "in": {"name": "India", "currency": "INR", "locale": "en-IN"},
    "mx": {"name": "Mexico", "currency": "MXN", "locale": "es-MX"},
    "br": {"name": "Brazil", "currency": "BRL", "locale": "pt-BR"},
    "th": {"name": "Thailand", "currency": "THB", "locale": "th-TH"},
    "tr": {"name": "Turkey", "currency": "TRY", "locale": "tr-TR"},
    "us": {"name": "United States", "currency": "USD", "locale": "en-US"},
}

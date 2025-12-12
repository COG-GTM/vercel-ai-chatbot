"""Playwright browser management utilities."""

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from src.config import settings
from src.scraper.proxy import get_proxy_config, get_country_info


@asynccontextmanager
async def create_browser_context(
    country_code: str,
    headless: Optional[bool] = None
):
    """
    Create a browser context configured for a specific country.
    
    Args:
        country_code: Two-letter country code for proxy routing
        headless: Override headless setting (default from config)
        
    Yields:
        Tuple of (browser, context, page)
    """
    proxy_config = get_proxy_config(country_code)
    country_info = get_country_info(country_code)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=headless if headless is not None else settings.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )
        
        context = await browser.new_context(
            proxy=proxy_config,
            viewport={"width": 1920, "height": 1080},
            locale=country_info.get("locale", "en-US"),
            timezone_id=get_timezone_for_country(country_code),
            user_agent=get_user_agent(),
        )
        
        # Add stealth scripts to avoid detection
        await context.add_init_script("""
            // Override navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
        """)
        
        page = await context.new_page()
        page.set_default_timeout(settings.browser_timeout)
        
        try:
            yield browser, context, page
        finally:
            await context.close()
            await browser.close()


def get_timezone_for_country(country_code: str) -> str:
    """Get appropriate timezone for country code."""
    timezones = {
        "in": "Asia/Kolkata",
        "mx": "America/Mexico_City",
        "br": "America/Sao_Paulo",
        "th": "Asia/Bangkok",
        "tr": "Europe/Istanbul",
        "us": "America/New_York",
    }
    return timezones.get(country_code, "America/New_York")


def get_user_agent() -> str:
    """Get a realistic user agent string."""
    return (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

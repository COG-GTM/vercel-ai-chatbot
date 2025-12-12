# Ryoko: Complete Build Instructions for Devin

> **Document Purpose**: This is a comprehensive technical specification for Devin (Cognition AI) to build Ryoko, a B2C travel platform. Devin should read this entire document, create a project plan, and execute it step by step.

---

## 🎯 Executive Summary

**What we're building**: Ryoko - a chat-first travel platform that finds cheap airline tickets using geographic price arbitrage.

**Repository**: https://github.com/COG-GTM/vercel-ai-chatbot

**Architecture**: Monorepo with Next.js frontend + Python Brain Engine

**Database**: Postgres (Neon) via Drizzle ORM (already integrated)

**Key Deliverables**:
1. Customize the Vercel AI Chatbot for travel use case
2. Create `search-flights` AI tool
3. Build Python Brain Engine in `/brain-engine` folder
4. Configure deployment for both services

---

## 📋 Project Plan Template

Devin should create and execute a plan with these phases:

```
PHASE 1: Repository Setup & Configuration (Day 1)
├── Task 1.1: Clone and analyze existing codebase
├── Task 1.2: Set up environment variables template
├── Task 1.3: Create monorepo structure with brain-engine folder
├── Task 1.4: Update .gitignore and vercel.json
└── Task 1.5: Verify local development works

PHASE 2: Brain Engine Development (Day 1-2)
├── Task 2.1: Create Python project structure
├── Task 2.2: Implement FastAPI application
├── Task 2.3: Build Playwright scraper with proxy support
├── Task 2.4: Create flight data models
├── Task 2.5: Add health check and error handling
├── Task 2.6: Create Dockerfile
└── Task 2.7: Test locally

PHASE 3: Frontend Integration (Day 2-3)
├── Task 3.1: Create search-flights.ts tool
├── Task 3.2: Register tool in chat route
├── Task 3.3: Customize system prompt for travel
├── Task 3.4: Update AI model configuration
├── Task 3.5: Add flight result display component (optional)
└── Task 3.6: Test end-to-end flow

PHASE 4: Database Schema Updates (Day 3)
├── Task 4.1: Add flight search history table
├── Task 4.2: Add price cache table
├── Task 4.3: Run migrations
└── Task 4.4: Create query functions

PHASE 5: Deployment Configuration (Day 3-4)
├── Task 5.1: Configure Vercel deployment
├── Task 5.2: Configure Railway deployment for Brain Engine
├── Task 5.3: Set up environment variables in both platforms
├── Task 5.4: Test production deployment
└── Task 5.5: Document deployment process

PHASE 6: Testing & Documentation (Day 4)
├── Task 6.1: Write integration tests
├── Task 6.2: Test proxy functionality
├── Task 6.3: Update README
└── Task 6.4: Create API documentation
```

---

## 🏗️ Architecture Overview

### Monorepo Structure

```
COG-GTM/vercel-ai-chatbot/
│
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Authentication pages
│   │   ├── login/
│   │   ├── register/
│   │   └── auth.ts
│   ├── (chat)/                   # Chat application
│   │   ├── api/
│   │   │   ├── chat/
│   │   │   │   ├── route.ts      # ⭐ MODIFY: Add searchFlights tool
│   │   │   │   └── schema.ts
│   │   │   ├── document/
│   │   │   ├── history/
│   │   │   └── vote/
│   │   └── page.tsx
│   └── layout.tsx
│
├── components/                   # React components
│   ├── chat.tsx
│   ├── message.tsx
│   ├── multimodal-input.tsx
│   ├── flight-results.tsx        # ⭐ CREATE: Flight display component
│   └── ui/
│
├── lib/
│   ├── ai/
│   │   ├── models.ts
│   │   ├── providers.ts
│   │   ├── prompts.ts            # ⭐ MODIFY: Travel expert prompt
│   │   ├── entitlements.ts
│   │   └── tools/
│   │       ├── get-weather.ts
│   │       ├── create-document.ts
│   │       └── search-flights.ts # ⭐ CREATE: Brain Engine tool
│   │
│   ├── db/
│   │   ├── schema.ts             # ⭐ MODIFY: Add flight tables
│   │   ├── queries.ts            # ⭐ MODIFY: Add flight queries
│   │   └── migrations/
│   │
│   └── utils.ts
│
├── brain-engine/                 # ⭐ CREATE: Entire folder
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI application
│   │   ├── config.py             # Configuration management
│   │   ├── scraper/
│   │   │   ├── __init__.py
│   │   │   ├── browser.py        # Playwright browser setup
│   │   │   ├── proxy.py          # Oxylabs proxy configuration
│   │   │   └── flights.py        # Flight scraping logic
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── flight.py         # Pydantic models
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── cache.py          # Future caching utilities
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_main.py
│   │   └── test_scraper.py
│   │
│   ├── .env.example
│   ├── .python-version           # 3.11
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml        # Local development
│   └── README.md
│
├── .env.example                  # ⭐ MODIFY: Add Brain Engine vars
├── .gitignore                    # ⭐ MODIFY: Add Python ignores
├── vercel.json                   # ⭐ MODIFY: Exclude brain-engine
├── package.json
├── drizzle.config.ts
└── README.md                     # ⭐ MODIFY: Update documentation
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERACTION                               │
│                                                                         │
│  User: "Find me cheap flights from LAX to Tokyo in March"               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    NEXT.JS FRONTEND (Vercel)                            │
│                                                                         │
│  1. components/chat.tsx                                                 │
│     └── useChat() hook captures user message                            │
│                                                                         │
│  2. app/(chat)/api/chat/route.ts                                        │
│     └── streamText() with tools: { searchFlights }                      │
│                                                                         │
│  3. lib/ai/tools/search-flights.ts                                      │
│     └── AI decides to call searchFlights tool                           │
│     └── Makes HTTP request to Brain Engine                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ POST /api/search
                                    │ Authorization: Bearer <API_KEY>
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    BRAIN ENGINE (Railway/Render)                        │
│                                                                         │
│  brain-engine/src/main.py                                               │
│  ├── Validates request                                                  │
│  ├── Calls scraper/flights.py                                           │
│  │   ├── Spins up Playwright browsers (concurrent)                      │
│  │   ├── Each browser routes through Oxylabs proxy                      │
│  │   │   ├── India IP (country code: in)                                │
│  │   │   ├── Mexico IP (country code: mx)                               │
│  │   │   ├── Brazil IP (country code: br)                               │
│  │   │   ├── Thailand IP (country code: th)                             │
│  │   │   └── Turkey IP (country code: tr)                               │
│  │   ├── Scrapes Google Flights from each location                      │
│  │   └── Extracts prices, airlines, times                               │
│  ├── Aggregates results                                                 │
│  ├── Calculates savings                                                 │
│  └── Returns JSON response                                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ JSON Response
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         AI RESPONSE                                     │
│                                                                         │
│  "I found great deals for LAX → Tokyo in March!                         │
│                                                                         │
│   🏆 Best Deal: ANA via India pricing                                   │
│      $487 round-trip (Save 38%!)                                        │
│                                                                         │
│   Other options:                                                        │
│   • JAL - $512 (Save 34%)                                               │
│   • United - $534 (Save 31%)"                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 File-by-File Implementation

### PHASE 1: Repository Setup

#### Task 1.1: Analyze Existing Codebase

First, Devin should explore the repository structure:

```bash
git clone https://github.com/COG-GTM/vercel-ai-chatbot.git
cd vercel-ai-chatbot
```

Key files to understand:
- `app/(chat)/api/chat/route.ts` - Main chat API endpoint
- `lib/ai/tools/` - Existing tool implementations
- `lib/ai/prompts.ts` - System prompts
- `lib/db/schema.ts` - Database schema

#### Task 1.2: Update .gitignore

Add Python-specific ignores:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
brain-engine/venv/
brain-engine/.venv/
brain-engine/env/

# Environment files
brain-engine/.env

# IDE
.idea/
*.swp
*.swo

# Playwright
brain-engine/playwright-browsers/
```

#### Task 1.3: Update vercel.json

Create or update `vercel.json` to exclude Brain Engine:

```json
{
  "git": {
    "deploymentEnabled": {
      "brain-engine/**": false
    }
  },
  "ignoreCommand": "git diff --quiet HEAD^ HEAD -- . ':!brain-engine'",
  "buildCommand": "pnpm build",
  "installCommand": "pnpm install",
  "framework": "nextjs"
}
```

#### Task 1.4: Update .env.example

Add Brain Engine configuration:

```env
# ===========================================
# EXISTING CONFIGURATION
# ===========================================

# Authentication (Required)
AUTH_SECRET=

# Database - Neon Postgres (Required)
POSTGRES_URL=

# AI Provider - Choose one or more
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# File Storage (Required)
BLOB_READ_WRITE_TOKEN=

# ===========================================
# BRAIN ENGINE CONFIGURATION (New)
# ===========================================

# Brain Engine API Connection
BRAIN_ENGINE_URL=http://localhost:8000
BRAIN_ENGINE_API_KEY=your-secret-api-key

# ===========================================
# FOR BRAIN ENGINE SERVICE (brain-engine/.env)
# ===========================================
# API_KEY=your-secret-api-key
# OXYLABS_USERNAME=your-oxylabs-username
# OXYLABS_PASSWORD=your-oxylabs-password
# REDIS_URL=redis://localhost:6379 (optional)
```

---

### PHASE 2: Brain Engine Development

#### Task 2.1: Create Directory Structure

```bash
mkdir -p brain-engine/src/scraper
mkdir -p brain-engine/src/models
mkdir -p brain-engine/src/utils
mkdir -p brain-engine/tests
touch brain-engine/src/__init__.py
touch brain-engine/src/scraper/__init__.py
touch brain-engine/src/models/__init__.py
touch brain-engine/src/utils/__init__.py
touch brain-engine/tests/__init__.py
```

#### Task 2.2: Create requirements.txt

File: `brain-engine/requirements.txt`

```text
# Web Framework
fastapi==0.109.2
uvicorn[standard]==0.27.1
python-multipart==0.0.9

# Browser Automation
playwright==1.41.2

# Data Validation
pydantic==2.6.1
pydantic-settings==2.1.0

# HTTP Client
httpx==0.26.0

# Environment Management
python-dotenv==1.0.1

# Async Support
asyncio==3.4.3

# Caching (Future)
redis==5.0.1

# Testing
pytest==8.0.0
pytest-asyncio==0.23.4

# Code Quality
black==24.1.1
ruff==0.2.1
```

#### Task 2.3: Create config.py

File: `brain-engine/src/config.py`

```python
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
```

#### Task 2.4: Create flight.py (Models)

File: `brain-engine/src/models/flight.py`

```python
"""Pydantic models for flight data."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class CabinClass(str, Enum):
    """Cabin class options."""
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"


class FlightSearchRequest(BaseModel):
    """Request model for flight search."""
    
    origin: str = Field(
        ...,
        description="Origin airport IATA code",
        min_length=3,
        max_length=3,
        examples=["LAX", "JFK", "SFO"]
    )
    destination: str = Field(
        ...,
        description="Destination airport IATA code",
        min_length=3,
        max_length=3,
        examples=["NRT", "LHR", "CDG"]
    )
    departure_date: str = Field(
        ...,
        alias="departureDate",
        description="Departure date in YYYY-MM-DD format",
        examples=["2025-03-15"]
    )
    return_date: Optional[str] = Field(
        None,
        alias="returnDate",
        description="Return date in YYYY-MM-DD format (optional for one-way)",
        examples=["2025-03-22"]
    )
    passengers: int = Field(
        default=1,
        ge=1,
        le=9,
        description="Number of passengers"
    )
    cabin_class: CabinClass = Field(
        default=CabinClass.ECONOMY,
        alias="cabinClass",
        description="Cabin class preference"
    )
    
    class Config:
        populate_by_name = True


class FlightSegment(BaseModel):
    """Individual flight segment."""
    
    airline: str
    airline_code: Optional[str] = None
    flight_number: Optional[str] = None
    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str
    duration: str
    aircraft: Optional[str] = None


class Flight(BaseModel):
    """Flight option with pricing."""
    
    id: str = Field(description="Unique identifier for this flight option")
    airline: str
    airline_logo: Optional[str] = None
    price: float
    currency: str = "USD"
    original_price: Optional[float] = Field(
        None,
        description="Price from baseline country (US) for comparison"
    )
    savings_percent: Optional[float] = Field(
        None,
        description="Percentage savings compared to baseline"
    )
    savings_amount: Optional[float] = Field(
        None,
        description="Dollar amount saved compared to baseline"
    )
    departure_time: str
    arrival_time: str
    duration: str
    stops: int
    stop_cities: Optional[List[str]] = None
    segments: Optional[List[FlightSegment]] = None
    searched_from_country: str = Field(
        description="Country the search was performed from"
    )
    booking_url: Optional[str] = None
    

class FlightSearchResponse(BaseModel):
    """Response model for flight search."""
    
    success: bool = True
    flights: List[Flight]
    total_results: int
    countries_searched: List[str]
    best_price: Optional[float] = None
    baseline_price: Optional[float] = Field(
        None,
        description="Price from US for comparison"
    )
    best_savings_percent: Optional[float] = None
    search_time_seconds: float
    cached: bool = False
    cache_expires_at: Optional[datetime] = None
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "flights": [
                    {
                        "id": "flight_001",
                        "airline": "ANA",
                        "price": 487.00,
                        "currency": "USD",
                        "original_price": 789.00,
                        "savings_percent": 38.3,
                        "savings_amount": 302.00,
                        "departure_time": "10:30 AM",
                        "arrival_time": "3:45 PM +1",
                        "duration": "11h 15m",
                        "stops": 0,
                        "searched_from_country": "India"
                    }
                ],
                "total_results": 15,
                "countries_searched": ["India", "Mexico", "Brazil"],
                "best_price": 487.00,
                "baseline_price": 789.00,
                "best_savings_percent": 38.3,
                "search_time_seconds": 12.5,
                "cached": False
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = "healthy"
    service: str = "brain-engine"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

#### Task 2.5: Create proxy.py

File: `brain-engine/src/scraper/proxy.py`

```python
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
```

#### Task 2.6: Create browser.py

File: `brain-engine/src/scraper/browser.py`

```python
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
```

#### Task 2.7: Create flights.py (Scraper)

File: `brain-engine/src/scraper/flights.py`

```python
"""Flight scraping logic for Google Flights."""

import asyncio
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime

from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

from src.config import settings, COUNTRY_CONFIG
from src.scraper.browser import create_browser_context
from src.scraper.proxy import get_country_info
from src.models.flight import Flight, FlightSearchRequest, CabinClass


def build_google_flights_url(request: FlightSearchRequest) -> str:
    """
    Build Google Flights search URL.
    
    Args:
        request: Flight search request parameters
        
    Returns:
        Google Flights URL string
    """
    base_url = "https://www.google.com/travel/flights"
    
    # Build the search parameters
    # Format: /flights/LAX/NRT/2025-03-15/2025-03-22
    origin = request.origin.upper()
    destination = request.destination.upper()
    
    path = f"/search?tfs=CBwQAhopEgoyMDI1LTAzLTE1agwIAhIIL20vMGRsdjByDAgCEggvbS8wN2RmaygBGikSCjIwMjUtMDMtMjJqDAgCEggvbS8wN2RmaxoMCAISCC9tLzBkbHZyKAFAAUgBcAGCAQsI____________AZgBAQ"
    
    # Simpler URL format that works
    url = f"{base_url}?hl=en&gl=us&curr=USD"
    url += f"&q=flights%20from%20{origin}%20to%20{destination}"
    url += f"%20on%20{request.departure_date}"
    if request.return_date:
        url += f"%20returning%20{request.return_date}"
    
    return url


async def extract_flights_from_page(
    page: Page,
    country_code: str,
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Extract flight data from Google Flights results page.
    
    Args:
        page: Playwright page object
        country_code: Country the search was performed from
        max_results: Maximum number of results to extract
        
    Returns:
        List of flight dictionaries
    """
    flights = []
    country_info = get_country_info(country_code)
    
    try:
        # Wait for results to load
        await page.wait_for_selector(
            'div[data-ved]',
            timeout=15000
        )
        
        # Get all flight result containers
        # Note: Google Flights selectors change frequently
        # These are common patterns but may need adjustment
        result_selectors = [
            '[class*="pIav2d"]',  # Main result container
            '[class*="yR1fYc"]',  # Alternative selector
            'li[data-ved]',       # List item fallback
        ]
        
        results = []
        for selector in result_selectors:
            results = await page.query_selector_all(selector)
            if results:
                break
        
        for i, result in enumerate(results[:max_results]):
            try:
                flight_data = await extract_single_flight(result, country_info["name"], i)
                if flight_data:
                    flights.append(flight_data)
            except Exception as e:
                print(f"Error extracting flight {i} from {country_info['name']}: {e}")
                continue
                
    except PlaywrightTimeout:
        print(f"Timeout waiting for results from {country_info['name']}")
    except Exception as e:
        print(f"Error extracting flights from {country_info['name']}: {e}")
    
    return flights


async def extract_single_flight(
    element,
    country_name: str,
    index: int
) -> Optional[Dict[str, Any]]:
    """
    Extract data from a single flight result element.
    
    Args:
        element: Playwright element handle
        country_name: Name of country searched from
        index: Result index for ID generation
        
    Returns:
        Flight dictionary or None if extraction fails
    """
    try:
        # Extract price
        price_element = await element.query_selector('[class*="price"], [class*="YMlIz"]')
        if not price_element:
            return None
            
        price_text = await price_element.inner_text()
        price = parse_price(price_text)
        if not price:
            return None
        
        # Extract airline
        airline_element = await element.query_selector(
            '[class*="airline"], [class*="sSHqwe"], [class*="Ir0Voe"]'
        )
        airline = await airline_element.inner_text() if airline_element else "Unknown Airline"
        
        # Extract times
        time_elements = await element.query_selector_all('[class*="mv1WYe"], [class*="zxVSec"]')
        departure_time = ""
        arrival_time = ""
        if len(time_elements) >= 2:
            departure_time = await time_elements[0].inner_text()
            arrival_time = await time_elements[1].inner_text()
        
        # Extract duration
        duration_element = await element.query_selector('[class*="Ak5kof"], [class*="gvkrdb"]')
        duration = await duration_element.inner_text() if duration_element else ""
        
        # Extract stops
        stops_element = await element.query_selector('[class*="EfT7Ae"], [class*="BbR8Ec"]')
        stops_text = await stops_element.inner_text() if stops_element else "Nonstop"
        stops = parse_stops(stops_text)
        
        # Generate unique ID
        flight_id = generate_flight_id(
            airline, departure_time, arrival_time, price, country_name
        )
        
        return {
            "id": flight_id,
            "airline": airline.strip(),
            "price": price,
            "currency": "USD",
            "departure_time": departure_time.strip(),
            "arrival_time": arrival_time.strip(),
            "duration": duration.strip(),
            "stops": stops,
            "searched_from_country": country_name,
        }
        
    except Exception as e:
        print(f"Error parsing flight element: {e}")
        return None


def parse_price(price_text: str) -> Optional[float]:
    """Parse price string to float."""
    try:
        # Remove currency symbols and commas
        cleaned = price_text.replace("$", "").replace(",", "").replace("USD", "").strip()
        return float(cleaned)
    except (ValueError, AttributeError):
        return None


def parse_stops(stops_text: str) -> int:
    """Parse stops text to integer."""
    lower_text = stops_text.lower()
    if "nonstop" in lower_text or "direct" in lower_text:
        return 0
    try:
        # Extract number from text like "1 stop" or "2 stops"
        return int(''.join(filter(str.isdigit, stops_text)) or 0)
    except ValueError:
        return 0


def generate_flight_id(
    airline: str,
    departure: str,
    arrival: str,
    price: float,
    country: str
) -> str:
    """Generate unique flight ID."""
    data = f"{airline}{departure}{arrival}{price}{country}"
    return hashlib.md5(data.encode()).hexdigest()[:12]


async def search_flights_from_country(
    request: FlightSearchRequest,
    country_code: str
) -> List[Dict[str, Any]]:
    """
    Search for flights appearing to browse from a specific country.
    
    Args:
        request: Flight search parameters
        country_code: Country to search from
        
    Returns:
        List of flight results
    """
    country_info = get_country_info(country_code)
    print(f"Searching from {country_info['name']}...")
    
    try:
        async with create_browser_context(country_code) as (browser, context, page):
            url = build_google_flights_url(request)
            
            await page.goto(url, wait_until="networkidle", timeout=settings.request_timeout)
            
            # Handle cookie consent if present
            try:
                consent_button = await page.query_selector(
                    'button[aria-label*="Accept"], button:has-text("Accept all")'
                )
                if consent_button:
                    await consent_button.click()
                    await page.wait_for_timeout(1000)
            except:
                pass
            
            flights = await extract_flights_from_page(
                page,
                country_code,
                settings.max_results_per_country
            )
            
            print(f"Found {len(flights)} flights from {country_info['name']}")
            return flights
            
    except Exception as e:
        print(f"Error searching from {country_info['name']}: {e}")
        return []


async def search_flights_multi_country(
    request: FlightSearchRequest
) -> Dict[str, Any]:
    """
    Search for flights from multiple countries concurrently.
    
    Args:
        request: Flight search parameters
        
    Returns:
        Aggregated results from all countries
    """
    start_time = datetime.utcnow()
    
    # Create search tasks for each country
    tasks = [
        search_flights_from_country(request, country_code)
        for country_code in settings.search_countries
    ]
    
    # Also search from US as baseline for comparison
    tasks.append(search_flights_from_country(request, "us"))
    
    # Execute all searches concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    all_flights = []
    countries_searched = []
    us_baseline_price = None
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Search task {i} failed: {result}")
            continue
            
        if isinstance(result, list) and result:
            country_code = (
                settings.search_countries[i]
                if i < len(settings.search_countries)
                else "us"
            )
            country_info = get_country_info(country_code)
            countries_searched.append(country_info["name"])
            
            # Track US baseline
            if country_code == "us" and result:
                us_baseline_price = min(f["price"] for f in result)
            else:
                all_flights.extend(result)
    
    # Sort by price
    all_flights.sort(key=lambda x: x["price"])
    
    # Calculate savings compared to US baseline
    if us_baseline_price and all_flights:
        for flight in all_flights:
            flight["original_price"] = us_baseline_price
            savings = us_baseline_price - flight["price"]
            flight["savings_amount"] = round(savings, 2)
            flight["savings_percent"] = round(
                (savings / us_baseline_price) * 100, 1
            )
    
    # Calculate summary stats
    best_price = all_flights[0]["price"] if all_flights else None
    best_savings = all_flights[0].get("savings_percent") if all_flights else None
    
    search_time = (datetime.utcnow() - start_time).total_seconds()
    
    return {
        "flights": all_flights,
        "total_results": len(all_flights),
        "countries_searched": countries_searched,
        "best_price": best_price,
        "baseline_price": us_baseline_price,
        "best_savings_percent": best_savings,
        "search_time_seconds": round(search_time, 2),
    }
```

#### Task 2.8: Create main.py

File: `brain-engine/src/main.py`

```python
"""
Brain Engine API - Flight price aggregation service.

This service scrapes flight prices from multiple geographic locations
to find the best deals through price arbitrage.
"""

from fastapi import FastAPI, HTTPException, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Optional
import logging

from src.config import settings
from src.models.flight import (
    FlightSearchRequest,
    FlightSearchResponse,
    HealthResponse,
    Flight,
)
from src.scraper.flights import search_flights_multi_country

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Ryoko Brain Engine",
    description="Flight price aggregation API using geographic arbitrage",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://ryoko.travel",  # Production domain
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


async def verify_api_key(
    authorization: Optional[str] = Header(None)
) -> str:
    """
    Verify API key from Authorization header.
    
    Args:
        authorization: Authorization header value
        
    Returns:
        Validated API key
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format. Use: Bearer <token>"
        )
    
    token = authorization.replace("Bearer ", "")
    
    if token != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return token


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - returns service info."""
    return HealthResponse()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring."""
    return HealthResponse()


@app.post("/api/search", response_model=FlightSearchResponse)
async def search_flights(
    request: FlightSearchRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Search for flights across multiple countries.
    
    This endpoint searches for flight prices from multiple geographic
    locations to find the best deals through price arbitrage.
    
    Args:
        request: Flight search parameters
        api_key: Validated API key (injected by dependency)
        
    Returns:
        FlightSearchResponse with aggregated results
    """
    logger.info(
        f"Flight search: {request.origin} -> {request.destination} "
        f"on {request.departure_date}"
    )
    
    try:
        # Execute multi-country search
        results = await search_flights_multi_country(request)
        
        # Convert to response model
        flights = [Flight(**f) for f in results["flights"]]
        
        response = FlightSearchResponse(
            success=True,
            flights=flights,
            total_results=results["total_results"],
            countries_searched=results["countries_searched"],
            best_price=results["best_price"],
            baseline_price=results["baseline_price"],
            best_savings_percent=results["best_savings_percent"],
            search_time_seconds=results["search_time_seconds"],
            cached=False,
        )
        
        logger.info(
            f"Search complete: {len(flights)} flights found, "
            f"best savings: {results.get('best_savings_percent', 0)}%"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else None
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )
```

#### Task 2.9: Create Dockerfile

File: `brain-engine/Dockerfile`

```dockerfile
# Stage 1: Base image with Python
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Dependencies
FROM base as dependencies

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Stage 3: Application
FROM dependencies as application

# Copy application code
COPY src/ ./src/

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Task 2.10: Create docker-compose.yml

File: `brain-engine/docker-compose.yml`

```yaml
version: '3.8'

services:
  brain-engine:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - API_KEY=${API_KEY}
      - OXYLABS_USERNAME=${OXYLABS_USERNAME}
      - OXYLABS_PASSWORD=${OXYLABS_PASSWORD}
      - DEBUG=true
    env_file:
      - .env
    volumes:
      - ./src:/app/src:ro  # Mount source for development
    restart: unless-stopped

  # Optional: Redis for caching (future)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

#### Task 2.11: Create .env.example

File: `brain-engine/.env.example`

```env
# ===========================================
# Brain Engine Configuration
# ===========================================

# API Security
API_KEY=your-secure-api-key-here

# Oxylabs Residential Proxy Credentials
# Get these from: https://dashboard.oxylabs.io
OXYLABS_USERNAME=your-oxylabs-username
OXYLABS_PASSWORD=your-oxylabs-password

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Browser Configuration
HEADLESS=true
BROWSER_TIMEOUT=30000
REQUEST_TIMEOUT=30000

# Search Configuration
# Comma-separated country codes
SEARCH_COUNTRIES=in,mx,br,th,tr
MAX_RESULTS_PER_COUNTRY=10

# Caching (Optional)
REDIS_URL=redis://localhost:6379
CACHE_TTL=900
```

#### Task 2.12: Create README.md

File: `brain-engine/README.md`

```markdown
# Ryoko Brain Engine

Flight price aggregation service using geographic price arbitrage.

## Overview

The Brain Engine searches for flight prices from multiple countries simultaneously,
leveraging the fact that airlines often show different prices based on user location.

## Architecture

```
Request → FastAPI → Playwright Browsers (concurrent)
                         ↓
            ┌────────────┼────────────┐
            ↓            ↓            ↓
        India IP    Mexico IP    Brazil IP
            ↓            ↓            ↓
        Oxylabs    Oxylabs     Oxylabs
            ↓            ↓            ↓
        Google     Google      Google
        Flights    Flights     Flights
            ↓            ↓            ↓
            └────────────┼────────────┘
                         ↓
              Aggregate & Compare
                         ↓
                JSON Response
```

## Quick Start

### Local Development

1. Copy environment file:
   ```bash
   cp .env.example .env
   ```

2. Fill in your credentials in `.env`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. Run the server:
   ```bash
   python -m src.main
   ```

### Docker

```bash
docker-compose up --build
```

## API Endpoints

### Health Check
```
GET /health
```

### Search Flights
```
POST /api/search
Authorization: Bearer <API_KEY>
Content-Type: application/json

{
  "origin": "LAX",
  "destination": "NRT",
  "departureDate": "2025-03-15",
  "returnDate": "2025-03-22",
  "passengers": 1,
  "cabinClass": "economy"
}
```

## Testing

```bash
# Health check
curl http://localhost:8000/health

# Search flights
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "origin": "LAX",
    "destination": "NRT",
    "departureDate": "2025-03-15"
  }'
```

## Deployment

### Railway

1. Connect GitHub repository
2. Set root directory to `/brain-engine`
3. Add environment variables
4. Deploy

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| API_KEY | Yes | API authentication key |
| OXYLABS_USERNAME | Yes | Oxylabs proxy username |
| OXYLABS_PASSWORD | Yes | Oxylabs proxy password |
| DEBUG | No | Enable debug mode (default: false) |
```

---

### PHASE 3: Frontend Integration

#### Task 3.1: Create search-flights.ts

File: `lib/ai/tools/search-flights.ts`

```typescript
/**
 * Search Flights Tool
 * 
 * This tool enables the AI to search for cheap flights using
 * the Brain Engine's geographic price arbitrage capabilities.
 */

import { tool } from 'ai';
import { z } from 'zod';

// Response type from Brain Engine
interface FlightResult {
  id: string;
  airline: string;
  price: number;
  currency: string;
  original_price?: number;
  savings_percent?: number;
  savings_amount?: number;
  departure_time: string;
  arrival_time: string;
  duration: string;
  stops: number;
  searched_from_country: string;
}

interface BrainEngineResponse {
  success: boolean;
  flights: FlightResult[];
  total_results: number;
  countries_searched: string[];
  best_price?: number;
  baseline_price?: number;
  best_savings_percent?: number;
  search_time_seconds: number;
  error?: string;
}

export const searchFlights = tool({
  description: `Search for cheap flights using geographic price arbitrage. 
    Use this tool when the user wants to:
    - Find flights or airfare
    - Book travel or trips
    - Compare flight prices
    - Find the cheapest way to fly somewhere
    
    The tool searches from multiple countries (India, Mexico, Brazil, Thailand, Turkey)
    to find prices that are often 10-40% cheaper than standard US/EU prices.
    
    Always ask for origin, destination, and dates if not provided.`,

  parameters: z.object({
    origin: z
      .string()
      .length(3)
      .describe('Origin airport IATA code (e.g., LAX, JFK, SFO, ORD)'),
    destination: z
      .string()
      .length(3)
      .describe('Destination airport IATA code (e.g., NRT, LHR, CDG, FCO)'),
    departureDate: z
      .string()
      .regex(/^\d{4}-\d{2}-\d{2}$/)
      .describe('Departure date in YYYY-MM-DD format'),
    returnDate: z
      .string()
      .regex(/^\d{4}-\d{2}-\d{2}$/)
      .optional()
      .describe('Return date in YYYY-MM-DD format (optional for one-way trips)'),
    passengers: z
      .number()
      .int()
      .min(1)
      .max(9)
      .default(1)
      .describe('Number of passengers (1-9)'),
    cabinClass: z
      .enum(['economy', 'premium_economy', 'business', 'first'])
      .default('economy')
      .describe('Preferred cabin class'),
  }),

  execute: async ({
    origin,
    destination,
    departureDate,
    returnDate,
    passengers,
    cabinClass,
  }) => {
    const brainEngineUrl = process.env.BRAIN_ENGINE_URL;
    const apiKey = process.env.BRAIN_ENGINE_API_KEY;

    // Validate configuration
    if (!brainEngineUrl) {
      return {
        success: false,
        error: 'Brain Engine URL not configured. Please set BRAIN_ENGINE_URL.',
        flights: [],
        countries_searched: [],
      };
    }

    if (!apiKey) {
      return {
        success: false,
        error: 'Brain Engine API key not configured. Please set BRAIN_ENGINE_API_KEY.',
        flights: [],
        countries_searched: [],
      };
    }

    try {
      console.log(`[searchFlights] Searching: ${origin} → ${destination} on ${departureDate}`);

      const response = await fetch(`${brainEngineUrl}/api/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
          origin: origin.toUpperCase(),
          destination: destination.toUpperCase(),
          departureDate,
          returnDate,
          passengers,
          cabinClass,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`[searchFlights] API error: ${response.status} - ${errorText}`);
        
        return {
          success: false,
          error: `Search failed with status ${response.status}. Please try again.`,
          flights: [],
          countries_searched: [],
        };
      }

      const data: BrainEngineResponse = await response.json();

      console.log(
        `[searchFlights] Found ${data.total_results} flights, ` +
        `best savings: ${data.best_savings_percent}%`
      );

      // Format results for AI consumption
      return {
        success: true,
        flights: data.flights.map((flight) => ({
          id: flight.id,
          airline: flight.airline,
          price: `$${flight.price.toFixed(2)}`,
          priceNumeric: flight.price,
          savings: flight.savings_percent
            ? `${flight.savings_percent}% off (save $${flight.savings_amount?.toFixed(2)})`
            : null,
          savingsPercent: flight.savings_percent,
          departureTime: flight.departure_time,
          arrivalTime: flight.arrival_time,
          duration: flight.duration,
          stops: flight.stops === 0 ? 'Nonstop' : `${flight.stops} stop${flight.stops > 1 ? 's' : ''}`,
          foundIn: flight.searched_from_country,
        })),
        summary: {
          totalResults: data.total_results,
          countriesSearched: data.countries_searched,
          bestPrice: data.best_price ? `$${data.best_price.toFixed(2)}` : null,
          baselinePrice: data.baseline_price ? `$${data.baseline_price.toFixed(2)}` : null,
          bestSavings: data.best_savings_percent ? `${data.best_savings_percent}%` : null,
          searchTime: `${data.search_time_seconds.toFixed(1)} seconds`,
        },
        route: {
          origin: origin.toUpperCase(),
          destination: destination.toUpperCase(),
          departureDate,
          returnDate: returnDate || 'One-way',
          passengers,
          cabinClass,
        },
      };
    } catch (error) {
      console.error('[searchFlights] Error:', error);

      return {
        success: false,
        error: error instanceof Error 
          ? `Search failed: ${error.message}` 
          : 'An unexpected error occurred while searching for flights.',
        flights: [],
        countries_searched: [],
      };
    }
  },
});
```

#### Task 3.2: Update chat route.ts

Find the file `app/(chat)/api/chat/route.ts` and make these changes:

**Step 1: Add import at the top of the file:**

```typescript
// Add with other tool imports
import { searchFlights } from '@/lib/ai/tools/search-flights';
```

**Step 2: Find the `streamText` call and add the tool:**

Look for code similar to:

```typescript
const result = streamText({
  model: myProvider.languageModel(selectedChatModel),
  system: systemPrompt({ selectedChatModel }),
  messages: convertedMessages,
  tools: {
    getWeather,
    createDocument,
    updateDocument,
    requestSuggestions,
  },
  // ...
});
```

Add `searchFlights` to the tools object:

```typescript
const result = streamText({
  model: myProvider.languageModel(selectedChatModel),
  system: systemPrompt({ selectedChatModel }),
  messages: convertedMessages,
  tools: {
    getWeather,
    createDocument,
    updateDocument,
    requestSuggestions,
    searchFlights,  // ← ADD THIS LINE
  },
  // ...
});
```

#### Task 3.3: Update prompts.ts

Replace or update the system prompt in `lib/ai/prompts.ts`:

```typescript
export const systemPrompt = ({
  selectedChatModel,
}: {
  selectedChatModel: string;
}) => {
  const basePrompt = `You are Ryoko, an AI-powered travel assistant specializing in finding the cheapest flights through geographic price arbitrage.

## Your Capabilities

You have access to a powerful flight search tool that:
- Searches from multiple countries simultaneously (India, Mexico, Brazil, Thailand, Turkey)
- Finds prices that are often 10-40% cheaper than what users would normally see
- Compares prices against US baseline to show real savings

## How to Help Users

1. **When users ask about flights:**
   - Use the searchFlights tool immediately
   - Ask for missing information (origin, destination, dates) if not provided
   - Present results clearly with savings highlighted

2. **Presenting Results:**
   - Lead with the best deal and the savings percentage
   - Show top 3-5 options with clear pricing
   - Explain which country the best price was found from
   - Be enthusiastic about good deals!

3. **If a search fails:**
   - Apologize briefly
   - Suggest trying again or with different dates
   - Don't make up prices or results

## Important Guidelines

- Always use real airport codes (LAX, JFK, NRT, LHR, etc.)
- Dates should be in YYYY-MM-DD format
- Be helpful and conversational, not robotic
- If users seem unsure about destinations, offer suggestions
- Mention that prices can change quickly and to book soon for good deals

## Personality

You're excited about helping people save money on travel. You're knowledgeable about airports, airlines, and travel tips. You make the booking process feel less stressful and more exciting.

Today's date: ${new Date().toISOString().split('T')[0]}`;

  // Add model-specific instructions if needed
  if (selectedChatModel.includes('reasoning')) {
    return `${basePrompt}

## Reasoning Mode
When in reasoning mode, think through:
1. Best time to book for this route
2. Alternative airports that might be cheaper
3. Whether connecting flights might offer better value`;
  }

  return basePrompt;
};

// Keep other prompts for artifacts, etc.
export const artifactsPrompt = `...`; // Keep existing
export const codePrompt = `...`; // Keep existing
export const sheetPrompt = `...`; // Keep existing
```

---

### PHASE 4: Database Schema Updates

#### Task 4.1: Update schema.ts

Add to `lib/db/schema.ts`:

```typescript
// Add these new tables after existing tables

export const flightSearches = pgTable('flight_searches', {
  id: uuid('id').primaryKey().notNull().defaultRandom(),
  chatId: uuid('chat_id')
    .notNull()
    .references(() => chats.id, { onDelete: 'cascade' }),
  userId: uuid('user_id')
    .notNull()
    .references(() => users.id, { onDelete: 'cascade' }),
  origin: varchar('origin', { length: 3 }).notNull(),
  destination: varchar('destination', { length: 3 }).notNull(),
  departureDate: date('departure_date').notNull(),
  returnDate: date('return_date'),
  passengers: integer('passengers').notNull().default(1),
  cabinClass: varchar('cabin_class', { length: 20 }).default('economy'),
  bestPrice: real('best_price'),
  baselinePrice: real('baseline_price'),
  savingsPercent: real('savings_percent'),
  resultsCount: integer('results_count'),
  searchTimeSeconds: real('search_time_seconds'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
});

export const flightPriceCache = pgTable('flight_price_cache', {
  id: uuid('id').primaryKey().notNull().defaultRandom(),
  origin: varchar('origin', { length: 3 }).notNull(),
  destination: varchar('destination', { length: 3 }).notNull(),
  departureDate: date('departure_date').notNull(),
  returnDate: date('return_date'),
  cabinClass: varchar('cabin_class', { length: 20 }).default('economy'),
  resultsJson: json('results_json').notNull(),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  expiresAt: timestamp('expires_at').notNull(),
});

// Add indexes for common queries
export const flightSearchesUserIdIdx = index('flight_searches_user_id_idx').on(
  flightSearches.userId
);

export const flightPriceCacheRouteIdx = index('flight_price_cache_route_idx').on(
  flightPriceCache.origin,
  flightPriceCache.destination,
  flightPriceCache.departureDate
);
```

#### Task 4.2: Add query functions

Add to `lib/db/queries.ts`:

```typescript
// Flight search logging
export async function logFlightSearch({
  chatId,
  userId,
  origin,
  destination,
  departureDate,
  returnDate,
  passengers,
  cabinClass,
  bestPrice,
  baselinePrice,
  savingsPercent,
  resultsCount,
  searchTimeSeconds,
}: {
  chatId: string;
  userId: string;
  origin: string;
  destination: string;
  departureDate: string;
  returnDate?: string;
  passengers: number;
  cabinClass: string;
  bestPrice?: number;
  baselinePrice?: number;
  savingsPercent?: number;
  resultsCount?: number;
  searchTimeSeconds?: number;
}) {
  return await db.insert(flightSearches).values({
    chatId,
    userId,
    origin,
    destination,
    departureDate,
    returnDate,
    passengers,
    cabinClass,
    bestPrice,
    baselinePrice,
    savingsPercent,
    resultsCount,
    searchTimeSeconds,
  });
}

export async function getUserFlightSearches(userId: string, limit = 10) {
  return await db
    .select()
    .from(flightSearches)
    .where(eq(flightSearches.userId, userId))
    .orderBy(desc(flightSearches.createdAt))
    .limit(limit);
}

// Price caching (future use)
export async function getCachedFlightPrices(
  origin: string,
  destination: string,
  departureDate: string
) {
  const now = new Date();
  return await db
    .select()
    .from(flightPriceCache)
    .where(
      and(
        eq(flightPriceCache.origin, origin),
        eq(flightPriceCache.destination, destination),
        eq(flightPriceCache.departureDate, departureDate),
        gt(flightPriceCache.expiresAt, now)
      )
    )
    .limit(1);
}

export async function setCachedFlightPrices({
  origin,
  destination,
  departureDate,
  returnDate,
  cabinClass,
  resultsJson,
  ttlMinutes = 15,
}: {
  origin: string;
  destination: string;
  departureDate: string;
  returnDate?: string;
  cabinClass: string;
  resultsJson: any;
  ttlMinutes?: number;
}) {
  const expiresAt = new Date(Date.now() + ttlMinutes * 60 * 1000);
  
  return await db.insert(flightPriceCache).values({
    origin,
    destination,
    departureDate,
    returnDate,
    cabinClass,
    resultsJson,
    expiresAt,
  });
}
```

#### Task 4.3: Run migrations

```bash
pnpm db:generate
pnpm db:migrate
```

---

### PHASE 5: Deployment Configuration

#### Task 5.1: Vercel Deployment

The frontend deploys automatically when pushing to GitHub if connected to Vercel.

**Environment Variables to set in Vercel Dashboard:**

```
AUTH_SECRET=<generate with: openssl rand -base64 32>
POSTGRES_URL=<from Neon dashboard>
OPENAI_API_KEY=<your key>
BLOB_READ_WRITE_TOKEN=<from Vercel dashboard>
BRAIN_ENGINE_URL=<Railway URL after deploying>
BRAIN_ENGINE_API_KEY=<same key as Brain Engine>
```

#### Task 5.2: Railway Deployment for Brain Engine

1. Create new project in Railway
2. Connect to GitHub repository
3. Set **Root Directory** to `brain-engine`
4. Railway auto-detects Dockerfile
5. Add environment variables:

```
API_KEY=<generate a secure random key>
OXYLABS_USERNAME=<from Oxylabs dashboard>
OXYLABS_PASSWORD=<from Oxylabs dashboard>
DEBUG=false
```

6. Deploy and copy the public URL
7. Update `BRAIN_ENGINE_URL` in Vercel

---

### PHASE 6: Testing

#### Task 6.1: Local Testing Script

Create `brain-engine/tests/test_api.py`:

```python
"""Integration tests for Brain Engine API."""

import pytest
import httpx
from src.config import settings

BASE_URL = f"http://localhost:{settings.api_port}"
HEADERS = {
    "Authorization": f"Bearer {settings.api_key}",
    "Content-Type": "application/json",
}


@pytest.mark.asyncio
async def test_health_check():
    """Test health endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_search_requires_auth():
    """Test that search requires authentication."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/search",
            json={
                "origin": "LAX",
                "destination": "NRT",
                "departureDate": "2025-03-15",
            },
        )
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_search_flights():
    """Test flight search endpoint."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/search",
            headers=HEADERS,
            json={
                "origin": "LAX",
                "destination": "NRT",
                "departureDate": "2025-03-15",
                "returnDate": "2025-03-22",
                "passengers": 1,
                "cabinClass": "economy",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "flights" in data
        assert "countries_searched" in data
```

#### Task 6.2: Manual Testing Commands

```bash
# Test Brain Engine locally
cd brain-engine
python -m pytest tests/ -v

# Test health endpoint
curl http://localhost:8000/health

# Test flight search
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "origin": "LAX",
    "destination": "NRT",
    "departureDate": "2025-03-15",
    "returnDate": "2025-03-22"
  }'

# Test frontend locally
cd ..
pnpm dev
# Open http://localhost:3000 and try:
# "Find me cheap flights from LAX to Tokyo in March"
```

---

## 📝 Checklist for Devin

### Before Starting
- [ ] Read this entire document
- [ ] Understand the monorepo structure
- [ ] Have access to GitHub repository

### Phase 1: Setup
- [ ] Clone repository
- [ ] Update .gitignore with Python patterns
- [ ] Create/update vercel.json
- [ ] Update .env.example
- [ ] Create brain-engine directory structure

### Phase 2: Brain Engine
- [ ] Create requirements.txt
- [ ] Create config.py
- [ ] Create models/flight.py
- [ ] Create scraper/proxy.py
- [ ] Create scraper/browser.py
- [ ] Create scraper/flights.py
- [ ] Create main.py
- [ ] Create Dockerfile
- [ ] Create docker-compose.yml
- [ ] Create .env.example
- [ ] Create README.md
- [ ] Test locally with Docker

### Phase 3: Frontend Integration
- [ ] Create lib/ai/tools/search-flights.ts
- [ ] Update app/(chat)/api/chat/route.ts
- [ ] Update lib/ai/prompts.ts
- [ ] Test tool integration

### Phase 4: Database
- [ ] Update lib/db/schema.ts
- [ ] Update lib/db/queries.ts
- [ ] Generate migrations
- [ ] Run migrations

### Phase 5: Deployment
- [ ] Configure Vercel environment variables
- [ ] Deploy Brain Engine to Railway
- [ ] Update BRAIN_ENGINE_URL in Vercel
- [ ] Test production deployment

### Phase 6: Testing
- [ ] Write integration tests
- [ ] Test end-to-end flow
- [ ] Update README.md
- [ ] Document API endpoints

---

## 🚨 Important Notes for Devin

1. **Don't modify existing functionality** - Only add new code, don't break what's working
2. **Test incrementally** - Test each phase before moving to the next
3. **Commit often** - Make small, descriptive commits
4. **Error handling** - Always include proper error handling
5. **Environment variables** - Never commit secrets, use .env files
6. **Google Flights selectors** - These change frequently, the scraper may need adjustment

---

*Document Version: 2.0*
*Last Updated: December 2025*
*Repository: https://github.com/COG-GTM/vercel-ai-chatbot*

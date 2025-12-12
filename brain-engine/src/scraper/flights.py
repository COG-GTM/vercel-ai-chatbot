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
    origin = request.origin.upper()
    destination = request.destination.upper()
    
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

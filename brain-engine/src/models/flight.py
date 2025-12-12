"""Pydantic models for flight data."""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
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
    
    model_config = ConfigDict(populate_by_name=True)


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
    
    model_config = ConfigDict(
        json_schema_extra={
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
    )


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = "healthy"
    service: str = "brain-engine"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

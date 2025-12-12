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

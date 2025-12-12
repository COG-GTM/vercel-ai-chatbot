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

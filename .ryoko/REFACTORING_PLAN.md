# Ryoko Refactoring Plan

> **Document Purpose**: This is the comprehensive technical specification for building Ryoko, a B2C travel platform that transforms the vercel-ai-chatbot into a flight search application using geographic price arbitrage.

## Overview

**What we're building**: Ryoko - a chat-first travel platform that finds cheap airline tickets using geographic price arbitrage.

**Architecture**: Monorepo with Next.js frontend + Python Brain Engine

**Database**: Postgres (Neon) via Drizzle ORM (already integrated)

## Target Monorepo Structure

```
COG-GTM/vercel-ai-chatbot/
│
├── app/                          # Next.js App Router (existing)
│   ├── (auth)/                   # Authentication pages
│   ├── (chat)/                   # Chat application
│   │   └── api/
│   │       └── chat/
│   │           └── route.ts      # MODIFY: Add searchFlights tool
│   └── layout.tsx
│
├── components/                   # React components (existing)
│   ├── flight-results.tsx        # CREATE: Flight display component
│   └── ui/
│
├── lib/
│   ├── ai/
│   │   ├── prompts.ts            # MODIFY: Travel expert prompt
│   │   └── tools/
│   │       └── search-flights.ts # CREATE: Brain Engine tool
│   │
│   └── db/
│       ├── schema.ts             # MODIFY: Add flight tables
│       └── queries.ts            # MODIFY: Add flight queries
│
├── brain-engine/                 # CREATE: Entire folder
│   ├── src/
│   │   ├── main.py               # FastAPI application
│   │   ├── config.py             # Configuration management
│   │   ├── scraper/
│   │   │   ├── browser.py        # Playwright browser setup
│   │   │   ├── proxy.py          # Oxylabs proxy configuration
│   │   │   └── flights.py        # Flight scraping logic
│   │   └── models/
│   │       └── flight.py         # Pydantic models
│   │
│   ├── tests/
│   ├── .env.example
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── README.md
│
├── .env.example                  # MODIFY: Add Brain Engine vars
├── .gitignore                    # MODIFY: Add Python ignores
├── vercel.json                   # MODIFY: Exclude brain-engine
└── README.md                     # MODIFY: Update documentation
```

## Implementation Phases

### Phase 1: Repository Setup & Configuration
- Task 1.1: Clone and analyze existing codebase
- Task 1.2: Set up environment variables template
- Task 1.3: Create monorepo structure with brain-engine folder
- Task 1.4: Update .gitignore and vercel.json
- Task 1.5: Verify local development works

### Phase 2: Brain Engine Development
- Task 2.1: Create Python project structure
- Task 2.2: Implement FastAPI application
- Task 2.3: Build Playwright scraper with proxy support
- Task 2.4: Create flight data models
- Task 2.5: Add health check and error handling
- Task 2.6: Create Dockerfile
- Task 2.7: Test locally

### Phase 3: Frontend Integration
- Task 3.1: Create search-flights.ts tool
- Task 3.2: Register tool in chat route
- Task 3.3: Customize system prompt for travel
- Task 3.4: Update AI model configuration
- Task 3.5: Add flight result display component (optional)
- Task 3.6: Test end-to-end flow

### Phase 4: Database Schema Updates
- Task 4.1: Add flight search history table
- Task 4.2: Add price cache table
- Task 4.3: Run migrations
- Task 4.4: Create query functions

### Phase 5: Deployment Configuration
- Task 5.1: Configure Vercel deployment
- Task 5.2: Configure Railway deployment for Brain Engine
- Task 5.3: Set up environment variables in both platforms
- Task 5.4: Test production deployment
- Task 5.5: Document deployment process

### Phase 6: Testing & Documentation
- Task 6.1: Write integration tests
- Task 6.2: Test proxy functionality
- Task 6.3: Update README
- Task 6.4: Create API documentation

## Key Files to Create/Modify

### Files to CREATE:
- `brain-engine/` (entire directory)
- `lib/ai/tools/search-flights.ts`
- `components/flight-results.tsx` (optional)

### Files to MODIFY:
- `.gitignore` - Add Python patterns
- `.env.example` - Add Brain Engine vars
- `vercel.json` - Exclude brain-engine from deployment
- `app/(chat)/api/chat/route.ts` - Add searchFlights tool
- `lib/ai/prompts.ts` - Travel expert prompt
- `lib/db/schema.ts` - Add flight tables
- `lib/db/queries.ts` - Add flight queries

## Environment Variables Required

### Frontend (Vercel):
- `BRAIN_ENGINE_URL` - URL of deployed Brain Engine
- `BRAIN_ENGINE_API_KEY` - API key for Brain Engine

### Brain Engine (Railway):
- `API_KEY` - API authentication key
- `OXYLABS_USERNAME` - Oxylabs proxy username
- `OXYLABS_PASSWORD` - Oxylabs proxy password

## Important Notes

1. Don't modify existing functionality - Only add new code
2. Test incrementally - Test each phase before moving to the next
3. Commit often - Make small, descriptive commits
4. Error handling - Always include proper error handling
5. Environment variables - Never commit secrets
6. Google Flights selectors - These change frequently, scraper may need adjustment

---

*Full implementation details are in the original RYOKO_DEVIN_INSTRUCTIONS.md document*
*Repository: https://github.com/COG-GTM/vercel-ai-chatbot*

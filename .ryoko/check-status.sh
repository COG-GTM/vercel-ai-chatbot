#!/bin/bash

# Ryoko Refactoring Status Checker
# This script checks the current implementation status against the refactoring plan
# Run from the repository root: ./.ryoko/check-status.sh

# Note: We don't use set -e because check functions return non-zero for missing files

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory and repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$REPO_ROOT"

echo ""
echo "========================================"
echo "   Ryoko Refactoring Status Check"
echo "========================================"
echo ""
echo "Repository: $(pwd)"
echo "Date: $(date)"
echo ""

# Counters
TOTAL_FILES_TO_CREATE=0
CREATED_FILES=0
TOTAL_FILES_TO_MODIFY=0
MODIFIED_FILES=0

# Function to check if file exists
check_file_exists() {
    local file=$1
    local description=$2
    TOTAL_FILES_TO_CREATE=$((TOTAL_FILES_TO_CREATE + 1))
    if [ -e "$file" ]; then
        echo -e "  ${GREEN}[EXISTS]${NC} $file"
        CREATED_FILES=$((CREATED_FILES + 1))
        return 0
    else
        echo -e "  ${RED}[MISSING]${NC} $file"
        return 1
    fi
}

# Function to check if file contains specific content
check_file_contains() {
    local file=$1
    local pattern=$2
    local description=$3
    TOTAL_FILES_TO_MODIFY=$((TOTAL_FILES_TO_MODIFY + 1))
    if [ -f "$file" ]; then
        if grep -q "$pattern" "$file" 2>/dev/null; then
            echo -e "  ${GREEN}[MODIFIED]${NC} $file - $description"
            MODIFIED_FILES=$((MODIFIED_FILES + 1))
            return 0
        else
            echo -e "  ${YELLOW}[PENDING]${NC} $file - $description"
            return 1
        fi
    else
        echo -e "  ${RED}[FILE NOT FOUND]${NC} $file"
        return 1
    fi
}

# Function to check directory exists
check_dir_exists() {
    local dir=$1
    if [ -d "$dir" ]; then
        echo -e "  ${GREEN}[EXISTS]${NC} $dir/"
        return 0
    else
        echo -e "  ${RED}[MISSING]${NC} $dir/"
        return 1
    fi
}

echo "----------------------------------------"
echo "PHASE 1: Repository Setup"
echo "----------------------------------------"

echo ""
echo "Checking brain-engine directory structure:"
check_dir_exists "brain-engine"
check_dir_exists "brain-engine/src"
check_dir_exists "brain-engine/src/scraper"
check_dir_exists "brain-engine/src/models"
check_dir_exists "brain-engine/tests"

echo ""
echo "Checking configuration files:"
check_file_contains ".gitignore" "__pycache__" "Python patterns added"
check_file_contains ".env.example" "BRAIN_ENGINE" "Brain Engine vars added"
check_file_exists "vercel.json"

echo ""
echo "----------------------------------------"
echo "PHASE 2: Brain Engine Development"
echo "----------------------------------------"

echo ""
echo "Checking Brain Engine files:"
check_file_exists "brain-engine/requirements.txt"
check_file_exists "brain-engine/src/__init__.py"
check_file_exists "brain-engine/src/main.py"
check_file_exists "brain-engine/src/config.py"
check_file_exists "brain-engine/src/scraper/__init__.py"
check_file_exists "brain-engine/src/scraper/browser.py"
check_file_exists "brain-engine/src/scraper/proxy.py"
check_file_exists "brain-engine/src/scraper/flights.py"
check_file_exists "brain-engine/src/models/__init__.py"
check_file_exists "brain-engine/src/models/flight.py"
check_file_exists "brain-engine/Dockerfile"
check_file_exists "brain-engine/docker-compose.yml"
check_file_exists "brain-engine/.env.example"
check_file_exists "brain-engine/README.md"

echo ""
echo "----------------------------------------"
echo "PHASE 3: Frontend Integration"
echo "----------------------------------------"

echo ""
echo "Checking frontend integration files:"
check_file_exists "lib/ai/tools/search-flights.ts"
check_file_contains "app/(chat)/api/chat/route.ts" "searchFlights" "searchFlights tool registered"
check_file_contains "lib/ai/prompts.ts" "Ryoko\|travel\|flight" "Travel prompt added"

echo ""
echo "Optional files:"
check_file_exists "components/flight-results.tsx" || echo "    (This file is optional)"

echo ""
echo "----------------------------------------"
echo "PHASE 4: Database Schema Updates"
echo "----------------------------------------"

echo ""
echo "Checking database schema updates:"
check_file_contains "lib/db/schema.ts" "flightSearches\|flight_searches" "Flight search table added"
check_file_contains "lib/db/schema.ts" "flightPriceCache\|flight_price_cache" "Price cache table added"
check_file_contains "lib/db/queries.ts" "logFlightSearch\|getUserFlightSearches" "Flight query functions added"

echo ""
echo "----------------------------------------"
echo "PHASE 5: Deployment Configuration"
echo "----------------------------------------"

echo ""
echo "Checking deployment files:"
if [ -f "vercel.json" ]; then
    check_file_contains "vercel.json" "brain-engine" "brain-engine excluded from Vercel"
fi

echo ""
echo "----------------------------------------"
echo "PHASE 6: Testing & Documentation"
echo "----------------------------------------"

echo ""
echo "Checking test files:"
check_file_exists "brain-engine/tests/__init__.py"
check_file_exists "brain-engine/tests/test_api.py"

echo ""
echo "========================================"
echo "           SUMMARY"
echo "========================================"
echo ""

# Calculate percentages
if [ $TOTAL_FILES_TO_CREATE -gt 0 ]; then
    CREATE_PERCENT=$((CREATED_FILES * 100 / TOTAL_FILES_TO_CREATE))
else
    CREATE_PERCENT=0
fi

if [ $TOTAL_FILES_TO_MODIFY -gt 0 ]; then
    MODIFY_PERCENT=$((MODIFIED_FILES * 100 / TOTAL_FILES_TO_MODIFY))
else
    MODIFY_PERCENT=0
fi

TOTAL_TASKS=$((TOTAL_FILES_TO_CREATE + TOTAL_FILES_TO_MODIFY))
COMPLETED_TASKS=$((CREATED_FILES + MODIFIED_FILES))

if [ $TOTAL_TASKS -gt 0 ]; then
    OVERALL_PERCENT=$((COMPLETED_TASKS * 100 / TOTAL_TASKS))
else
    OVERALL_PERCENT=0
fi

echo "Files to Create: $CREATED_FILES / $TOTAL_FILES_TO_CREATE ($CREATE_PERCENT%)"
echo "Files to Modify: $MODIFIED_FILES / $TOTAL_FILES_TO_MODIFY ($MODIFY_PERCENT%)"
echo ""
echo -e "Overall Progress: ${BLUE}$COMPLETED_TASKS / $TOTAL_TASKS ($OVERALL_PERCENT%)${NC}"
echo ""

# Determine current phase
if [ $OVERALL_PERCENT -eq 0 ]; then
    echo -e "Current Phase: ${YELLOW}Not Started${NC}"
elif [ $OVERALL_PERCENT -lt 20 ]; then
    echo -e "Current Phase: ${YELLOW}Phase 1 - Repository Setup${NC}"
elif [ $OVERALL_PERCENT -lt 50 ]; then
    echo -e "Current Phase: ${YELLOW}Phase 2 - Brain Engine Development${NC}"
elif [ $OVERALL_PERCENT -lt 70 ]; then
    echo -e "Current Phase: ${YELLOW}Phase 3 - Frontend Integration${NC}"
elif [ $OVERALL_PERCENT -lt 85 ]; then
    echo -e "Current Phase: ${YELLOW}Phase 4/5 - Database & Deployment${NC}"
elif [ $OVERALL_PERCENT -lt 100 ]; then
    echo -e "Current Phase: ${YELLOW}Phase 6 - Testing & Documentation${NC}"
else
    echo -e "Current Phase: ${GREEN}COMPLETED${NC}"
fi

echo ""
echo "========================================"
echo ""

# Exit with appropriate code
if [ $OVERALL_PERCENT -eq 100 ]; then
    exit 0
else
    exit 1
fi

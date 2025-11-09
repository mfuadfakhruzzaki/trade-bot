#!/bin/bash

# Script to run Trading Bot with Dashboard
# This script starts both the bot and dashboard in separate processes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Trading Bot + Dashboard Launcher${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if virtual environment exists
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo -e "${RED}Error: Virtual environment not found${NC}"
    echo "Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source "$PROJECT_DIR/venv/bin/activate"

# Check if .env file exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please copy .env.example to .env and configure it"
    exit 1
fi

# Parse arguments
DRY_RUN=""
DASHBOARD_ONLY=false
BOT_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        --dashboard-only)
            DASHBOARD_ONLY=true
            shift
            ;;
        --bot-only)
            BOT_ONLY=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--dry-run] [--dashboard-only] [--bot-only]"
            exit 1
            ;;
    esac
done

# PID file for cleanup
BOT_PID=""
DASHBOARD_PID=""

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}Stopping services...${NC}"
    
    if [ ! -z "$BOT_PID" ]; then
        echo "Stopping bot (PID: $BOT_PID)..."
        kill $BOT_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$DASHBOARD_PID" ]; then
        echo "Stopping dashboard (PID: $DASHBOARD_PID)..."
        kill $DASHBOARD_PID 2>/dev/null || true
    fi
    
    echo -e "${GREEN}Services stopped${NC}"
    exit 0
}

# Trap signals
trap cleanup SIGINT SIGTERM

# Start Dashboard
if [ "$BOT_ONLY" = false ]; then
    echo -e "${GREEN}Starting Dashboard...${NC}"
    python "$PROJECT_DIR/run_dashboard.py" --host 0.0.0.0 --port 5000 > logs/dashboard.log 2>&1 &
    DASHBOARD_PID=$!
    echo -e "${GREEN}Dashboard started (PID: $DASHBOARD_PID)${NC}"
    echo -e "${BLUE}Dashboard URL: http://localhost:5000${NC}"
    sleep 2
fi

# Start Trading Bot
if [ "$DASHBOARD_ONLY" = false ]; then
    echo -e "${GREEN}Starting Trading Bot...${NC}"
    if [ ! -z "$DRY_RUN" ]; then
        echo -e "${YELLOW}Running in DRY-RUN mode (no real trades)${NC}"
    fi
    
    python "$PROJECT_DIR/main.py" $DRY_RUN &
    BOT_PID=$!
    echo -e "${GREEN}Bot started (PID: $BOT_PID)${NC}"
fi

# Display status
echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}Services Running:${NC}"
if [ "$DASHBOARD_ONLY" = false ]; then
    echo -e "  • Trading Bot (PID: $BOT_PID)"
fi
if [ "$BOT_ONLY" = false ]; then
    echo -e "  • Dashboard (PID: $DASHBOARD_PID) - http://localhost:5000"
fi
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Wait for processes
wait

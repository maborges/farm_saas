#!/usr/bin/env bash
# Script para rodar testes E2E do frontend com Playwright
# Uso: ./scripts/run-e2e-tests.sh [OPTIONS]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default values
PROJECT=""
DEBUG=false
UI=false
REPORT=false
CODEGEN=false
BASE_URL=""

show_help() {
    cat << EOF
${BLUE}========================================${NC}
${GREEN}🎭 AgroSaaS - E2E Test Runner${NC}
${BLUE}========================================${NC}

${YELLOW}Usage:${NC}
  ./scripts/run-e2e-tests.sh [OPTIONS]

${YELLOW}Options:${NC}
  -h, --help              Show this help
  -p, --project PROJECT   Run specific project (chromium, firefox, webkit)
  -d, --debug             Run in debug mode
  --ui                    Open UI mode
  --report                Show last report
  --codegen               Open codegen tool
  -u, --url URL           Base URL (default: http://localhost:3000)

${YELLOW}Examples:${NC}
  # Run all tests
  ./scripts/run-e2e-tests.sh

  # Run only on Chromium
  ./scripts/run-e2e-tests.sh -p chromium

  # Run in debug mode
  ./scripts/run-e2e-tests.sh -d

  # Open UI mode
  ./scripts/run-e2e-tests.sh --ui

  # Show report
  ./scripts/run-e2e-tests.sh --report

  # Generate tests with codegen
  ./scripts/run-e2e-tests.sh --codegen

${YELLOW}Projects:${NC}
  - chromium (Desktop Chrome)
  - firefox (Desktop Firefox)
  - webkit (Desktop Safari)
  - Mobile Chrome
  - Mobile Safari
  - Microsoft Edge
  - Google Chrome

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -p|--project)
            PROJECT="$2"
            shift 2
            ;;
        -d|--debug)
            DEBUG=true
            shift
            ;;
        --ui)
            UI=true
            shift
            ;;
        --report)
            REPORT=true
            shift
            ;;
        --codegen)
            CODEGEN=true
            shift
            ;;
        -u|--url)
            BASE_URL="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Change to web directory
cd "$(dirname "$0")/.."
cd apps/web

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🎭 AgroSaaS - E2E Tests${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  Installing dependencies...${NC}"
    pnpm install
fi

# Install Playwright browsers if needed
if [ ! -d "node_modules/@playwright/test" ]; then
    echo -e "${YELLOW}📦 Installing Playwright...${NC}"
    pnpm add -D @playwright/test
fi

# Run commands
if [ "$REPORT" = true ]; then
    echo -e "${YELLOW}📊 Opening test report...${NC}"
    pnpm playwright show-report
    exit 0
fi

if [ "$CODEGEN" = true ]; then
    echo -e "${YELLOW}🔧 Opening codegen tool...${NC}"
    pnpm playwright codegen ${BASE_URL:-http://localhost:3000}
    exit 0
fi

if [ "$UI" = true ]; then
    echo -e "${YELLOW}🎨 Opening UI mode...${NC}"
    pnpm playwright test --ui
    exit 0
fi

# Build test command
PLAYWRIGHT_CMD="pnpm playwright test"

# Add project filter
if [ -n "$PROJECT" ]; then
    PLAYWRIGHT_CMD="$PLAYWRIGHT_CMD --project=$PROJECT"
fi

# Add debug mode
if [ "$DEBUG" = true ]; then
    PLAYWRIGHT_CMD="$PLAYWRIGHT_CMD --debug"
fi

# Add base URL
if [ -n "$BASE_URL" ]; then
    PLAYWRIGHT_CMD="BASE_URL=$BASE_URL $PLAYWRIGHT_CMD"
fi

# Run tests
echo -e "${YELLOW}🚀 Running E2E tests...${NC}"
echo -e "${BLUE}Command: $PLAYWRIGHT_CMD${NC}"
echo ""

if eval $PLAYWRIGHT_CMD; then
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}✅ All E2E tests passed!${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "${YELLOW}📊 To view report: ./scripts/run-e2e-tests.sh --report${NC}"
    exit 0
else
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${RED}❌ Some E2E tests failed!${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "${YELLOW}💡 Tip: Run with --debug to investigate failures${NC}"
    exit 1
fi

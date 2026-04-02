#!/usr/bin/env bash
# Script para rodar testes automatizados do backend
# Uso: ./scripts/run-tests.sh [OPTIONS]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TEST_PATH=""
COVERAGE=false
VERBOSE=false
MARKER=""
HTML_REPORT=false
FAST=false

# Help function
show_help() {
    cat << EOF
${BLUE}========================================${NC}
${GREEN}AgroSaaS - Backend Test Runner${NC}
${BLUE}========================================${NC}

${YELLOW}Usage:${NC}
  ./scripts/run-tests.sh [OPTIONS]

${YELLOW}Options:${NC}
  -h, --help              Show this help message
  -p, --path PATH         Run specific test file or directory
  -c, --coverage          Generate coverage report
  -v, --verbose           Verbose output
  -m, --marker MARKER     Run tests with specific marker
  --html                  Generate HTML report
  -f, --fast              Fast mode (skip slow tests)
  --unit                  Run only unit tests
  --integration           Run only integration tests
  --e2e                   Run only E2E tests

${YELLOW}Examples:${NC}
  # Run all tests
  ./scripts/run-tests.sh

  # Run specific test file
  ./scripts/run-tests.sh -p tests/financeiro/test_nfe_xml.py

  # Run with coverage
  ./scripts/run-tests.sh -c

  # Run only financial module tests
  ./scripts/run-tests.sh -m financeiro

  # Run only unit tests (fast)
  ./scripts/run-tests.sh --fast

  # Run integration tests
  ./scripts/run-tests.sh --integration

${YELLOW}Markers available:${NC}
  - core, agricola, financeiro, operacional, pecuaria, rh
  - integration, e2e, slow

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -p|--path)
            TEST_PATH="$2"
            shift 2
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -m|--marker)
            MARKER="$2"
            shift 2
            ;;
        --html)
            HTML_REPORT=true
            shift
            ;;
        -f|--fast)
            FAST=true
            shift
            ;;
        --unit)
            MARKER="not integration and not e2e"
            shift
            ;;
        --integration)
            MARKER="integration"
            shift
            ;;
        --e2e)
            MARKER="e2e"
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Change to project root
cd "$(dirname "$0")/.."

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🧪 AgroSaaS - Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if .venv exists
if [ ! -d "services/api/.venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    cd services/api
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    cd ../..
fi

# Activate virtual environment
echo -e "${YELLOW}📦 Activating virtual environment...${NC}"
source services/api/.venv/bin/activate

# Build pytest command
PYTEST_CMD="pytest"

# Add verbose flag if requested
if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -vv"
fi

# Add coverage flags if requested
if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=services/api --cov-report=term-missing"
    if [ "$HTML_REPORT" = true ]; then
        PYTEST_CMD="$PYTEST_CMD --cov-report=html:htmlcov"
    fi
fi

# Add marker filter if specified
if [ -n "$MARKER" ]; then
    PYTEST_CMD="$PYTEST_CMD -m \"$MARKER\""
fi

# Add fast mode (skip slow tests)
if [ "$FAST" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -m \"not slow\""
fi

# Add test path if specified
if [ -n "$TEST_PATH" ]; then
    PYTEST_CMD="$PYTEST_CMD $TEST_PATH"
else
    PYTEST_CMD="$PYTEST_CMD services/api/tests"
fi

# Run tests
echo -e "${YELLOW}🚀 Running tests...${NC}"
echo -e "${BLUE}Command: $PYTEST_CMD${NC}"
echo ""

if eval $PYTEST_CMD; then
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    # Show coverage report location if generated
    if [ "$HTML_REPORT" = true ]; then
        echo ""
        echo -e "${YELLOW}📊 HTML coverage report generated at: htmlcov/index.html${NC}"
    fi
    
    exit 0
else
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${RED}❌ Some tests failed!${NC}"
    echo -e "${BLUE}========================================${NC}"
    exit 1
fi

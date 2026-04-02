#!/usr/bin/env bash
# Script de diagnóstico para testes falhando
# Uso: ./scripts/debug-test-failure.sh [test_file.py] [error_message]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🔍 AgroSaaS - Debug Assistant${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if test file provided
if [ -z "$1" ]; then
    echo -e "${YELLOW}Usage:${NC}"
    echo "  ./scripts/debug-test-failure.sh [test_file.py]"
    echo "  ./scripts/debug-test-failure.sh tests/financeiro/test_nfe.py"
    echo ""
    echo -e "${YELLOW}Common issues quick check:${NC}"
    echo ""
    
    # Quick diagnostics
    echo -e "${MAGENTA}1. Checking backend environment...${NC}"
    if [ -d "services/api/.venv" ]; then
        echo -e "${GREEN}✓ Virtual environment exists${NC}"
    else
        echo -e "${RED}✗ Virtual environment not found!${NC}"
        echo -e "${YELLOW}  Fix: cd services/api && python3 -m venv .venv${NC}"
    fi
    
    echo -e "${MAGENTA}2. Checking frontend dependencies...${NC}"
    if [ -d "apps/web/node_modules" ]; then
        echo -e "${GREEN}✓ Node modules installed${NC}"
    else
        echo -e "${RED}✗ Node modules not found!${NC}"
        echo -e "${YELLOW}  Fix: cd apps/web && pnpm install${NC}"
    fi
    
    echo -e "${MAGENTA}3. Checking database connection...${NC}"
    if command -v docker &> /dev/null && docker ps | grep -q postgres; then
        echo -e "${GREEN}✓ PostgreSQL is running${NC}"
    else
        echo -e "${YELLOW}⚠ PostgreSQL not detected or docker not installed${NC}"
    fi
    
    echo -e "${MAGENTA}4. Checking pytest installation...${NC}"
    if [ -f "services/api/.venv/bin/pytest" ]; then
        echo -e "${GREEN}✓ pytest installed${NC}"
    else
        echo -e "${RED}✗ pytest not found!${NC}"
        echo -e "${YELLOW}  Fix: source services/api/.venv/bin/activate && pip install pytest pytest-asyncio${NC}"
    fi
    
    echo -e "${MAGENTA}5. Checking Playwright installation...${NC}"
    if [ -f "apps/web/node_modules/@playwright/test/cli.js" ]; then
        echo -e "${GREEN}✓ Playwright installed${NC}"
    else
        echo -e "${RED}✗ Playwright not found!${NC}"
        echo -e "${YELLOW}  Fix: cd apps/web && pnpm add -D @playwright/test && pnpm exec playwright install${NC}"
    fi
    
    echo ""
    exit 0
fi

TEST_FILE="$1"

echo -e "${YELLOW}Analyzing test file: ${GREEN}$TEST_FILE${NC}"
echo ""

# Check if file exists
if [ ! -f "$TEST_FILE" ]; then
    echo -e "${RED}✗ Test file not found: $TEST_FILE${NC}"
    echo ""
    echo -e "${YELLOW}Available test files:${NC}"
    find . -name "test_*.py" -type f | head -20
    exit 1
fi

# Analyze test file
echo -e "${MAGENTA}📊 Test File Analysis:${NC}"
echo ""

# Count tests
TEST_COUNT=$(grep -c "^async def test_\|^def test_" "$TEST_FILE" 2>/dev/null || echo "0")
echo -e "Total tests in file: ${GREEN}$TEST_COUNT${NC}"

# Check for common issues
echo ""
echo -e "${MAGENTA}🔍 Checking for common issues...${NC}"
echo ""

# Check imports
echo -e "${BLUE}1. Checking imports...${NC}"
if grep -q "import pytest" "$TEST_FILE"; then
    echo -e "   ${GREEN}✓ pytest imported${NC}"
else
    echo -e "   ${RED}✗ pytest not imported${NC}"
fi

if grep -q "from sqlalchemy" "$TEST_FILE" || grep -q "import sqlalchemy" "$TEST_FILE"; then
    echo -e "   ${GREEN}✓ sqlalchemy imported${NC}"
else
    echo -e "   ${YELLOW}⚠ sqlalchemy not imported (may be OK)${NC}"
fi

# Check fixtures
echo ""
echo -e "${BLUE}2. Checking fixtures usage...${NC}"
if grep -q "@pytest.fixture" "$TEST_FILE"; then
    echo -e "   ${GREEN}✓ Custom fixtures defined${NC}"
fi

if grep -q "session:" "$TEST_FILE" || grep -q "session: AsyncSession" "$TEST_FILE"; then
    echo -e "   ${GREEN}✓ Using session fixture${NC}"
else
    echo -e "   ${YELLOW}⚠ session fixture not used${NC}"
fi

if grep -q "tenant_id" "$TEST_FILE"; then
    echo -e "   ${GREEN}✓ Using tenant_id fixture${NC}"
else
    echo -e "   ${YELLOW}⚠ tenant_id fixture not used (may cause isolation issues)${NC}"
fi

# Check test structure
echo ""
echo -e "${BLUE}3. Checking test structure...${NC}"

# Check for Arrange-Act-Assert pattern
if grep -q "# Arrange" "$TEST_FILE" || grep -q "# Act" "$TEST_FILE" || grep -q "# Assert" "$TEST_FILE"; then
    echo -e "   ${GREEN}✓ AAA pattern comments found${NC}"
else
    echo -e "   ${YELLOW}⚠ Consider adding AAA comments for clarity${NC}"
fi

# Check for async
if grep -q "async def test_" "$TEST_FILE"; then
    echo -e "   ${GREEN}✓ Async tests detected${NC}"
    if grep -q "@pytest.mark.asyncio" "$TEST_FILE" || grep -q "asyncio_mode" "pyproject.toml" 2>/dev/null; then
        echo -e "   ${GREEN}✓ Async marker configured${NC}"
    else
        echo -e "   ${YELLOW}⚠ Ensure pytest-asyncio is configured${NC}"
    fi
else
    echo -e "   ${BLUE}ℹ Sync tests detected${NC}"
fi

# Check for common anti-patterns
echo ""
echo -e "${BLUE}4. Checking for anti-patterns...${NC}"

# Check for hardcoded IDs
if grep -qE "uuid4\(\)|UUID\('[a-f0-9-]+'\)" "$TEST_FILE"; then
    echo -e "   ${GREEN}✓ Using dynamic UUIDs${NC}"
else
    if grep -qE "id=['\"]?[0-9a-f-]+" "$TEST_FILE"; then
        echo -e "   ${YELLOW}⚠ Hardcoded IDs found (may cause isolation issues)${NC}"
    fi
fi

# Check for proper assertions
ASSERT_COUNT=$(grep -c "assert " "$TEST_FILE" 2>/dev/null || echo "0")
if [ "$ASSERT_COUNT" -gt 0 ]; then
    echo -e "   ${GREEN}✓ Assertions found ($ASSERT_COUNT)${NC}"
else
    echo -e "   ${RED}✗ No assertions found!${NC}"
fi

# Check for cleanup
if grep -q "await session.rollback\|await session.delete\|teardown" "$TEST_FILE"; then
    echo -e "   ${GREEN}✓ Cleanup code detected${NC}"
else
    echo -e "   ${BLUE}ℹ Using fixture-based cleanup (OK)${NC}"
fi

# Run test with verbose output
echo ""
echo -e "${MAGENTA}🧪 Running tests with verbose output...${NC}"
echo ""

cd "$(dirname "$0")/.."

if [ -f "services/api/.venv/bin/pytest" ]; then
    source services/api/.venv/bin/activate
    
    echo -e "${YELLOW}Command: pytest $TEST_FILE -v -s${NC}"
    echo ""
    
    if pytest "$TEST_FILE" -v -s --tb=short 2>&1 | tee /tmp/test_output.log; then
        echo ""
        echo -e "${BLUE}========================================${NC}"
        echo -e "${GREEN}✅ Tests passed!${NC}"
        echo -e "${BLUE}========================================${NC}"
    else
        echo ""
        echo -e "${BLUE}========================================${NC}"
        echo -e "${RED}❌ Tests failed!${NC}"
        echo -e "${BLUE}========================================${NC}"
        echo ""
        
        # Analyze error
        echo -e "${MAGENTA}📋 Error Analysis:${NC}"
        echo ""
        
        if grep -q "EntityNotFoundError" /tmp/test_output.log; then
            echo -e "${YELLOW}Issue: EntityNotFoundError${NC}"
            echo -e "${BLUE}Possible causes:${NC}"
            echo "  1. Trying to access data from wrong tenant"
            echo "  2. Referencing non-existent entity"
            echo "  3. Setup not creating required data"
            echo ""
            echo -e "${GREEN}Fix:${NC}"
            echo "  - Ensure all referenced entities are created in setup"
            echo "  - Check tenant_id matches between entities"
            echo "  - Use fixtures: session, tenant_id, talhao_id"
        fi
        
        if grep -q "BusinessRuleError" /tmp/test_output.log; then
            echo -e "${YELLOW}Issue: BusinessRuleError${NC}"
            echo -e "${BLUE}Possible causes:${NC}"
            echo "  1. Business validation working correctly"
            echo "  2. Test expecting wrong behavior"
            echo "  3. Invalid operation for current state"
            echo ""
            echo -e "${GREEN}Fix:${NC}"
            echo "  - Wrap in pytest.raises(BusinessRuleError) if expected"
            echo "  - Fix test expectations if validation is correct"
            echo "  - Check state/phase requirements"
        fi
        
        if grep -q "AssertionError" /tmp/test_output.log; then
            echo -e "${YELLOW}Issue: AssertionError${NC}"
            echo -e "${BLUE}Possible causes:${NC}"
            echo "  1. Unexpected value from calculation"
            echo "  2. Webhook created extra data"
            echo "  3. Test data not matching expected"
            echo ""
            echo -e "${GREEN}Fix:${NC}"
            echo "  - Debug actual vs expected values"
            echo "  - Check for automatic webhook actions"
            echo "  - Verify test setup data"
        fi
        
        if grep -q "IntegrityError" /tmp/test_output.log; then
            echo -e "${YELLOW}Issue: IntegrityError (Database)${NC}"
            echo -e "${BLUE}Possible causes:${NC}"
            echo "  1. Foreign key constraint violation"
            echo "  2. Unique constraint violation"
            echo "  3. Creating entities in wrong order"
            echo ""
            echo -e "${GREEN}Fix:${NC}"
            echo "  - Create parent entities before children"
            echo "  - Ensure all foreign keys reference existing IDs"
            echo "  - Check for duplicate unique values"
        fi
        
        if grep -q "TimeoutError\|timeout" /tmp/test_output.log; then
            echo -e "${YELLOW}Issue: TimeoutError${NC}"
            echo -e "${BLUE}Possible causes:${NC}"
            echo "  1. Async operation not awaited"
            echo "  2. Database query hanging"
            echo "  3. External service not responding"
            echo ""
            echo -e "${GREEN}Fix:${NC}"
            echo "  - Ensure all async calls use 'await'"
            echo "  - Check database connection"
            echo "  - Increase timeout if needed"
        fi
    fi
else
    echo -e "${RED}pytest not found! Activate virtual environment first.${NC}"
    echo -e "${YELLOW}Fix: source services/api/.venv/bin/activate${NC}"
fi

echo ""
echo -e "${YELLOW}For more help, see: docs/GUIA_CORRECAO_BUGS.md${NC}"

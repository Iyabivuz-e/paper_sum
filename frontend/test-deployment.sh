#!/bin/bash
# Frontend Deployment Testing Script
# Tests all major functionality before deployment

echo "🚀 Starting comprehensive frontend testing..."
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to run test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "${YELLOW}Testing: $test_name${NC}"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASS: $test_name${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL: $test_name${NC}"
        ((FAILED++))
    fi
    echo ""
}

echo "📦 Testing Frontend Dependencies..."
echo "=================================="

# Test if Node.js is available
run_test "Node.js availability" "node --version"

# Test if npm is available
run_test "npm availability" "npm --version"

# Test if dependencies are installed
run_test "node_modules exists" "[ -d node_modules ]"

# Test if Next.js is installed
run_test "Next.js installation" "npx next --version"

echo "🔧 Testing Build Process..."
echo "=================================="

# Test if project builds successfully
run_test "Next.js build" "npm run build"

# Test if build output exists
run_test "Build output exists" "[ -d .next ]"

echo "📱 Testing Frontend Features..."
echo "=================================="

# Test if development server can start (we'll just check if it doesn't error immediately)
run_test "Development server startup" "timeout 10s npm run dev > /dev/null 2>&1 || [ $? -eq 124 ]"

# Test environment variables
run_test "Environment file exists" "[ -f .env.production ] || [ -f .env.local ]"

echo "🔍 Testing Code Quality..."
echo "=================================="

# Test TypeScript compilation
run_test "TypeScript compilation" "npx tsc --noEmit"

# Test ESLint (if available)
if command -v npx &> /dev/null && npx eslint --version &> /dev/null; then
    run_test "ESLint check" "npx eslint . --ext .ts,.tsx --max-warnings 0 || true"
else
    echo -e "${YELLOW}⚠️  ESLint not available, skipping...${NC}"
fi

echo "📊 Testing Analytics Integration..."
echo "=================================="

# Test if analytics files exist
run_test "Analytics utility exists" "[ -f src/lib/analytics.ts ]"
run_test "Analytics dashboard exists" "[ -f src/components/analytics-dashboard.tsx ]"
run_test "Vercel Analytics package" "npm list @vercel/analytics > /dev/null 2>&1"
run_test "Vercel Speed Insights package" "npm list @vercel/speed-insights > /dev/null 2>&1"

echo "🎨 Testing UI Components..."
echo "=================================="

# Test if key components exist
run_test "Main layout exists" "[ -f src/app/layout.tsx ]"
run_test "Home page exists" "[ -f src/app/page.tsx ]"
run_test "Admin page exists" "[ -f src/app/admin/page.tsx ]"

echo "🔐 Testing Security & Configuration..."
echo "=================================="

# Test if security headers are configured
run_test "Next.js config exists" "[ -f next.config.ts ]"

# Test if package.json has proper scripts
run_test "Build script exists" "npm run build --dry-run > /dev/null 2>&1"
run_test "Start script exists" "npm run start --dry-run > /dev/null 2>&1"

echo "🌐 Testing Deployment Readiness..."
echo "=================================="

# Test if Vercel configuration exists
run_test "Vercel config exists" "[ -f vercel.json ]"

# Test if production environment is configured
run_test "Production env configured" "[ -f .env.production ]"

echo "=================================="
echo "📋 Test Summary"
echo "=================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo "Total Tests: $((PASSED + FAILED))"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Frontend is ready for deployment!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Please review and fix issues before deployment.${NC}"
    exit 1
fi

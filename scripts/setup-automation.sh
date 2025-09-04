#!/bin/bash
# Setup script to ensure automation is properly configured
# Run this if hooks aren't working or for new clones

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🤖 Setting up automated CI/CD testing...${NC}"
echo "================================================"

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

# Check if act is installed
if ! command -v act &> /dev/null; then
    echo -e "${YELLOW}📦 Installing act (GitHub Actions local runner)...${NC}"
    if command -v brew &> /dev/null; then
        brew install act
        echo -e "${GREEN}✅ act installed via Homebrew${NC}"
    else
        echo -e "${RED}❌ Please install act manually:${NC}"
        echo -e "   ${YELLOW}https://github.com/nektos/act#installation${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ act is installed${NC}"
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Docker is running${NC}"
fi

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${YELLOW}📦 Installing poetry...${NC}"
    pip install poetry
    echo -e "${GREEN}✅ poetry installed${NC}"
else
    echo -e "${GREEN}✅ poetry is installed${NC}"
fi

# Install dependencies
echo -e "${YELLOW}📦 Installing project dependencies...${NC}"
poetry install
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Setup pre-commit hooks
echo -e "${YELLOW}🔧 Setting up pre-commit hooks...${NC}"
if ! command -v pre-commit &> /dev/null; then
    pip install pre-commit
fi
pre-commit install
echo -e "${GREEN}✅ Pre-commit hooks installed${NC}"

# Setup pre-push hook
echo -e "${YELLOW}🔧 Setting up pre-push hook (automatic local CI)...${NC}"
if [[ -f .pre-push ]]; then
    cp .pre-push .git/hooks/pre-push
    chmod +x .git/hooks/pre-push
    echo -e "${GREEN}✅ Pre-push hook installed${NC}"
else
    echo -e "${RED}❌ .pre-push file not found${NC}"
    exit 1
fi

# Test the setup
echo -e "${YELLOW}🧪 Testing the automation setup...${NC}"

# Test pre-commit
echo -e "${BLUE}Testing pre-commit hooks...${NC}"
if pre-commit run --all-files &> /dev/null; then
    echo -e "${GREEN}✅ Pre-commit hooks working${NC}"
else
    echo -e "${YELLOW}⚠️  Pre-commit found issues (this is normal - they were fixed)${NC}"
fi

# Test local CI info
echo -e "${BLUE}Testing local CI setup...${NC}"
if ./scripts/test-local-ci.sh info &> /dev/null; then
    echo -e "${GREEN}✅ Local CI setup working${NC}"
else
    echo -e "${RED}❌ Local CI setup has issues${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Automation setup complete!${NC}"
echo ""
echo -e "${BLUE}📋 What's now automated:${NC}"
echo -e "   ${GREEN}✅ git commit${NC} → runs quick tests + formatting"
echo -e "   ${GREEN}✅ git push${NC} → runs full GitHub Actions locally first"
echo -e "   ${GREEN}✅ Prevents failed CI builds${NC} on GitHub"
echo ""
echo -e "${BLUE}📚 Useful commands:${NC}"
echo -e "   ${YELLOW}make help${NC}           - See all available commands"
echo -e "   ${YELLOW}make test-local-ci${NC}  - Run GitHub Actions locally"
echo -e "   ${YELLOW}make push-safe${NC}      - Test locally then push"
echo ""
echo -e "${BLUE}📖 For more details:${NC}"
echo -e "   ${YELLOW}cat AUTOMATION.md${NC}   - Complete automation guide"
echo -e "   ${YELLOW}cat docs/local-ci-testing.md${NC} - Technical details"
echo ""
echo -e "${GREEN}💡 Just use git normally - everything is automatic!${NC}"

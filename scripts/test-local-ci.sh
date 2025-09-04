#!/bin/bash
# Local CI/CD Testing Script
# Runs GitHub Actions locally using `act` before pushing to remote

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Local GitHub Actions Testing${NC}"
echo "=================================================="

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

# Check if act is installed
if ! command -v act &> /dev/null; then
    echo -e "${RED}❌ act is not installed. Install it with:${NC}"
    echo -e "   ${YELLOW}brew install act${NC} (macOS)"
    echo -e "   ${YELLOW}npm install -g @nektos/act${NC} (npm)"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites satisfied${NC}"

# Check current git status
echo -e "${YELLOW}📊 Current git status:${NC}"
git status --porcelain

if [[ -n $(git status --porcelain) ]]; then
    echo -e "${YELLOW}⚠️  You have uncommitted changes. Consider committing them first.${NC}"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create act configuration if it doesn't exist
if [[ ! -f .actrc ]]; then
    echo -e "${YELLOW}📝 Creating .actrc configuration...${NC}"
    cat > .actrc << 'EOF'
# Use larger runner image to match GitHub more closely
-P ubuntu-latest=catthehacker/ubuntu:act-latest

# Enable verbose logging
--verbose

# Use host network (helpful for some operations)
--use-host-network

# Don't pull images automatically (faster subsequent runs)
--pull=false
EOF
    echo -e "${GREEN}✅ Created .actrc${NC}"
fi

# Create secrets file if it doesn't exist
if [[ ! -f .secrets ]]; then
    echo -e "${YELLOW}📝 Creating .secrets file (empty - add secrets as needed)...${NC}"
    cat > .secrets << 'EOF'
# Add your secrets here in KEY=VALUE format
# Example:
# PYPI_TOKEN=your_token_here
EOF
    echo -e "${GREEN}✅ Created .secrets (remember to add actual secrets if needed)${NC}"
fi

# Function to run specific workflow
run_workflow() {
    local workflow_name=$1
    local event_type=${2:-push}

    echo -e "${BLUE}🔄 Running workflow: ${workflow_name}${NC}"
    echo "--------------------------------------------------"

    # Use act to run the workflow
    if act "$event_type" \
        --workflows ".github/workflows/${workflow_name}" \
        --secret-file .secrets \
        --artifact-server-path /tmp/act-artifacts; then
        echo -e "${GREEN}✅ Workflow ${workflow_name} passed locally!${NC}"
        return 0
    else
        echo -e "${RED}❌ Workflow ${workflow_name} failed locally!${NC}"
        return 1
    fi
}

# Function to run all workflows
run_all_workflows() {
    echo -e "${BLUE}🔄 Running all workflows...${NC}"

    # Run main CI workflow
    if ! act push \
        --secret-file .secrets \
        --artifact-server-path /tmp/act-artifacts; then
        echo -e "${RED}❌ CI workflow failed!${NC}"
        return 1
    fi

    echo -e "${GREEN}✅ All workflows passed locally!${NC}"
    return 0
}

# Function to show act status
show_act_info() {
    echo -e "${BLUE}📊 Act Information:${NC}"
    echo "--------------------------------------------------"
    echo -e "${YELLOW}Act version:${NC} $(act --version)"
    echo -e "${YELLOW}Docker version:${NC} $(docker --version)"
    echo -e "${YELLOW}Available workflows:${NC}"
    act --list
    echo "--------------------------------------------------"
}

# Function to clean act cache
clean_act_cache() {
    echo -e "${YELLOW}🧹 Cleaning act cache...${NC}"
    docker system prune -f
    rm -rf /tmp/act-artifacts
    echo -e "${GREEN}✅ Act cache cleaned${NC}"
}

# Main execution
main() {
    case "${1:-all}" in
        "info")
            show_act_info
            ;;
        "clean")
            clean_act_cache
            ;;
        "ci"|"main")
            run_workflow "ci.yml" "push"
            ;;
        "pr")
            run_workflow "ci.yml" "pull_request"
            ;;
        "all")
            show_act_info
            echo ""
            run_all_workflows
            ;;
        "help"|"--help"|"-h")
            echo -e "${BLUE}Local CI Testing Script${NC}"
            echo ""
            echo -e "${YELLOW}Usage:${NC}"
            echo "  $0 [command]"
            echo ""
            echo -e "${YELLOW}Commands:${NC}"
            echo "  all      Run all workflows (default)"
            echo "  ci       Run CI workflow only"
            echo "  pr       Run CI workflow as pull request"
            echo "  info     Show act and workflow information"
            echo "  clean    Clean act cache and artifacts"
            echo "  help     Show this help message"
            echo ""
            echo -e "${YELLOW}Examples:${NC}"
            echo "  $0           # Run all workflows"
            echo "  $0 ci        # Run CI workflow only"
            echo "  $0 info      # Show workflow information"
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $1${NC}"
            echo -e "Use ${YELLOW}$0 help${NC} for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"

# Final status
if [[ $? -eq 0 ]]; then
    echo ""
    echo -e "${GREEN}🎉 Local testing completed successfully!${NC}"
    echo -e "${GREEN}✅ Your changes should pass GitHub Actions${NC}"
    echo -e "${YELLOW}💡 Now you can safely push to GitHub:${NC} git push"
else
    echo ""
    echo -e "${RED}❌ Local testing failed!${NC}"
    echo -e "${RED}🔧 Fix the issues before pushing to GitHub${NC}"
    exit 1
fi

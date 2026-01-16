#!/bin/bash
# Transfer project files to SSH server
# Usage: ./transfer_to_ssh.sh user@hostname:/path/to/destination

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if destination is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: SSH destination not provided${NC}"
    echo ""
    echo "Usage: $0 user@hostname:/path/to/destination"
    echo ""
    echo "Example:"
    echo "  $0 user@example.com:~/vla_project"
    echo "  $0 ubuntu@192.168.1.100:/home/ubuntu/vla_semantic_robustness"
    exit 1
fi

DEST="$1"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${GREEN}Transferring files to: ${DEST}${NC}"
echo -e "${YELLOW}Source directory: ${SOURCE_DIR}${NC}"
echo ""

# Check if rsync is available (preferred for efficiency)
if command -v rsync &> /dev/null; then
    echo -e "${GREEN}Using rsync (recommended)${NC}"
    echo ""
    
    # Exclude patterns
    EXCLUDE_PATTERNS=(
        "--exclude='.git'"
        "--exclude='__pycache__'"
        "--exclude='*.pyc'"
        "--exclude='*.pyo'"
        "--exclude='.DS_Store'"
        "--exclude='*.log'"
        "--exclude='.ipynb_checkpoints'"
        "--exclude='*.swp'"
        "--exclude='*.swo'"
        "--exclude='*~'"
        "--exclude='.pytest_cache'"
        "--exclude='.mypy_cache'"
        "--exclude='.ruff_cache'"
    )
    
    # Use rsync with progress
    rsync -avz --progress \
        "${EXCLUDE_PATTERNS[@]}" \
        "${SOURCE_DIR}/" \
        "${DEST}/"
    
    echo ""
    echo -e "${GREEN}Transfer complete!${NC}"
    
elif command -v scp &> /dev/null; then
    echo -e "${YELLOW}Using scp (rsync recommended for better performance)${NC}"
    echo ""
    echo -e "${YELLOW}Note: This will transfer ALL files including logs and cache${NC}"
    echo -e "${YELLOW}Consider installing rsync on your system for better control${NC}"
    echo ""
    
    read -p "Continue with scp? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    
    scp -r "${SOURCE_DIR}"/* "${DEST}/"
    
    echo ""
    echo -e "${GREEN}Transfer complete!${NC}"
else
    echo -e "${RED}Error: Neither rsync nor scp is available${NC}"
    echo "Please install rsync: brew install rsync (on macOS)"
    exit 1
fi

echo ""
echo -e "${GREEN}Next steps on remote server:${NC}"
echo "1. SSH into your server: ssh ${DEST%%:*}"
echo "2. Navigate to the project directory"
echo "3. Run: cd SimplerEnv && bash install_linux.sh"


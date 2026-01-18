#!/bin/bash
# Script to push this repository to GitHub
# Usage: ./push_to_github.sh YOUR_USERNAME REPO_NAME

set -e

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 YOUR_USERNAME REPO_NAME"
    echo ""
    echo "Example:"
    echo "  $0 johndoe vla-semantic-robustness-stress-test"
    echo ""
    echo "First, create a new repository on GitHub:"
    echo "  1. Go to https://github.com/new"
    echo "  2. Create a new repository (don't initialize with README)"
    echo "  3. Then run this script with your username and repo name"
    exit 1
fi

USERNAME="$1"
REPO_NAME="$2"

echo "=========================================="
echo "Pushing to GitHub"
echo "=========================================="
echo "Repository: $USERNAME/$REPO_NAME"
echo ""

# Check if remote already exists
if git remote get-url origin &>/dev/null; then
    echo "Remote 'origin' already exists. Removing it..."
    git remote remove origin
fi

# Add remote
echo "Adding remote repository..."
git remote add origin "https://github.com/$USERNAME/$REPO_NAME.git"

# Push to GitHub
echo "Pushing to GitHub..."
echo ""
git push -u origin main

echo ""
echo "=========================================="
echo "Success! Repository pushed to GitHub"
echo "=========================================="
echo "View your repository at:"
echo "  https://github.com/$USERNAME/$REPO_NAME"
echo ""


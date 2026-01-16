#!/bin/bash
# SIMPLER Installation Script for Linux/CUDA Systems
# This script automates the installation of SIMPLER on a Linux system with CUDA support.

set -e  # Exit on error

echo "=========================================="
echo "SIMPLER Environment Installation Script"
echo "=========================================="
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "ERROR: This script is for Linux systems only."
    echo "SIMPLER requires Linux with CUDA support and cannot run on macOS."
    exit 1
fi

# Check for CUDA
if ! command -v nvidia-smi &> /dev/null; then
    echo "WARNING: nvidia-smi not found. CUDA may not be properly installed."
    echo "SIMPLER requires CUDA >= 11.8 and < 13."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "CUDA check: nvidia-smi found"
    nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo "Python version: $PYTHON_VERSION"

if [[ "$PYTHON_VERSION" != "3.10" && "$PYTHON_VERSION" != "3.11" ]]; then
    echo "WARNING: SIMPLER requires Python 3.10 or 3.11"
    echo "Current version: $PYTHON_VERSION"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo ""
echo "Step 1: Installing numpy==1.24.4 (required to avoid IK errors)"
echo "------------------------------------------------------------"
pip install numpy==1.24.4

echo ""
echo "Step 2: Installing ManiSkill2_real2sim"
echo "------------------------------------------------------------"
cd ManiSkill2_real2sim
pip install -e .
cd ..

echo ""
echo "Step 3: Installing SimplerEnv package"
echo "------------------------------------------------------------"
pip install -e .

echo ""
echo "Step 4: Installing optional dependencies"
echo "------------------------------------------------------------"

# Check and install meshcat
if ! python3 -c "import meshcat" 2>/dev/null; then
    echo "Installing meshcat..."
    pip install meshcat || echo "WARNING: meshcat installation failed"
else
    echo "meshcat already installed"
fi

# Check and install pybullet
if ! python3 -c "import pybullet" 2>/dev/null; then
    echo "Installing pybullet..."
    pip install pybullet || echo "WARNING: pybullet installation failed"
else
    echo "pybullet already installed"
fi

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "To verify installation, run:"
echo "  python3 -c \"import simpler_env; print('SimplerEnv imported successfully')\""
echo ""
echo "For a full test, see INSTALL_LINUX.md"


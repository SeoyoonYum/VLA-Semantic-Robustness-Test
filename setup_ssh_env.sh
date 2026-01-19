#!/bin/bash
# Quick setup script for SSH environment
# Run this after cloning the repository on your Linux/CUDA server

set -e

echo "=========================================="
echo "VLA Semantic Robustness - SSH Setup"
echo "=========================================="
echo ""

#
# Select a Python version that supports required wheels.
# numpy==1.24.4 does not have Python 3.12 wheels, so prefer 3.11 if available.
#
ROOT_DIR="$(pwd)"
PYTHON_BIN="python3"
PYTHON_VERSION="$("$PYTHON_BIN" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")"
if [ "$PYTHON_VERSION" = "3.12" ]; then
    if command -v python3.11 &> /dev/null; then
        PYTHON_BIN="python3.11"
    else
        echo "Python 3.12 detected. Installing Python 3.11 for numpy==1.24.4 compatibility..."
        if command -v apt-get &> /dev/null; then
            if command -v sudo &> /dev/null; then
                sudo apt-get update
                sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
            else
                apt-get update
                apt-get install -y python3.11 python3.11-venv python3.11-dev
            fi
            PYTHON_BIN="python3.11"
        else
            echo "ERROR: apt-get not available to install Python 3.11."
            echo "Please install Python 3.11 and rerun."
            exit 1
        fi
    fi
fi

# Ensure Python dev headers are available for building native extensions (e.g., ruckig)
if [ "$PYTHON_BIN" = "python3.11" ]; then
    if [ ! -d "/usr/include/python3.11" ]; then
        echo "Installing python3.11-dev for native extension builds..."
        if command -v apt-get &> /dev/null; then
            if command -v sudo &> /dev/null; then
                sudo apt-get update
                sudo apt-get install -y python3.11-dev
            else
                apt-get update
                apt-get install -y python3.11-dev
            fi
        else
            echo "ERROR: apt-get not available to install python3.11-dev."
            echo "Please install python3.11-dev manually, then rerun."
            exit 1
        fi
    fi
fi

# Use a local virtual environment to avoid externally-managed pip errors
VENV_DIR="$ROOT_DIR/.venv"
if [ -d "$VENV_DIR" ] && [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "Found incomplete virtual environment at $VENV_DIR. Removing..."
    rm -rf "$VENV_DIR"
fi
if [ -d "$VENV_DIR" ] && [ -f "$VENV_DIR/bin/python" ]; then
    VENV_PY_VERSION="$("$VENV_DIR/bin/python" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")"
    if [ "$VENV_PY_VERSION" != "$("$PYTHON_BIN" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")" ]; then
        echo "Existing venv uses Python $VENV_PY_VERSION, expected $("$PYTHON_BIN" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"). Recreating..."
        rm -rf "$VENV_DIR"
    fi
fi
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment in $VENV_DIR..."
    if ! "$PYTHON_BIN" -m venv "$VENV_DIR"; then
        echo "python3 venv module not available. Installing python3-venv..."
        if command -v apt-get &> /dev/null; then
            if command -v sudo &> /dev/null; then
                sudo apt-get update
                sudo apt-get install -y python3-venv python3-full
            else
                apt-get update
                apt-get install -y python3-venv python3-full
            fi
            echo "Recreating virtual environment in $VENV_DIR..."
            "$PYTHON_BIN" -m venv "$VENV_DIR"
        else
            echo "ERROR: apt-get not available to install python3-venv."
            echo "Please install python3-venv (and python3-full) manually, then rerun."
            exit 1
        fi
    fi
fi
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "ERROR: Virtual environment was not created. Aborting."
    echo "Try: apt-get install -y python3-venv python3-full && rm -rf $VENV_DIR"
    exit 1
fi
echo "Activating virtual environment..."
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
PYTHON="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"

# Step 1: Install core dependencies
echo "Step 1: Installing core dependencies..."
"$PIP" install --upgrade pip
"$PIP" install --upgrade setuptools wheel
"$PIP" install huggingface_hub transformers accelerate bitsandbytes sentencepiece tqdm
"$PIP" install numpy==1.24.4  # Required for SIMPLER

# Step 2: Install PyTorch with CUDA support
echo ""
echo "Step 2: Installing PyTorch with CUDA support..."
"$PIP" install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Step 3: Download model weights
echo ""
echo "Step 3: Downloading OpenVLA-7B model weights (~15GB)..."
echo "This may take a while depending on your connection speed."
"$PYTHON" download_model.py

# Step 4: Install SIMPLER environment
echo ""
echo "Step 4: Installing SIMPLER environment..."
cd SimplerEnv

# Install ManiSkill2_real2sim
echo "  Installing ManiSkill2_real2sim..."
cd ManiSkill2_real2sim
"$PIP" install -e .
cd ..

# Install SimplerEnv
echo "  Installing SimplerEnv..."
"$PIP" install -e .
cd ..

# Step 5: Install additional dependencies
echo ""
echo "Step 5: Installing additional dependencies..."
"$PIP" install timm pandas matplotlib seaborn scipy pyyaml

# Step 6: Create required directories
echo ""
echo "Step 6: Creating required directories..."
mkdir -p data/results
mkdir -p data/logs
touch data/results/.gitkeep
touch data/logs/.gitkeep

# Step 7: Verify installation
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Verifying installation..."

# Check GPU
echo "Checking GPU..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
else
    echo "WARNING: nvidia-smi not found. GPU may not be available."
fi

# Check PyTorch
echo ""
echo "Checking PyTorch and CUDA..."
$PYTHON -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'GPU count: {torch.cuda.device_count()}')
    print(f'GPU name: {torch.cuda.get_device_name(0)}')
"

# Check model weights
echo ""
echo "Checking model weights..."
if [ -d "weights" ] && [ -f "weights/config.json" ]; then
    echo "✓ Model weights directory exists"
    WEIGHT_COUNT=$(find weights -name "*.safetensors" | wc -l)
    echo "  Found $WEIGHT_COUNT safetensors files"
else
    echo "✗ Model weights not found. Run: python download_model.py"
fi

echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo "1. Review RESEARCH_MANIFESTO.md"
echo "2. Start implementing experiment modules"
echo "3. Run a test trial to verify everything works"
echo ""
echo "For troubleshooting, see SSH_SETUP_GUIDE.md"


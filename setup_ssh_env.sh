#!/bin/bash
# Quick setup script for SSH environment
# Run this after cloning the repository on your Linux/CUDA server

set -e

echo "=========================================="
echo "VLA Semantic Robustness - SSH Setup"
echo "=========================================="
echo ""

# Step 1: Install core dependencies
echo "Step 1: Installing core dependencies..."
pip install --upgrade pip
pip install huggingface_hub transformers accelerate bitsandbytes sentencepiece tqdm
pip install numpy==1.24.4  # Required for SIMPLER

# Step 2: Install PyTorch with CUDA support
echo ""
echo "Step 2: Installing PyTorch with CUDA support..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Step 3: Download model weights
echo ""
echo "Step 3: Downloading OpenVLA-7B model weights (~15GB)..."
echo "This may take a while depending on your connection speed."
python download_model.py

# Step 4: Install SIMPLER environment
echo ""
echo "Step 4: Installing SIMPLER environment..."
cd SimplerEnv

# Install ManiSkill2_real2sim
echo "  Installing ManiSkill2_real2sim..."
cd ManiSkill2_real2sim
pip install -e .
cd ..

# Install SimplerEnv
echo "  Installing SimplerEnv..."
pip install -e .
cd ..

# Step 5: Install additional dependencies
echo ""
echo "Step 5: Installing additional dependencies..."
pip install timm pandas matplotlib seaborn scipy pyyaml

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
python3 -c "
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


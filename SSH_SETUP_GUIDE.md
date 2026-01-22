# SSH Environment Setup Guide

After cloning the repository on your SSH server, follow these steps to get everything ready.

## Step 1: Verify Repository is Cloned

```bash
cd ~/VLA-Semantic-Robustness-Test  # or wherever you cloned it
ls -la
```

You should see:
- `RESEARCH_MANIFESTO.md`
- `download_model.py`
- `SimplerEnv/`
- etc.

## Step 2: Download Model Weights

The model weights (~15GB) are not in git. Download them:

```bash
# Make sure you're in the project directory
cd ~/VLA-Semantic-Robustness-Test

# Install required dependencies first
pip3 install huggingface_hub transformers bitsandbytes torch tqdm

# Download the model
python download_model.py
```

This will:
- Download OpenVLA-7B weights to `./weights/`
- Show progress bar
- Verify the download (if timm is installed)

**Note:** If verification fails due to missing `timm`, that's okay - the download still succeeded.

## Step 3: Install SIMPLER Environment

Since you're on Linux with CUDA, you can now install SIMPLER:

```bash
cd SimplerEnv

# Install numpy first (required version)
pip install numpy==1.24

# Install ManiSkill2_real2sim
cd ManiSkill2_real2sim
pip install -e .
cd ..

# Install SimplerEnv package
pip install -e .
```

Or use the automated script:

```bash
cd SimplerEnv
bash install_linux.sh
```

## Step 4: Install Additional Dependencies

For your research project, you'll need:

```bash
# Core dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install  accelerate  sentencepiece
pip install timm  # For model verification

# Scientific stack
pip install numpy pandas matplotlib seaborn scipy

# Logging and utilities
pip install tqdm pyyaml
```

## Step 5: Verify Installation

Test that everything works:

```bash
# Test model loading
python -c "
from transformers import AutoModelForVision2Seq, BitsAndBytesConfig
import torch

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type='nf4',
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForVision2Seq.from_pretrained(
    './weights',
    device_map='auto',
    trust_remote_code=True,
    quantization_config=quant_config,
)
print('Model loaded successfully!')
"

# Test SIMPLER (if installed)
python -c "
import simpler_env
env = simpler_env.make('google_robot_pick_coke_can')
obs, reset_info = env.reset()
print('SIMPLER environment loaded successfully!')
print('Observation keys:', list(obs.keys()))
"
```

## Step 6: Check GPU and CUDA

Verify your GPU setup:

```bash
# Check GPU
nvidia-smi

# Check CUDA version
nvcc --version

# Check PyTorch can see GPU
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU count: {torch.cuda.device_count()}')"
```

## Step 7: Create Required Directories

```bash
# Create directories for results and logs
mkdir -p data/results
mkdir -p data/logs
touch data/results/.gitkeep
touch data/logs/.gitkeep
```

## Step 8: Verify Project Structure

Your directory should look like:

```
VLA-Semantic-Robustness-Test/
├── weights/                    # Model weights (downloaded)
│   ├── model-00001-of-00003.safetensors
│   ├── model-00002-of-00003.safetensors
│   ├── model-00003-of-00003.safetensors
│   └── ... (other model files)
├── SimplerEnv/                # Simulator environment
├── data/
│   ├── results/               # CSV results will go here
│   └── logs/                  # Experiment logs
├── download_model.py
├── RESEARCH_MANIFESTO.md
└── ...
```

## Troubleshooting

### Model Download Issues

If download fails:
- Check internet connection
- Verify Hugging Face token if model is gated: `export HF_TOKEN=your_token`
- Check disk space: `df -h`

### SIMPLER Installation Issues

If SAPIEN installation fails:
- Verify CUDA version: `nvidia-smi` (should show CUDA >= 11.8)
- Check GPU: `nvidia-smi` should show your GPU
- Install system dependencies if needed:
  ```bash
  sudo apt update
  sudo apt install -y cmake libglib2.0-0 libx11-6 xvfb \
       libglew-dev libjpeg-dev libboost-python-dev
  ```

### Memory Issues

If you run out of memory:
- Verify 4-bit quantization is working
- Check VRAM usage: `nvidia-smi`
- Close other processes using GPU

## Next Steps

Once everything is set up:

1. Review `RESEARCH_MANIFESTO.md` for experiment design
2. Start implementing the experiment modules:
   - `model_loader.py` - Load quantized model
   - `sim_wrapper.py` - SIMPLER interface
   - `run_experiment.py` - Main experiment orchestrator
   - `mutation_generator.py` - Instruction mutations

3. Run a test trial to verify everything works

## Quick Setup Script

Save this as `setup_ssh_env.sh` and run it:

```bash
#!/bin/bash
set -e

echo "Step 1: Installing dependencies..."
pip install huggingface_hub transformers bitsandbytes torch tqdm timm numpy==1.24.4

echo "Step 2: Downloading model weights..."
python download_model.py

echo "Step 3: Installing SIMPLER..."
cd SimplerEnv
pip install numpy==1.24.4
cd ManiSkill2_real2sim && pip install -e . && cd ..
pip install -e .
cd ..

echo "Step 4: Creating directories..."
mkdir -p data/results data/logs
touch data/results/.gitkeep data/logs/.gitkeep

echo "Setup complete! Verify with: python -c 'import torch; print(torch.cuda.is_available())'"
```


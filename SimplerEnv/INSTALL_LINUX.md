# SIMPLER Installation Guide for Linux/CUDA Systems

## Important Note

**SIMPLER requires Linux with CUDA support and cannot be installed on macOS.** This installation guide is for use on a Linux system with:
- CUDA >= 11.8 and < 13
- NVIDIA GPU (ideally RTX series)
- Python 3.10 or 3.11

## Prerequisites

1. Ensure you have CUDA installed and accessible:
   ```bash
   nvidia-smi
   ```

2. Create a conda environment (recommended):
   ```bash
   conda create -n simpler_env python=3.10  # or 3.11
   conda activate simpler_env
   ```

## Installation Steps

1. **Install numpy<2.0** (required to avoid IK errors in pinocchio):
   ```bash
   pip install numpy==1.24.4
   ```

2. **Install ManiSkill2_real2sim**:
   ```bash
   cd SimplerEnv/ManiSkill2_real2sim
   pip install -e .
   ```

3. **Install SimplerEnv package**:
   ```bash
   cd SimplerEnv
   pip install -e .
   ```

4. **Install optional dependencies** (if needed for full functionality):
   ```bash
   pip install meshcat pybullet
   ```

## Verification

Test the installation:
```python
import simpler_env
from simpler_env.utils.env.observation_utils import get_image_from_maniskill2_obs_dict

env = simpler_env.make('google_robot_pick_coke_can')
obs, reset_info = env.reset()
print("Reset successful. Observation keys:", obs.keys())
print("Instruction:", env.get_language_instruction())
```

## Full Installation (for RT-1/Octo inference)

If you need RT-1 or Octo inference capabilities, follow the additional steps in the main README.md under "Full Installation (RT-1 and Octo Inference, Env Building)".

## Troubleshooting

1. **Vulkan errors**: If you encounter Vulkan-related errors, see the troubleshooting section in the main README.md.

2. **CUDA version issues**: Ensure your CUDA version is >= 11.8 and < 13.

3. **Dependency conflicts**: The numpy==1.24.4 requirement may conflict with other packages (like tensorflow). This is expected per the SIMPLER documentation to avoid IK errors in pinocchio.


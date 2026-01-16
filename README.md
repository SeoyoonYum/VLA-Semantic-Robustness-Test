# VLA Semantic Robustness Stress Test

Research project to quantify success rate degradation in vision-language-action (VLA) models when task instructions are mutated using natural language transformations while maintaining semantic equivalence.

## Overview

This project evaluates how linguistic variations in task instructions affect the performance of OpenVLA-7B. We measure degradation in success rate when instructions are mutated using 10 different natural language transformation categories (synonyms, passive voice, spatial reordering, etc.) while maintaining semantic equivalence.

## Research Question

How do linguistic variations in task instructions affect the performance of vision-language-action models? Specifically, we aim to measure the degradation in success rate when instructions are mutated using natural language transformations while maintaining semantic equivalence.

## Project Structure

```
.
├── RESEARCH_MANIFESTO.md          # Complete project documentation
├── download_model.py               # Script to download OpenVLA-7B weights
├── SimplerEnv/                    # SIMPLER simulator environment
├── weights/                        # Model weights (not in git, too large)
└── data/                          # Results and logs
```

## Quick Start

### Prerequisites

- Python 3.10 or 3.11
- CUDA >= 11.8 and < 13 (for SIMPLER)
- NVIDIA GPU with 16GB VRAM
- Linux (required for SIMPLER, macOS not supported)

### Installation

1. **Download Model Weights:**
   ```bash
   python download_model.py
   ```

2. **Install SIMPLER Environment** (on Linux/CUDA system):
   ```bash
   cd SimplerEnv
   bash install_linux.sh
   ```
   See `SimplerEnv/INSTALL_LINUX.md` for detailed instructions.

### Usage

See `RESEARCH_MANIFESTO.md` for complete project documentation, including:
- Experiment design
- Code standards
- Success definitions
- Data management

## Key Features

- **10 Linguistic Mutation Categories**: Synonyms, passive voice, spatial reordering, formal/informal, verb phrasing, object descriptors, directional language, temporal modifiers, negation/positive, complexity variation
- **Quantitative Metrics**: Success rate and distance-to-target measurements
- **Reproducible Framework**: Standardized experimental setup for VLA robustness testing

## Model

- **Model**: OpenVLA-7B
- **Quantization**: 4-bit (bitsandbytes) - mandatory for 16GB VRAM constraint
- **Simulator**: SIMPLER (SAPIEN-based)

## Status

Active Research Project - See `RESEARCH_MANIFESTO.md` for detailed status and progress.

## License

See individual component licenses:
- SimplerEnv: See `SimplerEnv/LICENSE`
- ManiSkill2_real2sim: See `SimplerEnv/ManiSkill2_real2sim/LICENSE`

## Citation

If you use this work, please cite the relevant papers:
- SimplerEnv: See `SimplerEnv/README.md`
- OpenVLA: See model repository


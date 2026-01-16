# VLA Semantic Robustness Stress Test
## Research Manifesto - Source of Truth

**Version:** 1.0  
**Last Updated:** 2025-01-XX  
**Project Duration:** 3 Weeks  
**Status:** Active Research Project

---

## 📋 Table of Contents

1. [Project Identity](#project-identity)
2. [Technical Constraints](#technical-constraints)
3. [Experiment Design](#experiment-design)
4. [Code Standards](#code-standards)
5. [Success Definitions](#success-definitions)
6. [Project Structure](#project-structure)
7. [Data Management](#data-management)
8. [Reporting Standards](#reporting-standards)

---

## Project Identity

### Project Name
**VLA Semantic Robustness Stress Test**

### Primary Research Goal
**Quantify success rate drops when moving from template instructions to natural language mutations.**

### Research Question
How do linguistic variations in task instructions affect the performance of vision-language-action models? Specifically, we aim to measure the degradation in success rate when instructions are mutated using natural language transformations while maintaining semantic equivalence.

### Hypothesis
Natural language mutations (synonyms, passive voice, spatial rephrasing, etc.) that preserve semantic meaning will cause measurable performance degradation in VLA models, even when the underlying task remains identical.

### Expected Outcomes
1. Quantitative measurement of success rate degradation across 10 linguistic mutation categories
2. Identification of which mutation types cause the most significant performance drops
3. Baseline performance metrics for OpenVLA-7B under linguistic stress conditions
4. Reproducible experimental framework for future VLA robustness testing

---

## Technical Constraints

### Hardware Requirements
- **VRAM:** 16GB (strict limit)
- **GPU Options:**
  - Single T4 GPU (cloud)
  - Local RTX GPU (if available)
- **Memory Management:** All code must respect 16GB VRAM constraint

### Model Specifications
- **Model:** OpenVLA-7B
- **Quantization:** **4-bit (bitsandbytes) is MANDATORY**
  - No exceptions - model must fit within 16GB VRAM
  - Use `bitsandbytes` library for quantization
  - Quantization config must be consistent across all experiments

### Environment
- **Simulator:** SIMPLER Simulator
- **Environment Version:** (To be specified)
- **Task Set:** 3 distinct manipulation tasks

### Software Dependencies
- Python 3.8+ (specify exact version)
- PyTorch (compatible with quantization)
- bitsandbytes
- SIMPLER Simulator API
- Standard scientific stack (numpy, pandas, etc.)

---

## Experiment Design

### Independent Variable
**10 Linguistic Mutation Categories**

1. **Synonyms** - Replace key action verbs with synonyms
   - Example: "pick up" → "grab", "lift", "take"
   
2. **Passive Voice** - Convert active to passive voice
   - Example: "Pick up the red block" → "The red block should be picked up"
   
3. **Spatial Reordering** - Rearrange spatial descriptors
   - Example: "left side" → "on the left", "to your left"
   
4. **Formal/Informal** - Shift register (formal ↔ informal)
   - Example: "retrieve" → "grab", "obtain" → "get"
   
5. **Verb Phrasing** - Alternative verb constructions
   - Example: "move" → "transport", "relocate", "shift"
   
6. **Object Descriptors** - Vary object descriptions
   - Example: "red block" → "crimson cube", "scarlet box"
   
7. **Directional Language** - Alternative directional terms
   - Example: "toward" → "in the direction of", "closer to"
   
8. **Temporal Modifiers** - Add/remove temporal language
   - Example: "now" → "at this moment", "immediately" → "right away"
   
9. **Negation/Positive** - Restructure negative instructions positively
   - Example: "don't drop" → "keep holding", "avoid dropping"
   
10. **Complexity Variation** - Add/remove qualifiers
    - Example: "carefully place" → "place", "gently set down" → "set down"

### Dependent Variables

1. **Success Rate (SR)**
   - Binary: Success (1) or Failure (0) per episode
   - Calculated as: `SR = (Number of Successful Episodes) / (Total Episodes)`
   - Reported per mutation category and overall

2. **Distance-to-Target**
   - Continuous metric: Final distance from target object/position
   - Units: (To be specified based on SIMPLER units)
   - Reported as mean, std, min, max per condition

### Sample Size
- **3 Tasks** × **10 Mutations** × **10 Trials** = **300 total episodes**
- Each mutation category tested on all 3 tasks
- 10 independent trials per task-mutation combination
- Total runtime estimate: (To be calculated based on episode duration)

### Control Condition
- **Baseline:** Original template instructions (no mutations)
- Baseline tested with same sample size: 3 Tasks × 10 Trials = 30 episodes
- All mutations compared against baseline

### Randomization
- Trial order randomized within each task-mutation combination
- Seed management: Use fixed seeds for reproducibility, document all seeds used

---

## Code Standards

### Logging Requirements
- **MANDATORY:** Use Python `logging` module instead of `print()`
- Log levels:
  - `DEBUG`: Detailed diagnostic information
  - `INFO`: General informational messages (experiment progress)
  - `WARNING`: Warning messages (non-critical issues)
  - `ERROR`: Error messages (failures that don't stop execution)
  - `CRITICAL`: Critical errors (execution stopping)
- Log format: Include timestamp, level, module, and message
- Log to both console and file (experiment log file)

### Data Persistence
- **Auto-save CSV results after every trial**
- CSV structure:
  - Columns: `trial_id`, `task`, `mutation_category`, `mutation_text`, `success`, `distance_to_target`, `episode_length`, `timestamp`, `seed`
  - Append mode: New trials appended to existing CSV
  - Backup: Create timestamped backup before major operations
- File naming: `results_YYYYMMDD_HHMMSS.csv`

### Modular Architecture

#### Required Modules

1. **`model_loader.py`**
   - Responsibilities:
     - Load OpenVLA-7B model
     - Apply 4-bit quantization (bitsandbytes)
     - Initialize model for inference
     - Handle model caching/reloading
   - Functions:
     - `load_quantized_model(model_path, device)`
     - `get_model_config()`
     - `validate_model_loading()`

2. **`sim_wrapper.py`**
   - Responsibilities:
     - Interface with SIMPLER Simulator
     - Reset environment
     - Execute actions
     - Collect observations
     - Check termination conditions
   - Functions:
     - `initialize_simulator(config)`
     - `reset_environment(task_config)`
     - `step(action)`
     - `get_observation()`
     - `is_terminated()`
     - `get_reward()`

3. **`run_experiment.py`**
   - Responsibilities:
     - Orchestrate experiment execution
     - Manage trial loops
     - Apply mutations to instructions
     - Collect and save results
     - Handle errors gracefully
   - Functions:
     - `run_single_trial(task, mutation, seed)`
     - `run_experiment_batch(task_list, mutation_list, num_trials)`
     - `apply_mutation(instruction, mutation_category)`
     - `save_results(results, filename)`

4. **`mutation_generator.py`** (Optional but recommended)
   - Responsibilities:
     - Generate mutations for each category
     - Ensure semantic equivalence validation
     - Store mutation templates
   - Functions:
     - `generate_mutation(instruction, category)`
     - `validate_semantic_equivalence(original, mutated)`

5. **`utils.py`** (Optional but recommended)
   - Responsibilities:
     - Logging setup
     - Configuration management
     - File I/O helpers
     - Statistics calculation

### Code Quality Standards
- Type hints: Use Python type hints for all function signatures
- Docstrings: All functions must have docstrings (Google style)
- Error handling: Try-except blocks with appropriate logging
- Configuration: Use config files (YAML/JSON) for experiment parameters
- Version control: Commit frequently with descriptive messages

### Configuration Management
- Create `config.yaml` or `config.json` for:
  - Model paths
  - Simulator settings
  - Experiment parameters (tasks, mutations, trials)
  - Hardware settings (device, quantization config)
  - File paths (results directory, log directory)

---

## Success Definitions

### SIMPLER Environment Success Criteria

A trial is considered **successful** if **ALL** of the following conditions are met:

1. **Termination Condition:**
   - `is_terminated == True`
   - Episode reached natural termination (not timeout)

2. **Reward Threshold:**
   - `reward > 0`
   - Positive reward indicates task completion

3. **Task-Specific Criteria:** (To be defined per task)
   - Task 1: (Define specific success condition)
   - Task 2: (Define specific success condition)
   - Task 3: (Define specific success condition)

### Failure Conditions

A trial is considered **failed** if **ANY** of the following occur:

1. Episode timeout (max steps reached)
2. `reward <= 0`
3. `is_terminated == False` when episode ends
4. Simulator crash or error
5. Model inference error

### Edge Cases

- **Partial Success:** If reward > 0 but task not fully completed, document but count as failure
- **Timeout:** If max steps reached, record as failure with distance-to-target
- **Crashes:** Log error, record as failure, continue with next trial

### Distance-to-Target Calculation

- **Definition:** Euclidean distance (or appropriate metric) from final object/end-effector position to target position
- **Units:** Meters (or SIMPLER's native units)
- **Measurement:** Record at episode termination
- **Special Cases:**
  - If object not grasped: Distance from end-effector to target
  - If object grasped but not placed: Distance from object to target placement

---

## Project Structure

### Directory Layout

```
vla_semantic_robustness/
├── README.md
├── RESEARCH_MANIFESTO.md          # This file (Source of Truth)
├── config.yaml                    # Experiment configuration
├── requirements.txt               # Python dependencies
├── model_loader.py                # Model loading and quantization
├── sim_wrapper.py                 # SIMPLER simulator interface
├── run_experiment.py              # Main experiment orchestrator
├── mutation_generator.py          # Instruction mutation logic
├── utils.py                       # Utility functions
├── data/
│   ├── results/                   # CSV results directory
│   │   └── results_*.csv
│   ├── logs/                      # Experiment logs
│   │   └── experiment_*.log
│   └── models/                    # Model checkpoints (if needed)
├── scripts/
│   ├── analyze_results.py         # Post-experiment analysis
│   └── visualize_results.py       # Plotting and visualization
└── notebooks/
    └── exploratory_analysis.ipynb # Jupyter notebook for analysis
```

### File Naming Conventions
- Python modules: `snake_case.py`
- Results files: `results_YYYYMMDD_HHMMSS.csv`
- Log files: `experiment_YYYYMMDD_HHMMSS.log`
- Config files: `config.yaml` or `config.json`

---

## Data Management

### Results CSV Schema

| Column Name | Type | Description |
|------------|------|-------------|
| `trial_id` | int | Unique trial identifier |
| `task` | str | Task name/identifier |
| `mutation_category` | str | One of 10 mutation categories |
| `original_instruction` | str | Original template instruction |
| `mutated_instruction` | str | Mutated instruction used |
| `success` | bool | Success (True) or Failure (False) |
| `reward` | float | Final episode reward |
| `distance_to_target` | float | Final distance to target |
| `episode_length` | int | Number of steps in episode |
| `is_terminated` | bool | Whether episode terminated naturally |
| `seed` | int | Random seed used for trial |
| `timestamp` | str | ISO format timestamp |
| `notes` | str | Optional notes/errors |

### Data Backup Strategy
- Auto-backup CSV after every 10 trials
- Daily backups of entire `data/` directory
- Version control: Commit results CSV at end of each day

### Data Analysis Pipeline
1. Load results CSV
2. Calculate success rates per mutation category
3. Compute distance-to-target statistics
4. Compare against baseline
5. Generate visualizations (bar charts, box plots)
6. Statistical tests (if applicable)

---

## Reporting Standards

### Progress Tracking
- Daily progress updates
- Track: Trials completed, Success rates so far, Any issues encountered
- Update manifest with findings as they emerge

### Final Report Structure
1. **Executive Summary**
2. **Methodology** (reference this manifesto)
3. **Results**
   - Success rates by mutation category
   - Distance-to-target statistics
   - Baseline comparison
4. **Analysis**
   - Which mutations cause most degradation
   - Statistical significance tests
5. **Discussion**
   - Implications for VLA robustness
   - Limitations
6. **Conclusion**

### Visualization Requirements
- Success rate bar chart (baseline vs mutations)
- Distance-to-target box plots per mutation category
- Heatmap of success rates (Task × Mutation)
- Time series if applicable

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-01-XX | Initial manifesto creation | - |

---

## Notes and Assumptions

### Key Assumptions
1. SIMPLER Simulator API is stable and consistent
2. 4-bit quantization does not significantly alter model behavior for comparison purposes
3. 10 trials per condition provides sufficient statistical power
4. Mutations maintain semantic equivalence (to be validated)

### Known Limitations
1. Limited to 3 tasks (may not generalize)
2. Single model (OpenVLA-7B) - results may not generalize to other VLAs
3. SIMPLER environment may not reflect real-world complexity
4. 10 mutation categories may not cover all linguistic variations

### Future Extensions
- Additional mutation categories
- More tasks
- Multiple models for comparison
- Real-world robot testing
- Ablation studies on quantization impact

---

## Quick Reference Checklist

### Before Starting Experiment
- [ ] Model loaded with 4-bit quantization
- [ ] SIMPLER simulator initialized
- [ ] Logging configured
- [ ] Results CSV file created
- [ ] Config file validated
- [ ] Baseline trials completed

### During Experiment
- [ ] Logging all major events
- [ ] Auto-saving CSV after each trial
- [ ] Monitoring VRAM usage
- [ ] Tracking progress (X/300 trials)
- [ ] Error handling in place

### After Experiment
- [ ] All 300 trials completed
- [ ] Results CSV finalized
- [ ] Data analysis performed
- [ ] Visualizations generated
- [ ] Final report written
- [ ] Code and data archived

---

**This document is the Source of Truth. All code generation, experiment execution, and analysis should reference and adhere to the standards defined herein.**


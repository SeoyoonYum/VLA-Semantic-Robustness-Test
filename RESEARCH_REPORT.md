# VLA Semantic Robustness Stress Test
## A Preliminary Study of Instruction Mutations in SIMPLER

### Abstract
We evaluate semantic robustness of a vision-language-action policy on a SIMPLER
manipulation task by measuring success-rate (SR) drops under natural-language
instruction mutations. Using a single task with 20 trials per condition, we
compare baseline instructions against ten mutation categories. Results show a
substantial degradation from baseline SR (60%) to an overall mutated SR (28.2%),
with the strongest brittleness under passive voice, verb phrasing, and spatial
reordering. These findings indicate sensitivity to surface form and ordering,
motivating improved language invariance in VLA policies.

### 1. Introduction
Vision-language-action (VLA) policies are expected to generalize across natural
language phrasing. Prior work suggests that even semantically equivalent
rewordings can cause performance drops. This study quantifies such degradation
using the SIMPLER simulator and a fixed task with controlled instruction
mutations.

### 2. Research Question and Hypothesis
**RQ:** How do linguistic variations that preserve semantic meaning affect VLA
success rates?  
**Hypothesis:** Semantically equivalent instruction mutations will reduce SR
relative to the baseline template instruction.

### 3. Experimental Setup
**Simulator:** SIMPLER  
**Policy:** Octo (widowx_bridge setup)  
**Task:** `widowx_put_eggplant_in_basket`  
**Trials:** 20 seeds per condition  
**Metrics:** Success Rate (SR);  
**Mutations (10 categories):** synonyms, passive voice, spatial reordering,
formal/informal, verb phrasing, object descriptors, directional language,
temporal modifiers, negation/positive, complexity variation.

### 4. Method
We run 20 baseline trials using the environment-provided instruction and 20
trials for each mutation category. The mutation generator replaces or rephrases
key parts of the instruction while preserving intent. Results are logged per
episode to `data/results/results_octo.csv`. The analysis below reflects entries
from lines 282–502 (20 episodes per category, 220 trials total).

### 5. Results
**Success Rate by Category (20 trials each):**

- Baseline: **12/20 = 60%**
- Synonyms: **3/20 = 15%**
- Passive voice: **1/20 = 5%**
- Spatial reordering: **0/20 = 0%**
- Formal/informal: **8/20 = 40%**
- Verb phrasing: **2/20 = 10%**
- Object descriptors: **8/20 = 40%**
- Directional language: **9/20 = 45%**
- Temporal modifiers: **4/20 = 20%**
- Negation/positive: **6/20 = 30%**
- Complexity variation: **9/20 = 45%**

**Overall SR across mutations:** **62/220 = 28.2%**  
**Baseline SR:** **60%**

### 6. Interpretation
The baseline condition is moderate (60%), while most mutation categories cause
sharp drops. The policy is most robust to **directional language** and
**complexity variation** (both 45%), and moderately robust to **formal/informal**
and **object descriptors** (40%). It is highly brittle to **passive voice**,
**verb phrasing**, and **spatial reordering** (0%), indicating strong reliance
on instruction surface form and ordering rather than abstract semantics.

### 7. Discussion
The results confirm the hypothesis: semantically equivalent rewordings
significantly reduce SR. The extreme failure of spatial reordering suggests
ordering sensitivity, while passive voice failures may reflect difficulty with
non-canonical verb-object structure. These findings motivate stronger language
invariance in policy training and evaluation.

### 8. Limitations
- Single task and single policy; results may not generalize.
- SR threshold in the manifesto (>= 90% before mutations) was not met here,
  so robustness estimates may be optimistic or unstable.
- Distance-to-target metrics were unavailable in logged results.
- Fine-tuning the policy on SIMPLER and expanding to more tasks are promising
  next steps to improve baseline SR, but were not feasible in this study.

### 9. Conclusion
This study provides preliminary evidence that VLA policies can be highly
fragile to natural-language rephrasings. Even with the same visual scene and
task goal, SR drops from 60% to 28.2% across mutations, with several categories
approaching zero success. Future work should expand to multiple tasks and
policies, enforce the manifesto alignment threshold, and add richer metrics.

### 10. Reproducibility Notes
- Config: `octo_experiment_config.yaml`
- Runner: `run_octo_robustness.py`
- Mutation generator: `mutation_generator.py`
- Results: `data/results/results_octo.csv`



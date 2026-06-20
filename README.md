# Stress-Testing Semantic Robustness in Vision–Language–Action Policies

**Technical report · 2026.** An empirical probe of how the *phrasing* of an instruction
affects the success rate of a vision–language–action (VLA) policy, holding the policy
weights and the visual scene fixed.

📄 **[Read the paper (PDF)](paper.pdf)**  ·  DOI: *(add after Zenodo release — see below)*

---

## Summary

We evaluate **Octo-Small** on the SIMPLER `widowx_put_eggplant_in_basket` task under a
baseline instruction and ten programmatically generated, meaning-preserving instruction
perturbations (**11 conditions × 20 seeds = 220 episodes**). Success rate falls from
**60%** (baseline) to a **25%** mean across the perturbations.

The interpretable signal is a split between **structural** and **additive** edits:

- Genuinely reordering the sentence (`"Into yellow basket, put eggplant"`) collapses to **0%**.
- Substituting the core action verb / preposition for a near-synonym is severe (**10–15%**).
- Additive edits — descriptors, directional phrases, register, verbosity — are tolerated (**40–45%**).

This is consistent with template-matching on canonical word order rather than semantic
grounding. It is an **exploratory single-policy study, not a benchmark**. The
`passive_voice` and `negation_positive` operators are templated approximations rather than
true grammatical transformations, and their scores are **not** interpreted as evidence
about those linguistic phenomena.

## Repository layout

| Path | What it is |
|---|---|
| `paper.pdf` | The technical report. |
| `run_octo_robustness.py` | Config-driven experiment runner (baseline + mutations, calibration, logging). |
| `mutation_generator.py` | Instruction-perturbation operators (10 families). |
| `octo_experiment_config.yaml` | Task, seeds, action-scale sweep, step budget. |
| `experiment_utils.py` | Logging / CSV helpers. |
| `data/results/results_octo.csv` | Per-episode logs. |
| `SimplerEnv/` | Vendored SIMPLER environment. |

## Reproducing

Setup: Octo-Small · `widowx_bridge` · third-person camera · ≤120 steps · action scale **0.75**
(selected by a `{0.25, 0.5, 0.75, 1.0}` sweep) · sticky-gripper window 10 · fixed seeds 0–19.

```bash
python run_octo_robustness.py --config octo_experiment_config.yaml --phase all
```

The numbers in the paper correspond to the **final locked run** logged in
`data/results/results_octo.csv`. Note that this file also accumulates earlier development
runs across other tasks, so statistics computed over the whole file will differ from the
per-condition run reported in the paper.

**Requirements:** Linux, CUDA GPU, Python 3.10/3.11. See `SimplerEnv/INSTALL_LINUX.md`.

## Citation

See [`CITATION.cff`](CITATION.cff), or:

```bibtex
@techreport{yum2026vla,
  title  = {Stress-Testing Semantic Robustness in Vision--Language--Action Policies},
  author = {Yum, Seoyoon},
  year   = {2026},
  note   = {Technical report},
  doi    = {10.5281/zenodo.XXXXXXX}
}
```

*(Replace the DOI after the Zenodo release.)*

## License

- **Report (`paper.pdf`):** CC BY 4.0.
- **Code:** see component licenses (`SimplerEnv/LICENSE`, `SimplerEnv/ManiSkill2_real2sim/LICENSE`).

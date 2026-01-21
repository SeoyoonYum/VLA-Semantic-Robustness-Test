#!/usr/bin/env python
"""Run Octo baseline and mutation robustness experiments in SIMPLER."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

import numpy as np

# JAX platform is configurable via CLI; default set in main().

import simpler_env
from simpler_env.policies.octo.octo_model import OctoInference

from experiment_utils import append_csv, now_iso, setup_logger
from mutation_generator import MUTATION_CATEGORIES, generate_mutation

try:
    import yaml
except Exception:  # pragma: no cover - optional dependency
    yaml = None


DEFAULT_FIELDS = [
    "trial_id",
    "task",
    "mutation_category",
    "original_instruction",
    "mutated_instruction",
    "success",
    "distance_to_target",
    "episode_length",
    "timestamp",
    "seed",
    "notes",
]


@dataclass
class RunConfig:
    policy: str
    policy_setup: str
    tasks: List[str]
    camera: str
    max_steps: int
    action_scale: float
    heuristic_grasp_steps: int
    baseline_min_sr: float
    seeds: List[int]
    calibration_scales: List[float]
    calibration_episodes: int
    results_path: str
    log_path: str
    locked_config_path: str


def _load_config(path: str) -> Dict[str, object]:
    with open(path, "r") as f:
        if path.endswith(".json") or yaml is None:
            return json.load(f)
        return yaml.safe_load(f)


def _to_run_config(cfg: Dict[str, object]) -> RunConfig:
    return RunConfig(
        policy=cfg["policy"],
        policy_setup=cfg["policy_setup"],
        tasks=list(cfg["tasks"]),
        camera=cfg.get("camera", "3rd_view_camera"),
        max_steps=int(cfg.get("max_steps", 120)),
        action_scale=float(cfg.get("action_scale", 1.0)),
        heuristic_grasp_steps=int(cfg.get("heuristic_grasp_steps", 0)),
        baseline_min_sr=float(cfg.get("baseline_min_sr", 0.9)),
        seeds=list(cfg.get("seeds", list(range(10)))),
        calibration_scales=list(cfg.get("calibration_scales", [0.25, 0.5, 0.75, 1.0])),
        calibration_episodes=int(cfg.get("calibration_episodes", 5)),
        results_path=str(cfg.get("results_path", "data/results/results.csv")),
        log_path=str(cfg.get("log_path", "data/logs/experiment.log")),
        locked_config_path=str(cfg.get("locked_config_path", "data/logs/locked_config.json")),
    )


def _augment_ld_library_path() -> None:
    # Ensure CUDA/cuDNN libs from pip packages are visible to JAX.
    import site
    import glob

    lib_dirs: List[str] = []
    for p in site.getsitepackages():
        lib_dirs.extend(glob.glob(os.path.join(p, "nvidia", "*", "lib")))

    existing = os.environ.get("LD_LIBRARY_PATH", "")
    parts = [p for p in existing.split(":") if p]
    for d in lib_dirs:
        if d not in parts:
            parts.append(d)
    os.environ["LD_LIBRARY_PATH"] = ":".join(parts)


def _get_rgb(obs: dict, camera: str) -> np.ndarray:
    cam = obs["image"][camera]
    rgb = cam["rgb"]
    if rgb.dtype != np.uint8:
        rgb = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    return rgb


def _run_episode(
    task: str,
    instruction: str,
    seed: int,
    config: RunConfig,
    action_scale: float,
    logger,
) -> Dict[str, object]:
    env = simpler_env.make(task)
    obs, _ = env.reset(seed=seed)
    model = OctoInference(model_type=config.policy, policy_setup=config.policy_setup, init_rng=seed)
    model.reset(instruction)

    image = _get_rgb(obs, config.camera)
    steps = 0
    success = False
    distance_to_target = None
    notes = ""
    sticky_remaining = 0
    last_reward: Optional[float] = None

    for _ in range(config.max_steps):
        raw_action, action = model.step(image, instruction)
        action["world_vector"] = action["world_vector"] * action_scale
        action["rot_axangle"] = action["rot_axangle"] * action_scale

        if config.heuristic_grasp_steps > 0:
            if sticky_remaining > 0:
                action["gripper"] = np.array([-1.0])
                sticky_remaining -= 1
            elif action["gripper"][0] < -0.5:
                action["gripper"] = np.array([-1.0])
                sticky_remaining = config.heuristic_grasp_steps

        obs, reward, terminated, truncated, info = env.step(
            np.concatenate([action["world_vector"], action["rot_axangle"], action["gripper"]])
        )
        last_reward = reward
        steps += 1
        if terminated or truncated:
            success = bool(info.get("success", terminated))
            distance_to_target = info.get("distance_to_target")
            break
        image = _get_rgb(obs, config.camera)

    if distance_to_target is None:
        notes = "distance_to_target unavailable"

    return {
        "success": success,
        "distance_to_target": distance_to_target,
        "episode_length": steps,
        "reward": last_reward,
        "notes": notes,
    }


def calibrate_action_scale(task: str, config: RunConfig, logger) -> float:
    best_scale = config.action_scale
    best_sr = -1.0
    logger.info("Starting action scale calibration on %s", task)
    for scale in config.calibration_scales:
        successes = 0
        for i in range(config.calibration_episodes):
            seed = config.seeds[i % len(config.seeds)]
            env = simpler_env.make(task)
            obs, _ = env.reset(seed=seed)
            instruction = env.get_language_instruction()
            result = _run_episode(task, instruction, seed, config, scale, logger)
            if result["success"]:
                successes += 1
        sr = successes / max(1, config.calibration_episodes)
        logger.info("Scale %.3f -> SR %.2f", scale, sr)
        if sr > best_sr:
            best_sr = sr
            best_scale = scale
    logger.info("Selected action scale: %.3f (SR %.2f)", best_scale, best_sr)
    return best_scale


def run_baseline(config: RunConfig, action_scale: float, logger) -> float:
    total = 0
    successes = 0
    trial_id = 0
    for task in config.tasks:
        for seed in config.seeds:
            env = simpler_env.make(task)
            obs, _ = env.reset(seed=seed)
            instruction = env.get_language_instruction()
            result = _run_episode(task, instruction, seed, config, action_scale, logger)
            row = {
                "trial_id": trial_id,
                "task": task,
                "mutation_category": "baseline",
                "original_instruction": instruction,
                "mutated_instruction": instruction,
                "success": result["success"],
                "distance_to_target": result["distance_to_target"],
                "episode_length": result["episode_length"],
                "timestamp": now_iso(),
                "seed": seed,
                "notes": result["notes"],
            }
            append_csv(config.results_path, DEFAULT_FIELDS, row)
            successes += int(result["success"])
            total += 1
            trial_id += 1
    sr = successes / max(1, total)
    logger.info("Baseline SR %.3f (%d/%d)", sr, successes, total)
    return sr


def run_mutations(config: RunConfig, action_scale: float, logger) -> None:
    trial_id = 0
    for task in config.tasks:
        for category in MUTATION_CATEGORIES:
            for seed in config.seeds:
                env = simpler_env.make(task)
                obs, _ = env.reset(seed=seed)
                original = env.get_language_instruction()
                mutated = generate_mutation(original, category, seed)
                result = _run_episode(task, mutated, seed, config, action_scale, logger)
                row = {
                    "trial_id": trial_id,
                    "task": task,
                    "mutation_category": category,
                    "original_instruction": original,
                    "mutated_instruction": mutated,
                    "success": result["success"],
                    "distance_to_target": result["distance_to_target"],
                    "episode_length": result["episode_length"],
                    "timestamp": now_iso(),
                    "seed": seed,
                    "notes": result["notes"],
                }
                append_csv(config.results_path, DEFAULT_FIELDS, row)
                trial_id += 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="octo_experiment_config.yaml")
    parser.add_argument("--phase", choices=["align", "baseline", "mutations", "all"], default="all")
    parser.add_argument("--jax-platform", choices=["cpu", "gpu"], default="gpu")
    args = parser.parse_args()

    os.environ["JAX_PLATFORM_NAME"] = args.jax_platform
    _augment_ld_library_path()

    cfg = _load_config(args.config)
    config = _to_run_config(cfg)
    logger = setup_logger(config.log_path)

    action_scale = config.action_scale
    if args.phase in ["align", "all"]:
        action_scale = calibrate_action_scale(config.tasks[0], config, logger)
        baseline_sr = run_baseline(config, action_scale, logger)
        locked = cfg.copy()
        locked["action_scale"] = action_scale
        locked["baseline_sr"] = baseline_sr
        with open(config.locked_config_path, "w") as f:
            json.dump(locked, f, indent=2)
        if baseline_sr < config.baseline_min_sr:
            logger.warning(
                "Baseline SR %.3f < %.3f; do not proceed to mutations.",
                baseline_sr,
                config.baseline_min_sr,
            )
            return

    if args.phase in ["baseline"]:
        run_baseline(config, action_scale, logger)
    elif args.phase in ["mutations", "all"]:
        run_mutations(config, action_scale, logger)


if __name__ == "__main__":
    main()


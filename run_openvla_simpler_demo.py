#!/usr/bin/env python
"""Run OpenVLA-7B on a SIMPLER task and save a rollout video."""

from __future__ import annotations

import argparse
import os
from typing import Tuple

import imageio.v2 as imageio
import numpy as np
from PIL import Image
import torch
from transforms3d.euler import euler2axangle
from transformers import AutoModelForVision2Seq, AutoProcessor, BitsAndBytesConfig

import simpler_env


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OpenVLA-7B SIMPLER demo.")
    parser.add_argument(
        "--task",
        default="google_robot_pick_coke_can",
        choices=simpler_env.ENVIRONMENTS,
        help="SIMPLER task name.",
    )
    parser.add_argument(
        "--weights-path",
        default="/root/VLA-Semantic-Robustness-Test/weights",
        help="Path to local OpenVLA-7B weights.",
    )
    parser.add_argument(
        "--camera",
        default="overhead_camera",
        help="Camera name from obs['image'] to use.",
    )
    parser.add_argument(
        "--unnorm-key",
        default="bridge_orig",
        help="OpenVLA unnormalization key (e.g., bridge_orig).",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=200,
        help="Maximum rollout steps.",
    )
    parser.add_argument(
        "--action-scale",
        type=float,
        default=1.0,
        help="Scale factor for world/rotation actions.",
    )
    parser.add_argument(
        "--save-video",
        default="openvla_rollout.mp4",
        help="Output video path.",
    )
    return parser.parse_args()


def get_rgb(obs: dict, camera_name: str) -> np.ndarray:
    image = obs["image"][camera_name]["rgb"]
    if image.dtype != np.uint8:
        image = (np.clip(image, 0, 1) * 255).astype(np.uint8)
    return image


def action_to_env(action: np.ndarray, action_scale: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    action = np.asarray(action, dtype=np.float32).reshape(-1)
    world_vector = action[:3] * action_scale
    roll, pitch, yaw = action[3:6]
    axis, angle = euler2axangle(roll, pitch, yaw)
    rot_axangle = axis * angle * action_scale
    gripper = action[6:7]
    return world_vector, rot_axangle, gripper


def main() -> None:
    args = parse_args()
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

    # Build env
    env = simpler_env.make(args.task)
    obs, _ = env.reset()

    # Load OpenVLA
    processor = AutoProcessor.from_pretrained(args.weights_path, trust_remote_code=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )
        model = AutoModelForVision2Seq.from_pretrained(
            args.weights_path,
            trust_remote_code=True,
            quantization_config=bnb_config,
            device_map="auto",
            low_cpu_mem_usage=True,
        )
    else:
        model = AutoModelForVision2Seq.from_pretrained(
            args.weights_path,
            trust_remote_code=True,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
        ).to(device)
    model.eval()

    instruction = env.get_language_instruction()
    frames = []

    for step_idx in range(args.max_steps):
        rgb = get_rgb(obs, args.camera)
        frames.append(rgb)
        image = Image.fromarray(rgb)
        prompt = f"In: What action should the robot take to {instruction}?\nOut:"

        inputs = processor(prompt, image, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.inference_mode():
            action = model.predict_action(
                **inputs,
                unnorm_key=args.unnorm_key,
                do_sample=False,
            )

        if isinstance(action, torch.Tensor):
            action = action.detach().cpu().numpy()
        world_vector, rot_axangle, gripper = action_to_env(action, args.action_scale)

        obs, reward, terminated, truncated, info = env.step(
            np.concatenate([world_vector, rot_axangle, gripper])
        )

        if terminated or truncated:
            break

    imageio.mimsave(args.save_video, frames, fps=20)
    print(f"Saved {args.save_video}")


if __name__ == "__main__":
    main()


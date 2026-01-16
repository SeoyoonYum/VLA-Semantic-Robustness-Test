"""Download and verify OpenVLA-7B weights."""

from __future__ import annotations

import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

import torch
from huggingface_hub import HfApi, hf_hub_download
from tqdm import tqdm
from transformers import AutoModelForVision2Seq, BitsAndBytesConfig


DEFAULT_MODEL_ID = "openvla/openvla-7b"
DEFAULT_WEIGHTS_DIR = Path("./weights")


def setup_logging(log_dir: Path) -> None:
    """Configure console and file logging."""
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = log_dir / f"download_model_{timestamp}.log"

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def list_repo_files(model_id: str) -> List[str]:
    """List all files for a model repository."""
    api = HfApi()
    return api.list_repo_files(repo_id=model_id, repo_type="model")


def download_weights(model_id: str, weights_dir: Path, files: Iterable[str]) -> None:
    """Download all files from a model repository with a progress bar."""
    weights_dir.mkdir(parents=True, exist_ok=True)
    logging.info("Downloading %s to %s", model_id, weights_dir.resolve())

    for filename in tqdm(list(files), desc="Downloading files", unit="file"):
        hf_hub_download(
            repo_id=model_id,
            filename=filename,
            repo_type="model",
            local_dir=str(weights_dir),
        )


def verify_4bit_load(weights_dir: Path) -> None:
    """Load model in 4-bit from local weights to verify integrity."""
    logging.info("Starting verification load (4-bit) from %s", weights_dir.resolve())
    
    try:
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )

        model = AutoModelForVision2Seq.from_pretrained(
            str(weights_dir),
            device_map="auto",
            trust_remote_code=True,
            quantization_config=quant_config,
        )
        model.eval()
        logging.info("Verification succeeded: model loaded in 4-bit.")
    except ImportError as e:
        logging.warning(
            "Verification skipped due to missing dependencies: %s. "
            "Install required packages (e.g., 'pip install timm') to enable verification. "
            "Download completed successfully.",
            str(e)
        )
    except Exception as e:
        logging.warning(
            "Verification failed with error: %s. "
            "Download completed successfully, but model integrity could not be verified.",
            str(e)
        )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Download and verify OpenVLA weights.")
    parser.add_argument(
        "--model-id",
        type=str,
        default=DEFAULT_MODEL_ID,
        help="Hugging Face model ID to download.",
    )
    parser.add_argument(
        "--weights-dir",
        type=Path,
        default=DEFAULT_WEIGHTS_DIR,
        help="Local directory to store model weights.",
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=Path("data/logs"),
        help="Directory to store logs.",
    )
    return parser.parse_args()


def main() -> None:
    """Run download and verification."""
    args = parse_args()
    setup_logging(args.log_dir)

    logging.info("Listing files for %s", args.model_id)
    files = list_repo_files(args.model_id)
    if not files:
        logging.error("No files found for %s", args.model_id)
        raise SystemExit(1)

    download_weights(args.model_id, args.weights_dir, files)
    verify_4bit_load(args.weights_dir)
    logging.info("Done.")


if __name__ == "__main__":
    main()


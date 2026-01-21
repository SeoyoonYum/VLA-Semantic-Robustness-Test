"""Utility helpers for experiments: logging, CSV, and timestamps."""

from __future__ import annotations

import csv
import logging
import os
from datetime import datetime
from typing import Dict, Iterable


def now_iso() -> str:
    return datetime.utcnow().isoformat()


def ensure_dir(path: str) -> None:
    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def setup_logger(log_path: str) -> logging.Logger:
    logger = logging.getLogger("robustness")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_path:
        ensure_dir(os.path.dirname(log_path))
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def append_csv(path: str, fieldnames: Iterable[str], row: Dict[str, object]) -> None:
    ensure_dir(os.path.dirname(path))
    exists = os.path.exists(path)
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerow(row)


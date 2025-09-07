#!/usr/bin/env python3
import logging
import logging.handlers
import os
from pathlib import Path

def setup_logging(log_dir: Path, level_str: str = "INFO") -> logging.Logger:
    log_dir.mkdir(exist_ok=True)
    level = getattr(logging, level_str.upper(), logging.INFO)

    logger = logging.getLogger("netauto")
    logger.setLevel(level)
    logger.propagate = False  # avoid double logs

    # Clear any existing handlers (idempotent runs)
    logger.handlers.clear()

    # File: rotate at 5MB, keep 5 files
    file_h = logging.handlers.RotatingFileHandler(
        log_dir / "app.log", maxBytes=5_000_000, backupCount=5, encoding="utf-8"
    )
    file_h.setLevel(level)
    file_h.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    ))

    # Console
    console_h = logging.StreamHandler()
    console_h.setLevel(level)
    console_h.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

    logger.addHandler(file_h)
    logger.addHandler(console_h)
    return logger

"""Logging setup for the test framework with automatic step screenshot capture."""

import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

from utils.config import ROOT_DIR, settings

_LOGGER_NAME = "kirki-ecom-tests"
_step_logger = None

# Global step logs registry for HTML reports
FRAMEWORK_STEP_LOGS = []

def setup_logging(log_dir: "Path | None" = None) -> logging.Logger:
    """Configure and return the framework logger (idempotent)."""
    global _step_logger
    if _step_logger is not None:
        return _step_logger

    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    fmt = logging.Formatter(
        "%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)
    logger.addHandler(console)

    log_dir = log_dir or (ROOT_DIR / "reports" / "logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(
        log_dir / f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log",
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    _step_logger = logger
    return logger


def get_logger() -> logging.Logger:
    if _step_logger is None:
        return setup_logging()
    return _step_logger


def log_step(message: str, driver=None) -> None:
    """Record a named step and optionally capture a step screenshot."""
    get_logger().info("STEP | %s", message)
    
    screenshot_rel_path = None
    if driver is not None:
        try:
            screenshots_dir = ROOT_DIR / "reports" / "screenshots"
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            slug = re.sub(r'[^a-zA-Z0-9_]', '_', message.lower())[:30]
            filename = f"step_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:20]}_{slug}.png"
            full_path = screenshots_dir / filename
            driver.save_screenshot(str(full_path))
            screenshot_rel_path = f"screenshots/{filename}"
        except Exception as e:
            get_logger().debug(f"Failed to capture step screenshot: {e}")

    FRAMEWORK_STEP_LOGS.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "step": message,
        "screenshot": screenshot_rel_path
    })


def log_debug(message: str) -> None:
    get_logger().debug(message)


def log_warning(message: str) -> None:
    get_logger().warning(message)


logger = get_logger()

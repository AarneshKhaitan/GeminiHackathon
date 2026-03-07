"""
Logging configuration for IHEE backend.

Basic logging to track investigation progress:
- Cycle start/end
- Hypothesis generation/elimination
- Evidence gathering
- Token usage
- API calls and errors
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(name: str = "ihee", level: int = logging.INFO, log_to_file: bool = True) -> logging.Logger:
    """
    Set up a logger with console and optional file output.

    Args:
        name: Logger name
        level: Logging level (default: INFO)
        log_to_file: Whether to write logs to file (default: True)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler with simple format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler with detailed format
    if log_to_file:
        logs_dir = Path(__file__).parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"investigation_{timestamp}.log"

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-7s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        logger.info(f"Logging to: {log_file}")

    return logger


def get_logger(name: str = "ihee") -> logging.Logger:
    """Get existing logger or create new one if doesn't exist."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger

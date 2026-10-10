"""Logging setup: rotating file handler plus console output."""
import logging
import os
from logging.handlers import RotatingFileHandler

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def setup_logging(log_file: str = "logs/app.log", level: str = "INFO") -> logging.Logger:
    """Configure and return the application's root logger."""
    os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
    logger = logging.getLogger("sis")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:  # avoid duplicate handlers on re-import
        formatter = logging.Formatter(LOG_FORMAT)

        file_handler = RotatingFileHandler(
            log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console shows warnings and above so the menu stays readable.
        console = logging.StreamHandler()
        console.setLevel(logging.WARNING)
        console.setFormatter(formatter)
        logger.addHandler(console)
    return logger

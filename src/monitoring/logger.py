"""Logging configuration for the credit scoring API."""

import sys
from pathlib import Path
from loguru import logger

# Log directory
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def setup_logger():
    """Configure loguru logger with file and console outputs."""

    # Remove default handler
    logger.remove()

    # Console handler - INFO level
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )

    # File handler - All logs (DEBUG+)
    logger.add(
        LOG_DIR / "app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="30 days",
        compression="gz"
    )

    # File handler - Errors only
    logger.add(
        LOG_DIR / "error.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="10 MB",
        retention="30 days",
        compression="gz"
    )

    # File handler - Predictions audit log (JSON format for easy parsing)
    logger.add(
        LOG_DIR / "predictions.log",
        format="{message}",
        level="INFO",
        filter=lambda record: "PREDICTION" in record["message"],
        rotation="50 MB",
        retention="90 days"
    )

    logger.info("Logger initialized")
    return logger


def get_logger():
    """Get the configured logger instance."""
    return logger


# Initialize logger on module import
setup_logger()

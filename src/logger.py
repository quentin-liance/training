"""Logger configuration using loguru."""

import sys
from pathlib import Path

from loguru import logger

# Remove default handler
logger.remove()

# Console handler with colors and simplified format
logger.add(
    sys.stderr,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan> - "
        "<level>{message}</level>"
    ),
    level="INFO",
    colorize=True,
)

# File handler with detailed format
logs_dir = Path(__file__).parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

logger.add(
    logs_dir / "app_{time:YYYY-MM-DD}.log",
    rotation="500 MB",
    retention="10 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
)

logger.info("Logger initialized successfully")

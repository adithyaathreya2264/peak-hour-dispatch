import logging
import sys
from loguru import logger
from app.core.config import settings


# Remove default logger
logger.remove()

# Add custom logger with format
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG" if settings.ENVIRONMENT == "development" else "INFO",
    colorize=True,
)

# Add file logger
logger.add(
    "logs/app.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
)


def get_logger(name: str):
    """Get a logger instance with the specified name"""
    return logger.bind(name=name)

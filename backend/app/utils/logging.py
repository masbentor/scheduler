import logging
import sys
from typing import Any, Dict

# Configure logging format
log_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_format)

# Create file handler
file_handler = logging.FileHandler('app.log')
file_handler.setFormatter(log_format)

# Create logger
logger = logging.getLogger('scheduler')
logger.setLevel(logging.INFO)

# Add handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Helper functions for structured logging
def log_info(message: str, extra: Dict[str, Any] = None) -> None:
    """Log info message with optional extra fields"""
    logger.info(message, extra=extra or {})

def log_error(message: str, extra: Dict[str, Any] = None) -> None:
    """Log error message with optional extra fields"""
    logger.error(message, extra=extra or {})

def log_warning(message: str, extra: Dict[str, Any] = None) -> None:
    """Log warning message with optional extra fields"""
    logger.warning(message, extra=extra or {})
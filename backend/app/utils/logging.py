import logging
import sys
from typing import Optional
from pathlib import Path
from datetime import datetime

def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """Set up a logger with console and file handlers
    
    Args:
        name: Name of the logger
        level: Logging level
        log_file: Optional path to log file. If None, uses default path.
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create detailed formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler - only INFO and above
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Default log file if none specified
    if log_file is None:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        date_str = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"{name}_{date_str}.log"
    
    # File handler - captures everything
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)  # Capture all levels in file
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Prevent propagation to avoid duplicate logs
    logger.propagate = False
    
    return logger

# Create default application logger
logger = setup_logger('scheduler', level=logging.DEBUG)  # Set to DEBUG level by default

# Add a function to get logger for specific modules
def get_module_logger(module_name: str) -> logging.Logger:
    """Get a logger for a specific module
    
    Args:
        module_name: Name of the module requesting the logger
        
    Returns:
        Logger instance configured for the module
    """
    return setup_logger(f'scheduler.{module_name}') 
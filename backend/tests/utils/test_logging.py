import pytest
import logging
from pathlib import Path
from datetime import datetime
from app.utils.logging import setup_logger, get_module_logger

def test_setup_logger_with_default_config():
    """Test logger setup with default configuration"""
    logger = setup_logger('test_logger')
    
    # Check logger level
    assert logger.level == logging.INFO
    
    # Check handlers
    assert len(logger.handlers) == 2  # Console and file handler
    
    # Check console handler
    console_handler = next(h for h in logger.handlers if isinstance(h, logging.StreamHandler))
    assert console_handler.level == logging.INFO
    
    # Check file handler
    file_handler = next(h for h in logger.handlers if isinstance(h, logging.FileHandler))
    assert file_handler.level == logging.DEBUG
    
    # Check log file creation
    log_dir = Path("logs")
    assert log_dir.exists()
    date_str = datetime.now().strftime("%Y%m%d")
    expected_log_file = log_dir / f"test_logger_{date_str}.log"
    assert expected_log_file.exists()

def test_setup_logger_with_custom_config():
    """Test logger setup with custom configuration"""
    test_log_file = Path("logs/custom_test.log")
    logger = setup_logger('custom_test', level=logging.DEBUG, log_file=test_log_file)
    
    # Check logger level
    assert logger.level == logging.DEBUG
    
    # Check handlers
    assert len(logger.handlers) == 2
    
    # Check file handler uses custom file
    file_handler = next(h for h in logger.handlers if isinstance(h, logging.FileHandler))
    assert Path(file_handler.baseFilename) == test_log_file.absolute()

def test_get_module_logger():
    """Test getting a module-specific logger"""
    module_name = "test_module"
    logger = get_module_logger(module_name)
    
    # Check logger name
    assert logger.name == f"scheduler.{module_name}"
    
    # Check handlers are properly configured
    assert len(logger.handlers) == 2
    
    # Verify log file naming
    file_handler = next(h for h in logger.handlers if isinstance(h, logging.FileHandler))
    date_str = datetime.now().strftime("%Y%m%d")
    expected_name = f"scheduler.{module_name}_{date_str}.log"
    assert Path(file_handler.baseFilename).name == expected_name

def test_logger_formatting():
    """Test logger message formatting"""
    logger = setup_logger('format_test')
    
    # Get file handler
    file_handler = next(h for h in logger.handlers if isinstance(h, logging.FileHandler))
    log_file = Path(file_handler.baseFilename)
    
    # Log a test message
    test_message = "Test log message"
    logger.info(test_message)
    
    # Read the log file
    log_content = log_file.read_text()
    
    # Check format components
    assert test_message in log_content
    assert "format_test" in log_content  # Logger name
    assert "INFO" in log_content  # Log level
    assert "[test_logging.py:" in log_content  # File name and line number

@pytest.fixture(autouse=True)
def cleanup_logs():
    """Clean up log files after each test"""
    yield
    # Clean up test log files
    log_dir = Path("logs")
    if log_dir.exists():
        for log_file in log_dir.glob("test_*.log"):
            log_file.unlink()
        for log_file in log_dir.glob("custom_*.log"):
            log_file.unlink()
        for log_file in log_dir.glob("format_*.log"):
            log_file.unlink()
        # Remove directory if empty
        if not any(log_dir.iterdir()):
            log_dir.rmdir() 
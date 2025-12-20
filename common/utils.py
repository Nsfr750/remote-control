"""
Common utility functions for the remote control application.
"""
import logging
import sys
from pathlib import Path
from typing import Optional

def setup_logger(name: str, log_file: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with both console and file handlers.
    
    Args:
        name: Name of the logger
        log_file: Path to the log file (optional)
        level: Logging level (default: logging.INFO)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if log file is specified
    if log_file:
        # Create log directory if it doesn't exist
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path to the project root directory
    """
    return Path(__file__).parent.parent

def validate_ip_address(ip: str) -> bool:
    """
    Validate an IP address.
    
    Args:
        ip: IP address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    import socket
    try:
        socket.inet_pton(socket.AF_INET, ip)
        return True
    except socket.error:
        try:
            socket.inet_pton(socket.AF_INET6, ip)
            return True
        except socket.error:
            return False

def validate_port(port: int) -> bool:
    """
    Validate a port number.
    
    Args:
        port: Port number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return 1 <= port <= 65535

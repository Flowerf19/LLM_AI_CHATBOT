"""
Utility helper functions
"""
import logging
from typing import Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (usually __name__ from calling module)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name or __name__)

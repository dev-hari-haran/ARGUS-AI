"""
Centralized logging utility.
"""
import logging
from src.utils.config_loader import load_config

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger instance.
    
    Args:
        name: The name of the logger (usually __name__).
        
    Returns:
        A configured logging.Logger object.
    """
    try:
        config = load_config('logging')
        level_str = config.get('level', 'INFO')
        fmt = config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        date_fmt = config.get('date_format', '%Y-%m-%d %H:%M:%S')
    except Exception:
        # Fallback if config loading fails
        level_str = 'INFO'
        fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        date_fmt = '%Y-%m-%d %H:%M:%S'
        
    level = getattr(logging, level_str.upper(), logging.INFO)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=date_fmt))
        logger.addHandler(handler)
        
    return logger

"""
Typed config loader with validation.
"""
import yaml
from pathlib import Path
from typing import Dict, Any

from src.utils.paths import CONFIG_DIR

def load_config(config_name: str) -> Dict[str, Any]:
    """
    Loads a YAML configuration file from the configs directory.
    
    Args:
        config_name: Name of the config file (e.g., 'robot.yaml' or 'robot').
        
    Returns:
        Dictionary containing the configuration.
    """
    if not config_name.endswith('.yaml'):
        config_name += '.yaml'
        
    config_path = CONFIG_DIR / config_name
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        
    return config or {}

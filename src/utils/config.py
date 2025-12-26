"""Configuration loader and merger."""

import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_name: str) -> Dict[str, Any]:
    """
    Load configuration from config directory.
    
    Args:
        config_name: Name like 'default', 'fast_preview', or path to YAML
    
    Returns:
        Configuration dictionary
    """
    if Path(config_name).exists():
        config_path = Path(config_name)
    else:
        config_path = Path(__file__).parent.parent.parent / "config" / f"{config_name}.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    
    with open(config_path) as f:
        return yaml.safe_load(f)


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge override into base config.
    
    Args:
        base: Base configuration
        override: Override configuration
    
    Returns:
        Merged configuration
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result

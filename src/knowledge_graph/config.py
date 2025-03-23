"""Configuration utilities for the knowledge graph generator."""
import tomli
import os

def load_config(config_file="config.toml"):
    """
    Load configuration from TOML file.
    
    Args:
        config_file: Path to the TOML configuration file
        
    Returns:
        Dictionary containing the configuration or None if loading fails
    """
    try:
        with open(config_file, "rb") as f:
            return tomli.load(f)
    except Exception as e:
        print(f"Error loading config file: {e}")
        return None 
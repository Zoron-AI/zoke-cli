"""Configuration management for zoke CLI."""

import json
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".config" / "zoke"
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_config_path() -> Path:
    """Return the path to the config file."""
    return CONFIG_FILE


def load_config() -> dict:
    """Load configuration from file."""
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE) as f:
        return json.load(f)


def save_config(config: dict) -> None:
    """Save configuration to file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_api_key() -> Optional[str]:
    """Get the OpenAI API key from config."""
    config = load_config()
    return config.get("openai_api_key")


def set_api_key(key: str) -> None:
    """Set the OpenAI API key in config."""
    config = load_config()
    config["openai_api_key"] = key
    save_config(config)

"""Configuration management.

Settings come from config/config.json and can be overridden with
environment variables, which is how cloud platforms (Docker, Heroku,
Azure, AWS, etc.) usually inject configuration.

Environment overrides:
    SIS_DATA_FILE, SIS_LOG_FILE, SIS_LOG_LEVEL
"""
import json
import os

from src.utils.exceptions import StudentError

DEFAULTS = {
    "app_name": "Student Information System",
    "data_file": "data/students.json",
    "log_file": "logs/app.log",
    "log_level": "INFO",
}

ENV_OVERRIDES = {
    "SIS_DATA_FILE": "data_file",
    "SIS_LOG_FILE": "log_file",
    "SIS_LOG_LEVEL": "log_level",
}


def load_config(path: str = "config/config.json") -> dict:
    """Load configuration, falling back to defaults if the file is missing."""
    config = dict(DEFAULTS)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                config.update(json.load(f))
        except (json.JSONDecodeError, OSError) as exc:
            raise StudentError(f"Invalid configuration file '{path}': {exc}") from exc

    for env_name, key in ENV_OVERRIDES.items():
        if os.environ.get(env_name):
            config[key] = os.environ[env_name]
    return config

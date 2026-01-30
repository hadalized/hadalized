"""XDG base directories the application uses."""

from pathlib import Path  # required for pydantic

import xdg_base_dirs

from hadalized.const import APP_NAME

APP_DIR = Path(APP_NAME)


def config() -> Path:
    """Application configuration home.

    Returns:
        The application configuration home directory.

    """
    return xdg_base_dirs.xdg_config_home() / APP_DIR


def cache() -> Path:
    """Application cache home.

    Returns:
        The application configuration home directory.

    """
    return xdg_base_dirs.xdg_cache_home() / APP_DIR


def state() -> Path:
    """Application state home.

    Returns:
        The application configuration home directory.

    """
    return xdg_base_dirs.xdg_state_home() / APP_DIR


def data() -> Path:
    """Application data home.

    Returns:
        The application configuration home directory.

    """
    return xdg_base_dirs.xdg_data_home() / APP_DIR


def template() -> Path:
    """Application config templates home.

    Returns:
        The application configuration home directory.

    """
    return config() / "templates"


def build() -> Path:
    """Application home for built themes.

    Returns:
        The application configuration home directory.

    """
    return state() / "build"

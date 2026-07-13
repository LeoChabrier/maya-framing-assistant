"""Config loader for data-driven presets (render formats, focal lenses).

Reads JSON files from the package ``config/`` directory. If a file is missing
or malformed, falls back to baked-in defaults so the tool always launches.
"""

import json

from .paths import Paths


# Fallbacks used when a config file is missing or cannot be parsed.
DEFAULT_RENDER_FORMATS = [
    {'name': 'HD', 'label': 'HD 1.77 (1920x1080)',
     'width': 1920, 'height': 1080, 'aspect_ratio': 1.778},
    {'name': 'Flat', 'label': 'FLAT 1.85 (1998x1080)',
     'width': 1998, 'height': 1080, 'aspect_ratio': 1.850},
    {'name': 'Scope', 'label': 'SCOPE 2.39 (2048x858)',
     'width': 2048, 'height': 858, 'aspect_ratio': 2.387},
]

DEFAULT_FOCAL_CATEGORIES = [
    {'name': 'Wide Angle', 'focals': [12, 24]},
    {'name': 'Standard', 'focals': [35, 50]},
    {'name': 'Telephoto', 'focals': [85, 100, 135, 150, 175, 200]},
]


class Config:
    """Loads preset data from the ``config/`` directory."""

    @staticmethod
    def _load(filename, key, default):
        """Load ``key`` from a JSON config file, or return ``default``.

        Args:
            filename: Config filename inside the config directory.
            key: Top-level key holding the list to return.
            default: Fallback value if the file is missing/invalid.

        Returns:
            The parsed list, or ``default`` on any error.
        """
        path = Paths.config_file(filename)
        try:
            with open(path, 'r', encoding='utf-8') as handle:
                data = json.load(handle)
            value = data.get(key)
            if isinstance(value, list) and value:
                return value
        except (OSError, ValueError) as exc:
            print(f"[FramingAssistant] Could not load {filename}: {exc}. "
                  "Using built-in defaults.")
        return default

    @classmethod
    def render_formats(cls):
        """Return the list of render format dicts.

        Returns:
            list[dict]: Each with name, label, width, height, aspect_ratio.
        """
        return cls._load('render_formats.json', 'formats', DEFAULT_RENDER_FORMATS)

    @classmethod
    def focal_categories(cls):
        """Return focal presets grouped by category.

        Returns:
            list[dict]: Each with 'name' and a 'focals' list of values.
        """
        return cls._load('focal_presets.json', 'categories', DEFAULT_FOCAL_CATEGORIES)

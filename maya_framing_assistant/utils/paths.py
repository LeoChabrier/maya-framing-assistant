"""Path utilities for Maya Framing Assistant."""

import os


class Paths:
    """Centralized path management for the application."""

    _root = None

    @classmethod
    def set_root(cls, root_path):
        """Set the root directory of the application.

        Args:
            root_path: Absolute path to the application root directory.
        """
        cls._root = root_path

    @classmethod
    def root(cls):
        """Get the root directory path.

        Returns:
            str: Root directory path.
        """
        if cls._root is None:
            # Fallback: use the parent of this file's directory
            cls._root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return cls._root

    @classmethod
    def pictures(cls):
        """Get the pictures directory path.

        Returns:
            str: Pictures directory path.
        """
        return os.path.join(cls.root(), "images", "pictures")

    @classmethod
    def gui(cls):
        """Get the GUI directory path.

        Returns:
            str: GUI directory path.
        """
        return os.path.join(cls.root(), "gui")

    @classmethod
    def ui_file(cls, name="mainWindow.ui"):
        """Get path to a UI file.

        Args:
            name: UI filename (default: mainWindow.ui).

        Returns:
            str: Full path to the UI file.
        """
        return os.path.join(cls.gui(), name)

    @classmethod
    def picture(cls, name):
        """Get path to a picture file.

        Args:
            name: Picture name (with or without .png extension).

        Returns:
            str: Full path to the picture file.
        """
        if not name.endswith(".png"):
            name = f"{name}.png"
        return os.path.join(cls.pictures(), name)

    @classmethod
    def list_pictures(cls):
        """List all available framing overlay pictures.

        Returns:
            list: List of picture names (without extension).
        """
        pictures_dir = cls.pictures()
        if not os.path.exists(pictures_dir):
            return []

        return [
            os.path.splitext(f)[0]
            for f in os.listdir(pictures_dir)
            if f.endswith(".png")
        ]

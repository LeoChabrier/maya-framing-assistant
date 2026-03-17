"""
Maya Framing Assistant - Entry Point

A framing helper for Maya that allows you to easily create an image plane
with framing overlays and set it up with the right settings.

Features:
- Framing overlay image planes (Rule of Thirds, Golden Ratio, etc.)
- Tumble tool, pan/zoom controls
- Focal length presets
- Render format presets (HD, Flat, Scope)

Author: Christophe Moreau (moreau.vfx@gmail.com)
Version: 2.0.0
"""
# -*- coding: utf-8 -*-

# Built-in
import os
import sys

# Ensure the package root is in sys.path
PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))
if PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, PACKAGE_ROOT)

# Third-party
from maya import cmds

# Internal
from core import CameraService
from gui import MainWindow
from utils import Paths


def main():
    """Launch the Maya Framing Assistant window."""
    # Set the root path for the Paths utility
    Paths.set_root(PACKAGE_ROOT)

    # Create the main window
    window = MainWindow()

    # Check for user cameras
    cameras = CameraService.get_user_cameras()

    if cameras:
        window.update_camera_list()
    else:
        # Prompt user to create a camera
        result = cmds.confirmDialog(
            title='Warning',
            message='There is no user Camera in the scene, please create one.',
            button=['Ok', 'Create Camera'],
            defaultButton='Ok',
            cancelButton='Ok',
            dismissString='Ok'
        )

        if result == 'Create Camera':
            CameraService.create_camera()
            window.ui.pushColor.setStyleSheet('background-color:rgb(255,255,255)')
            window.update_camera_list()

    window.show()
    return window


if __name__ == '__main__':
    main()

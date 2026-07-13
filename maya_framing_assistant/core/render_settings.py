"""Render settings service for Maya.

Render format presets are data-driven (see ``config/render_formats.json``,
loaded via ``utils.Config``); this module only applies/detects them.
"""

from maya import cmds


class RenderSettings:
    """Service class for Maya render settings operations."""

    @staticmethod
    def get_resolution():
        """Get current render resolution.

        Returns:
            tuple: (width, height).
        """
        width = cmds.getAttr("defaultResolution.width")
        height = cmds.getAttr("defaultResolution.height")
        return width, height

    @staticmethod
    def set_resolution(width, height, aspect_ratio=None):
        """Set render resolution.

        Args:
            width: Resolution width in pixels.
            height: Resolution height in pixels.
            aspect_ratio: Optional device aspect ratio. If None, calculated from width/height.
        """
        cmds.setAttr("defaultResolution.width", width)
        cmds.setAttr("defaultResolution.height", height)

        if aspect_ratio is None:
            aspect_ratio = width / height
        cmds.setAttr("defaultResolution.deviceAspectRatio", aspect_ratio)

    @staticmethod
    def get_aspect_ratio():
        """Get current device aspect ratio.

        Returns:
            float: Device aspect ratio.
        """
        return cmds.getAttr("defaultResolution.deviceAspectRatio")

    @staticmethod
    def apply_format(render_format):
        """Apply a render format preset.

        Args:
            render_format: A render format dict (width, height, aspect_ratio).
        """
        RenderSettings.set_resolution(
            render_format['width'],
            render_format['height'],
            render_format['aspect_ratio']
        )

    @staticmethod
    def detect_current_format(formats):
        """Detect which configured format matches current settings.

        Args:
            formats: List of render format dicts (name, width, height, ...).

        Returns:
            str or None: Matching format name, or None if none matches.
        """
        width, height = RenderSettings.get_resolution()

        for fmt in formats:
            if fmt.get('width') == width and fmt.get('height') == height:
                return fmt.get('name')

        return None

    @staticmethod
    def calculate_fit_to_resolution_gate(camera, width=None, height=None):
        """Calculate the size needed to fit an image plane to resolution gate.

        Args:
            camera: Camera transform name.
            width: Resolution width (uses current settings if None).
            height: Resolution height (uses current settings if None).

        Returns:
            float: Vertical size for the image plane.
        """
        if width is None or height is None:
            width, height = RenderSettings.get_resolution()

        h_aperture = cmds.getAttr(f"{camera}.horizontalFilmAperture")
        return (height * h_aperture) / width

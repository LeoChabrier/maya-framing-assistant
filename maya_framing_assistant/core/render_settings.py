"""Render settings service for Maya."""

from maya import cmds


class RenderFormat:
    """Standard render format presets."""

    HD = {
        'name': 'HD',
        'width': 1920,
        'height': 1080,
        'aspect_ratio': 1.778
    }

    FLAT = {
        'name': 'Flat',
        'width': 1998,
        'height': 1080,
        'aspect_ratio': 1.850
    }

    SCOPE = {
        'name': 'Scope',
        'width': 2048,
        'height': 858,
        'aspect_ratio': 2.387
    }


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
            render_format: A RenderFormat preset dictionary.
        """
        RenderSettings.set_resolution(
            render_format['width'],
            render_format['height'],
            render_format['aspect_ratio']
        )

    @staticmethod
    def detect_current_format():
        """Detect which standard format matches current settings.

        Returns:
            str or None: Format name ('HD', 'Flat', 'Scope') or None if custom.
        """
        width, height = RenderSettings.get_resolution()

        if width == 1920 and height == 1080:
            return 'HD'
        elif width == 1998 and height == 1080:
            return 'Flat'
        elif width == 2048 and height == 858:
            return 'Scope'

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

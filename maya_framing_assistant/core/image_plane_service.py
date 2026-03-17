"""Image plane operations service for Maya."""

import os
from maya import cmds


def clip(value, lower, upper):
    """Clamp a value between lower and upper bounds.

    Args:
        value: Value to clamp.
        lower: Lower bound.
        upper: Upper bound.

    Returns:
        Clamped value.
    """
    return lower if value < lower else upper if value > upper else value


class ImagePlaneService:
    """Service class for all Maya image plane operations."""

    @staticmethod
    def get_image_plane(camera_shape):
        """Get the image plane attached to a camera.

        Args:
            camera_shape: Camera shape name.

        Returns:
            str or None: Image plane transform name, or None if not found.
        """
        image_planes = cmds.listRelatives(
            camera_shape, type='imagePlane', ad=True, c=True
        )
        if image_planes:
            transforms = cmds.listRelatives(image_planes, parent=True)
            return transforms[0] if transforms else None
        return None

    @staticmethod
    def get_image_plane_shape(image_plane):
        """Get the shape node of an image plane.

        Args:
            image_plane: Image plane transform name.

        Returns:
            str: Image plane shape name.
        """
        shapes = cmds.listRelatives(image_plane, ad=False, s=True)
        return shapes[0] if shapes else None

    @staticmethod
    def create(camera, image_path):
        """Create an image plane for a camera.

        Args:
            camera: Camera transform name.
            image_path: Full path to the image file.

        Returns:
            str: Image plane shape name.
        """
        cmds.imagePlane(
            camera=camera,
            showInAllViews=False,
            fileName=image_path
        )
        shape = cmds.listRelatives(ad=False, s=True)[0]
        return shape

    @staticmethod
    def delete(camera):
        """Delete all image planes attached to a camera.

        Args:
            camera: Camera transform name.
        """
        cmds.select(camera, r=True)
        shapes = cmds.listRelatives(ad=False, s=True)
        if shapes:
            image_planes = cmds.listRelatives(shapes, ad=True, pa=True)
            if image_planes:
                cmds.delete(image_planes)
        cmds.select(clear=True)

    @staticmethod
    def setup_defaults(image_plane_shape, camera_shape, color_rgb=(1, 1, 1), alpha=1.0):
        """Apply default settings to an image plane.

        Args:
            image_plane_shape: Image plane shape name.
            camera_shape: Camera shape name (to get near clip).
            color_rgb: Tuple of (r, g, b) color values (0-1 range).
            alpha: Alpha gain value (0-1 range).
        """
        # Get camera near clip to position image plane
        near_clip = cmds.getAttr(f"{camera_shape}.nearClipPlane")
        depth_value = abs(near_clip * 1.1)

        # Apply settings
        cmds.setAttr(f"{image_plane_shape}.depth", depth_value)
        cmds.setAttr(f"{image_plane_shape}.textureFilter", 1)
        cmds.setAttr(f"{image_plane_shape}.fit", 3)  # Vertical fit
        cmds.setAttr(
            f"{image_plane_shape}.colorGain",
            color_rgb[0], color_rgb[1], color_rgb[2],
            type="double3"
        )
        cmds.setAttr(f"{image_plane_shape}.alphaGain", alpha)
        cmds.setAttr(f"{image_plane_shape}.overrideEnabled", 1)
        cmds.setAttr(f"{image_plane_shape}.overrideDisplayType", 2)

    # ─── Custom Attributes ──────────────────────────────────────────

    @staticmethod
    def add_picture_index_attr(image_plane_shape, index=0):
        """Add custom attribute to track which picture is assigned.

        Args:
            image_plane_shape: Image plane shape name.
            index: Picture list index.
        """
        cmds.select(image_plane_shape)
        if not cmds.attributeQuery("imagePlaneName", node=image_plane_shape, exists=True):
            cmds.addAttr(ln="imagePlaneName", dv=0)
        cmds.setAttr(f"{image_plane_shape}.imagePlaneName", index)

    @staticmethod
    def get_picture_index(image_plane_shape):
        """Get the stored picture index from custom attribute.

        Args:
            image_plane_shape: Image plane shape name.

        Returns:
            int: Picture index, or 0 if attribute doesn't exist.
        """
        try:
            return int(cmds.getAttr(f"{image_plane_shape}.imagePlaneName"))
        except (ValueError, TypeError):
            return 0

    # ─── Image ──────────────────────────────────────────────────────

    @staticmethod
    def get_image_name(image_plane_shape):
        """Get the current image file name (without path or extension).

        Args:
            image_plane_shape: Image plane shape name.

        Returns:
            str: Image file name without extension.
        """
        full_path = cmds.getAttr(f"{image_plane_shape}.imageName")
        return os.path.splitext(os.path.basename(full_path))[0]

    @staticmethod
    def set_image(image_plane_shape, image_path, index=None):
        """Set the image file for an image plane.

        Args:
            image_plane_shape: Image plane shape name.
            image_path: Full path to the image file.
            index: Optional picture index to store.
        """
        cmds.setAttr(f"{image_plane_shape}.imageName", image_path, type="string")
        if index is not None:
            ImagePlaneService.add_picture_index_attr(image_plane_shape, index)

    # ─── Color ──────────────────────────────────────────────────────

    @staticmethod
    def get_color_gain(image_plane_shape):
        """Get the color gain RGB values.

        Args:
            image_plane_shape: Image plane shape name.

        Returns:
            tuple: (r, g, b) color values (0-1 range).
        """
        r = clip(cmds.getAttr(f"{image_plane_shape}.colorGainR"), 0, 1)
        g = clip(cmds.getAttr(f"{image_plane_shape}.colorGainG"), 0, 1)
        b = clip(cmds.getAttr(f"{image_plane_shape}.colorGainB"), 0, 1)
        return r, g, b

    @staticmethod
    def set_color_gain(image_plane_shape, r, g, b):
        """Set the color gain RGB values.

        Args:
            image_plane_shape: Image plane shape name.
            r, g, b: Color values (0-1 range).
        """
        cmds.setAttr(
            f"{image_plane_shape}.colorGain",
            r, g, b,
            type="double3"
        )

    @staticmethod
    def set_grayscale(image_plane_shape, value):
        """Set a uniform grayscale color gain.

        Args:
            image_plane_shape: Image plane shape name.
            value: Grayscale value (0-1 range).
        """
        ImagePlaneService.set_color_gain(image_plane_shape, value, value, value)

    # ─── Alpha ──────────────────────────────────────────────────────

    @staticmethod
    def get_alpha_gain(image_plane_shape):
        """Get the alpha gain value.

        Args:
            image_plane_shape: Image plane shape name.

        Returns:
            float: Alpha gain value (0-1 range).
        """
        return cmds.getAttr(f"{image_plane_shape}.alphaGain")

    @staticmethod
    def set_alpha_gain(image_plane_shape, value):
        """Set the alpha gain value.

        Args:
            image_plane_shape: Image plane shape name.
            value: Alpha gain value (0-1 range).
        """
        cmds.setAttr(f"{image_plane_shape}.alphaGain", value)

    # ─── Transform ──────────────────────────────────────────────────

    @staticmethod
    def set_rotation(image_plane_shape, angle):
        """Set the image plane rotation.

        Args:
            image_plane_shape: Image plane shape name.
            angle: Rotation angle in degrees.
        """
        cmds.setAttr(f"{image_plane_shape}.rotate", angle)

    @staticmethod
    def set_size_y(image_plane_shape, size):
        """Set the vertical size of the image plane.

        Args:
            image_plane_shape: Image plane shape name.
            size: Vertical size value.
        """
        cmds.setAttr(f"{image_plane_shape}.sizeY", size)

    # ─── Fit Mode ───────────────────────────────────────────────────

    @staticmethod
    def set_fit_mode(image_plane_shape, mode):
        """Set the image plane fit mode.

        Args:
            image_plane_shape: Image plane shape name.
            mode: Fit mode (0=Fill, 1=Best, 2=Horizontal, 3=Vertical, 4=To Size).
        """
        cmds.setAttr(f"{image_plane_shape}.fit", mode)

    @staticmethod
    def get_fit_mode(image_plane_shape):
        """Get the image plane fit mode.

        Args:
            image_plane_shape: Image plane shape name.

        Returns:
            int: Fit mode value.
        """
        return cmds.getAttr(f"{image_plane_shape}.fit")

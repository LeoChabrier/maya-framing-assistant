"""Camera operations service for Maya."""

from maya import cmds, mel


class CameraService:
    """Service class for all Maya camera operations."""

    @staticmethod
    def get_user_cameras():
        """Get list of user-created cameras (excluding default cameras).

        Returns:
            list: List of camera transform names.
        """
        cameras = [
            c for c in cmds.ls(type='camera')
            if not cmds.camera(c, q=True, sc=True)  # Exclude startup cameras
        ]
        transforms = cmds.listRelatives(cameras, parent=True, fullPath=False)
        return transforms if transforms else []

    @staticmethod
    def get_active_viewport():
        """Get the current active viewport and camera.

        Returns:
            tuple: (viewport_name, camera_name) or ('', '') if none found.
        """
        current_viewport = ''
        current_camera = ''
        user_cameras = CameraService.get_user_cameras()

        for viewport in cmds.getPanel(type="modelPanel"):
            cam_path = cmds.modelEditor(viewport, q=True, av=True, cam=True)
            parts = cam_path.split('|')
            camera = parts[-2] if len(parts) >= 2 else parts[-1]

            # Workaround for Maya 2022 viewport bug
            if not current_viewport and camera == 'persp':
                current_viewport = viewport

            if camera and str(cmds.objectType(cam_path)) != "camera":
                camera = parts[-1]

            if camera in user_cameras:
                current_viewport = viewport
                current_camera = camera

        return current_viewport, current_camera

    @staticmethod
    def get_camera_shape(camera_transform):
        """Get the shape node of a camera transform.

        Args:
            camera_transform: Camera transform name.

        Returns:
            list: Camera shape nodes.
        """
        return cmds.listRelatives(camera_transform)

    @staticmethod
    def look_through(viewport, camera):
        """Set the viewport to look through a specific camera.

        Args:
            viewport: Viewport panel name.
            camera: Camera transform name.
        """
        cmds.lookThru(viewport, camera)

    @staticmethod
    def create_camera():
        """Create a new camera with default settings.

        Returns:
            tuple: (transform, shape) names of the created camera.
        """
        result = cmds.camera()
        shape = result[1] if len(result) > 1 else "cameraShape1"

        cmds.setAttr(f"{shape}.displayCameraFrustum", 0)
        cmds.setAttr(f"{shape}.nearClipPlane", 1)
        cmds.setAttr(f"{shape}.farClipPlane", 20000)
        cmds.select(cl=True)

        return result

    # ─── Focal Length ───────────────────────────────────────────────

    @staticmethod
    def get_focal_length(camera):
        """Get the focal length of a camera.

        Args:
            camera: Camera transform name.

        Returns:
            float: Focal length value.
        """
        return cmds.getAttr(f"{camera}.focalLength")

    @staticmethod
    def set_focal_length(camera, value):
        """Set the focal length of a camera.

        Args:
            camera: Camera transform name.
            value: Focal length value.
        """
        cmds.setAttr(f"{camera}.focalLength", value)

    @staticmethod
    def get_center_of_interest(camera):
        """Get the center of interest distance.

        Args:
            camera: Camera transform name.

        Returns:
            float: Center of interest distance.
        """
        return cmds.getAttr(f"{camera}.centerOfInterest")

    @staticmethod
    def dolly(camera, distance):
        """Dolly the camera to a specific distance.

        Args:
            camera: Camera transform name.
            distance: Absolute distance value.
        """
        cmds.dolly(camera, abs=True, d=distance)

    # ─── Camera Display ─────────────────────────────────────────────

    @staticmethod
    def set_frustum_display(camera, state):
        """Toggle camera frustum display.

        Args:
            camera: Camera transform name.
            state: Boolean to show/hide frustum.
        """
        cmds.setAttr(f"{camera}.displayCameraFrustum", state)

    @staticmethod
    def set_camera_display_settings(camera):
        """Apply standard display settings to a camera.

        Args:
            camera: Camera transform name.
        """
        cmds.setAttr(f"{camera}.displayResolution", 1)
        cmds.setAttr(f"{camera}.displayGateMask", 1)
        cmds.setAttr(f"{camera}.displayFilmGate", 1)

    @staticmethod
    def get_overscan(camera):
        """Get camera overscan value.

        Args:
            camera: Camera transform name.

        Returns:
            float: Overscan value.
        """
        return cmds.getAttr(f"{camera}.overscan")

    @staticmethod
    def set_overscan(camera_shape, value):
        """Set camera overscan value.

        Args:
            camera_shape: Camera shape name.
            value: Overscan value (1.0 = no overscan).
        """
        cmds.setAttr(f"{camera_shape}.overscan", value)

    @staticmethod
    def get_vertical_film_aperture(camera):
        """Get camera vertical film aperture.

        Args:
            camera: Camera transform name.

        Returns:
            float: Vertical film aperture value.
        """
        return cmds.getAttr(f"{camera}.verticalFilmAperture")

    @staticmethod
    def get_horizontal_film_aperture(camera):
        """Get camera horizontal film aperture.

        Args:
            camera: Camera transform name.

        Returns:
            float: Horizontal film aperture value.
        """
        return cmds.getAttr(f"{camera}.horizontalFilmAperture")

    # ─── Pan/Zoom ───────────────────────────────────────────────────

    @staticmethod
    def set_pan_zoom_enabled(camera_shape, state):
        """Enable or disable pan/zoom on a camera.

        Args:
            camera_shape: Camera shape name.
            state: Boolean to enable/disable.
        """
        cmds.setAttr(f"{camera_shape}.panZoomEnabled", state)

    @staticmethod
    def get_pan_values(camera_shape):
        """Get horizontal and vertical pan values.

        Args:
            camera_shape: Camera shape name.

        Returns:
            tuple: (horizontal_pan, vertical_pan).
        """
        h_pan = cmds.getAttr(f"{camera_shape}.horizontalPan")
        v_pan = cmds.getAttr(f"{camera_shape}.verticalPan")
        return h_pan, v_pan

    @staticmethod
    def set_pan_values(camera_shape, h_pan, v_pan):
        """Set horizontal and vertical pan values.

        Args:
            camera_shape: Camera shape name.
            h_pan: Horizontal pan value.
            v_pan: Vertical pan value.
        """
        cmds.setAttr(f"{camera_shape}.horizontalPan", h_pan)
        cmds.setAttr(f"{camera_shape}.verticalPan", v_pan)

    @staticmethod
    def get_zoom(camera_shape):
        """Get camera zoom value.

        Args:
            camera_shape: Camera shape name.

        Returns:
            float: Zoom value.
        """
        return cmds.getAttr(f"{camera_shape}.zoom")

    @staticmethod
    def set_zoom(camera_shape, value):
        """Set camera zoom value.

        Args:
            camera_shape: Camera shape name.
            value: Zoom value.
        """
        cmds.setAttr(f"{camera_shape}.zoom", value)

    @staticmethod
    def reset_pan_zoom(camera_shape):
        """Reset pan/zoom to default values.

        Args:
            camera_shape: Camera shape name.
        """
        cmds.setAttr(f"{camera_shape}.horizontalPan", 0)
        cmds.setAttr(f"{camera_shape}.verticalPan", 0)
        cmds.setAttr(f"{camera_shape}.zoom", 1)

    # ─── Roll ───────────────────────────────────────────────────────

    @staticmethod
    def set_roll(camera, value):
        """Set camera roll angle.

        Args:
            camera: Camera transform name.
            value: Roll angle in degrees.
        """
        cmds.setAttr(f"{camera}.rotateAxisZ", value)

    # ─── Tools ──────────────────────────────────────────────────────

    @staticmethod
    def activate_tumble_tool(orbit_mode=True):
        """Activate the tumble tool with specific settings.

        Args:
            orbit_mode: If True, use orbit mode. If False, use standard tumble.
        """
        if orbit_mode:
            cmds.setToolTo('tumbleContext')
            cmds.tumbleCtx(
                'tumbleContext',
                edit=True,
                localTumble=False,
                autoSetPivot=True,
                ot=True,
                ac=False,
                ts=1
            )
        else:
            cmds.setToolTo('selectSuperContext')
            cmds.tumbleCtx(
                'tumbleContext',
                edit=True,
                alternateContext=1,
                ot=False,
                localTumble=True,
                autoSetPivot=False,
                ts=1
            )

    @staticmethod
    def show_manipulator(camera_shape):
        """Show the manipulator tool for a camera.

        Args:
            camera_shape: Camera shape name.
        """
        cmds.select(clear=True)
        cmds.select(camera_shape)
        mel.eval('ShowManipulatorTool')

    @staticmethod
    def activate_move_tool():
        """Activate the move tool."""
        mel.eval('MoveTool')

    @staticmethod
    def clear_selection():
        """Clear the current selection."""
        cmds.select(clear=True)

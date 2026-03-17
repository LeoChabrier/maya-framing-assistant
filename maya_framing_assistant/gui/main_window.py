"""Main window for Maya Framing Assistant."""

try:
    from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
    from maya import cmds
    MAYA_AVAILABLE = True
except ImportError:
    MAYA_AVAILABLE = False

from utils import (
    QtWidgets, QtCore, QtGui, QUiLoader,
    MouseButtonPress, MouseMove, Wheel, LeftButton, get_event_pos
)
from utils import Paths

if MAYA_AVAILABLE:
    from core import CameraService, ImagePlaneService, RenderSettings
    from core.render_settings import RenderFormat
    from core.image_plane_service import clip


if MAYA_AVAILABLE:
    class _MainWindowBase(MayaQWidgetBaseMixin, QtWidgets.QMainWindow):
        pass
else:
    class _MainWindowBase(QtWidgets.QMainWindow):
        pass


class MainWindow(_MainWindowBase):
    """Main window for the Framing Helper tool."""

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # Load UI from file
        self.ui = QUiLoader().load(Paths.ui_file())
        self.setWindowTitle('Framing Helper')
        self.setCentralWidget(self.ui)

        # Initialize state
        self._init_state()

        # Connect signals
        self._connect_signals()

        # Setup event filters
        self.ui.listCam.installEventFilter(self)
        self.ui.panZoomArea.installEventFilter(self)

        # Initial setup
        self._activate_options(2)
        self._init_render_format_buttons()

    def _init_state(self):
        """Initialize instance state variables."""
        self.image_plane = ''
        self.selected_pic = ''
        self.cam_aperture_y = 0.0
        self.focal = 0.0
        self.current_camera_shape = ''
        self.image_plane_shape = ''

        if MAYA_AVAILABLE:
            viewport, camera = CameraService.get_active_viewport()
            self.viewer_to_use = viewport
            self.camera_to_use = camera
        else:
            self.viewer_to_use = ''
            self.camera_to_use = ''

        self.init_pan_zoom_x = 0.0
        self.init_pan_zoom_y = 0.0
        self.current_pan_zoom_x = 0.0
        self.current_pan_zoom_y = 0.0
        self.init_center_of_interest = 0

        # Populate picture list
        self.ui.listPic.setCurrentRow(0)
        self.ui.listPic.addItems(Paths.list_pictures())

        if self.ui.listPic.count() > 0:
            first_pic = self.ui.listPic.item(0).text()
            self.selected_pic = first_pic
            self.ui.preview.setPixmap(QtGui.QPixmap(Paths.picture(first_pic)))

        self.ui.panZoomArea.setEnabled(False)

        if MAYA_AVAILABLE and self.ui.imagePlane.text():
            self.image_plane_shape = ImagePlaneService.get_image_plane_shape(
                self.ui.imagePlane.text()
            )

    def _connect_signals(self):
        """Connect all UI signals to slots."""
        # Camera
        self.ui.listCam.currentIndexChanged.connect(self._on_camera_changed)
        self.ui.showFrustum.clicked.connect(self._on_show_frustum)
        self.ui.overScan.valueChanged.connect(self._on_overscan_changed)

        # Image Plane
        self.ui.pb_create.clicked.connect(self._on_create_delete)
        self.ui.listPic.itemClicked.connect(self._on_picture_selected)
        self.ui.colorOffset.valueChanged.connect(self._on_color_offset_changed)
        self.ui.alphaGain.valueChanged.connect(self._on_alpha_changed)
        self.ui.rotateButton.clicked.connect(self._on_rotate)
        self.ui.pushColor.clicked.connect(self._on_color_picker)
        self.ui.gate.clicked.connect(self._on_gate_toggle)
        self.ui.fit.clicked.connect(self._on_fit_toggle)
        self.ui.aspectRatio.clicked.connect(self._on_aspect_ratio_toggle)

        # Focal Length
        self.ui.focalLength.valueChanged.connect(self._on_focal_length_changed)
        self.ui.focalLength.sliderPressed.connect(self._on_focal_slider_pressed)
        self.ui.focalLengthValue.returnPressed.connect(self._on_focal_value_entered)
        self.ui.dollyZoomCheckBox.clicked.connect(self._on_dolly_zoom_toggle)
        self.ui.showManip.clicked.connect(self._on_show_manip)

        # Focal Presets
        for btn_name in ['12', '24', '35', '50', '85', '100', '135', '150', '175', '200']:
            btn = getattr(self.ui, f'pushButton{btn_name}')
            btn.clicked.connect(self._on_focal_preset)

        # Pan/Zoom
        self.ui.panZoom.clicked.connect(self._on_pan_zoom_toggle)
        self.ui.initPushButton.clicked.connect(self._on_reset_pan_zoom)

        # Roll & Tumble
        self.ui.rollSlider.valueChanged.connect(self._on_roll_changed)
        self.ui.tumbleTool.clicked.connect(self._on_tumble_toggle)

        # Render Settings
        self.ui.hdFormat.clicked.connect(self._on_render_format)
        self.ui.scopeFormat.clicked.connect(self._on_render_format)
        self.ui.flatFormat.clicked.connect(self._on_render_format)

    def _init_render_format_buttons(self):
        """Set render format buttons based on current settings."""
        if not MAYA_AVAILABLE:
            return
        current_format = RenderSettings.detect_current_format()
        self.ui.hdFormat.setChecked(current_format == 'HD')
        self.ui.flatFormat.setChecked(current_format == 'Flat')
        self.ui.scopeFormat.setChecked(current_format == 'Scope')

    # ─── Event Handling ─────────────────────────────────────────────

    def closeEvent(self, event):
        """Handle window close - reset tumble tool."""
        self._on_tumble_toggle(False)

    def eventFilter(self, obj, event):
        """Filter events for custom widget behavior."""
        if event.type() == MouseButtonPress:
            if obj is self.ui.listCam and self.ui.listCam != '':
                self.update_camera_list()
            elif obj is self.ui.panZoomArea:
                pos = get_event_pos(event)
                self._init_pan_zoom(pos.x(), pos.y())

        elif event.type() == Wheel and obj is self.ui.panZoomArea:
            self._on_pan_zoom_wheel(event.angleDelta().y())

        elif event.type() == MouseMove and obj is self.ui.panZoomArea:
            if event.buttons() == LeftButton and self.ui.panZoom.isChecked():
                pos = get_event_pos(event)
                self._do_pan_zoom_move(pos.x(), pos.y())

        return False

    # ─── Camera List ────────────────────────────────────────────────

    def update_camera_list(self):
        """Refresh the camera dropdown list."""
        if not MAYA_AVAILABLE:
            return
        current_cam = self.ui.listCam.currentText() or self.camera_to_use
        current_idx = self.ui.listCam.currentIndex()

        self.ui.listCam.clear()
        cameras = CameraService.get_user_cameras()
        self.ui.listCam.addItems(cameras)

        self._activate_options(1)
        self.ui.tabWidget.setEnabled(bool(cameras))

        if cameras:
            if current_cam in cameras:
                current_idx = cameras.index(current_cam)
            self._on_camera_changed(current_idx)
        else:
            print("Please create a camera.")

    def _on_camera_changed(self, index):
        """Handle camera selection change."""
        if not MAYA_AVAILABLE:
            return
        self.ui.imagePlane.setText('')
        self.ui.listCam.setCurrentIndex(index)

        if not self.ui.listCam.currentText():
            return

        camera = self.ui.listCam.currentText()
        self.current_camera_shape = CameraService.get_camera_shape(camera)

        # Check for existing image plane
        image_plane = ImagePlaneService.get_image_plane(self.current_camera_shape)
        if image_plane:
            self.ui.imagePlane.setText(image_plane)
            self._update_image_preview()
            self.ui.imagePlaneFrame.setEnabled(True)
            self.ui.pb_create.setText('Delete')
        else:
            self.ui.listPic.setCurrentRow(0)
            self.ui.imagePlaneFrame.setEnabled(False)
            self.ui.pb_create.setText('Create Image Plane')

        # Update focal length UI
        focal = CameraService.get_focal_length(camera)
        self.ui.focalLength.setValue(focal)
        self.ui.focalLengthValue.setText(str(int(focal)))

        # Update overscan UI
        overscan = CameraService.get_overscan(camera)
        self.ui.overScan.setValue((overscan - 1) * 100)

        if index != -1:
            CameraService.look_through(self.viewer_to_use, camera)

    # ─── Image Plane Operations ─────────────────────────────────────

    def _on_create_delete(self):
        """Handle create/delete image plane button."""
        if not MAYA_AVAILABLE:
            return
        if self.ui.pb_create.text() == 'Delete':
            self._delete_image_plane()
            self.ui.pb_create.setText('Create Image Plane')
        else:
            self._create_image_plane()
            self.ui.pb_create.setText('Delete')

    def _create_image_plane(self):
        """Create a new image plane for the current camera."""
        if not MAYA_AVAILABLE:
            return
        camera = self.ui.listCam.currentText()
        pic_name = self.ui.listPic.currentItem().text()
        pic_index = self.ui.listPic.currentRow()

        # Create image plane
        self.image_plane_shape = ImagePlaneService.create(
            camera, Paths.picture(pic_name)
        )

        # Store picture index
        ImagePlaneService.add_picture_index_attr(self.image_plane_shape, pic_index)

        # Get color from button
        color = self.ui.pushColor.palette().button().color().getRgb()
        color_rgb = (color[0] / 255, color[1] / 255, color[2] / 255)
        alpha = self.ui.alphaGain.value() / 100

        # Setup image plane
        camera_shape = self.current_camera_shape[0]
        ImagePlaneService.setup_defaults(
            self.image_plane_shape, camera_shape, color_rgb, alpha
        )

        # Setup camera display
        CameraService.set_camera_display_settings(camera)

        # Fit to resolution gate
        self.cam_aperture_y = CameraService.get_vertical_film_aperture(camera)
        self._on_gate_toggle(True)

        CameraService.clear_selection()

        # Update UI
        image_plane = ImagePlaneService.get_image_plane(self.current_camera_shape)
        self.ui.imagePlane.setText(image_plane)
        self._activate_options(1)
        self.ui.imagePlaneFrame.setEnabled(True)
        self._on_image_plane_changed()

    def _delete_image_plane(self):
        """Delete the current image plane."""
        if not MAYA_AVAILABLE:
            return
        camera = self.ui.listCam.currentText()
        ImagePlaneService.delete(camera)

        self.ui.imagePlane.setText('')
        self._activate_options(0)
        self.ui.imagePlaneFrame.setEnabled(False)
        self.ui.listPic.setCurrentRow(0)

        if self.ui.listPic.currentItem():
            self.ui.preview.setPixmap(
                QtGui.QPixmap(Paths.picture(self.ui.listPic.currentItem().text()))
            )

    def _update_image_preview(self):
        """Update the preview pixmap and color from current image plane."""
        if not MAYA_AVAILABLE:
            return
        self.image_plane_shape = ImagePlaneService.get_image_plane_shape(
            self.ui.imagePlane.text()
        )
        image_name = ImagePlaneService.get_image_name(self.image_plane_shape)

        if image_name in Paths.list_pictures():
            pic_index = ImagePlaneService.get_picture_index(self.image_plane_shape)
            self.ui.listPic.setCurrentRow(pic_index)
            selected_pic = self.ui.listPic.currentItem().text()
            self.ui.preview.setPixmap(QtGui.QPixmap(Paths.picture(selected_pic)))
            self._update_color_from_image_plane()

    def _on_image_plane_changed(self):
        """Handle image plane selection change."""
        if not MAYA_AVAILABLE:
            return
        if not self.ui.imagePlane.text() or not self.ui.listPic.currentItem():
            return

        self.image_plane_shape = ImagePlaneService.get_image_plane_shape(
            self.ui.imagePlane.text()
        )
        self.selected_pic = self.ui.listPic.currentItem().text()

        pic_index = ImagePlaneService.get_picture_index(self.image_plane_shape)
        self.ui.listPic.setCurrentRow(pic_index)
        self.ui.preview.setPixmap(QtGui.QPixmap(Paths.picture(self.selected_pic)))
        self._activate_options(1)

        # Handle Golden Ratio special case
        is_golden = self.selected_pic in ('Golden_Ratio', 'Golden_Ratio_Mirror')
        self.ui.aspectRatio.setEnabled(not is_golden)
        self.ui.aspectRatio.setChecked(not is_golden)
        self._on_aspect_ratio_toggle(not is_golden)

    def _on_picture_selected(self):
        """Handle picture list selection."""
        if not self.ui.listPic.currentItem():
            return

        self.selected_pic = self.ui.listPic.currentItem().text()
        self.ui.preview.setPixmap(QtGui.QPixmap(Paths.picture(self.selected_pic)))

        if MAYA_AVAILABLE and self.ui.imagePlane.text():
            self.image_plane_shape = ImagePlaneService.get_image_plane_shape(
                self.ui.imagePlane.text()
            )
            pic_index = self.ui.listPic.currentRow()
            ImagePlaneService.set_image(
                self.image_plane_shape,
                Paths.picture(self.selected_pic),
                pic_index
            )
            self._update_image_preview()
            self._on_image_plane_changed()

    # ─── Color & Alpha ──────────────────────────────────────────────

    def _on_color_offset_changed(self, value):
        """Handle color offset slider change."""
        gray = value / 100
        if MAYA_AVAILABLE:
            ImagePlaneService.set_grayscale(self.image_plane_shape, gray)
        color_css = f'background-color:rgb({int(gray*255)},{int(gray*255)},{int(gray*255)})'
        self.ui.pushColor.setStyleSheet(color_css)

    def _on_alpha_changed(self, value):
        """Handle alpha slider change."""
        if not MAYA_AVAILABLE:
            return
        ImagePlaneService.set_alpha_gain(self.image_plane_shape, value / 100)

    def _on_color_picker(self):
        """Open color editor."""
        current_color = self.ui.pushColor.palette().button().color()
        if MAYA_AVAILABLE:
            rgb_tuple = current_color.getRgb()
            cmds.colorEditor(
                rgb=(rgb_tuple[0]/255, rgb_tuple[1]/255, rgb_tuple[2]/255),
                alpha=False
            )
            if cmds.colorEditor(query=True, result=True):
                rgb = cmds.colorEditor(query=True, rgb=True)
                ImagePlaneService.set_color_gain(self.image_plane_shape, *rgb)
                color_css = f'background-color:rgb({int(rgb[0]*255)},{int(rgb[1]*255)},{int(rgb[2]*255)})'
                self.ui.pushColor.setStyleSheet(color_css)
        else:
            color = QtWidgets.QColorDialog.getColor(current_color, self, 'Pick a color')
            if color.isValid():
                color_css = f'background-color:rgb({color.red()},{color.green()},{color.blue()})'
                self.ui.pushColor.setStyleSheet(color_css)

    def _update_color_from_image_plane(self):
        """Update UI controls from image plane color values."""
        if not MAYA_AVAILABLE:
            return
        r, g, b = ImagePlaneService.get_color_gain(self.image_plane_shape)
        ImagePlaneService.set_color_gain(self.image_plane_shape, r, g, b)

        alpha = ImagePlaneService.get_alpha_gain(self.image_plane_shape)
        self.ui.alphaGain.setValue(alpha * 100)

        color_css = f'background-color:rgb({int(r*255)},{int(g*255)},{int(b*255)})'
        self.ui.pushColor.setStyleSheet(color_css)

        if r == g == b:
            self.ui.colorOffset.setValue(r * 100)

    # ─── Image Plane Settings ───────────────────────────────────────

    def _on_rotate(self, state):
        """Handle rotate button toggle."""
        if not MAYA_AVAILABLE:
            return
        ImagePlaneService.set_rotation(self.image_plane_shape, 180 if state else 0)

    def _on_gate_toggle(self, state):
        """Handle resolution/film gate toggle."""
        if not MAYA_AVAILABLE:
            return
        if state:
            self.ui.gate.setText('Resolution')
            camera = self.ui.listCam.currentText()
            fit_size = RenderSettings.calculate_fit_to_resolution_gate(camera)
            ImagePlaneService.set_size_y(self.image_plane_shape, fit_size)
        else:
            ImagePlaneService.set_size_y(self.image_plane_shape, self.cam_aperture_y)
            self.ui.gate.setText('Film Gate')

    def _on_fit_toggle(self, state):
        """Handle horizontal/vertical fit toggle."""
        if not MAYA_AVAILABLE:
            return
        if state:
            ImagePlaneService.set_fit_mode(self.image_plane_shape, 2)  # Horizontal
            self.ui.fit.setText('Horizontal')
        else:
            ImagePlaneService.set_fit_mode(self.image_plane_shape, 3)  # Vertical
            self.ui.fit.setText('Vertical')

    def _on_aspect_ratio_toggle(self, state):
        """Handle aspect ratio toggle."""
        if not MAYA_AVAILABLE:
            return
        if state:
            ImagePlaneService.set_fit_mode(self.image_plane_shape, 4)  # To Size
        else:
            # Use current fit mode
            fit_text = self.ui.fit.text()
            mode = 2 if fit_text == 'Horizontal' else 3 if fit_text == 'Vertical' else 0
            ImagePlaneService.set_fit_mode(self.image_plane_shape, mode)

    # ─── Focal Length ───────────────────────────────────────────────

    def _on_focal_length_changed(self, value):
        """Handle focal length slider change."""
        self.ui.focalLengthValue.setText(str(value))
        if not MAYA_AVAILABLE:
            return
        camera = self.ui.listCam.currentText()
        CameraService.set_focal_length(camera, value)

        if self.ui.dollyZoomCheckBox.isChecked():
            distance = (self.init_center_of_interest * value) / self.focal
            CameraService.dolly(camera, distance)

    def _on_focal_slider_pressed(self):
        """Handle focal length slider press - store initial values."""
        if not MAYA_AVAILABLE:
            return
        camera = self.ui.listCam.currentText()
        self.init_center_of_interest = CameraService.get_center_of_interest(camera)
        self.focal = self.ui.focalLength.value()

    def _on_focal_value_entered(self):
        """Handle focal length text entry."""
        text = self.ui.focalLengthValue.text()
        if text:
            self.ui.focalLength.setValue(float(text))

    def _on_focal_preset(self):
        """Handle focal length preset button click."""
        btn = self.sender()
        value = float(btn.text())
        self.ui.focalLength.setValue(value)
        self.ui.focalLengthValue.setText(str(int(value)))
        if MAYA_AVAILABLE:
            CameraService.set_focal_length(self.ui.listCam.currentText(), value)

    def _on_dolly_zoom_toggle(self, state):
        """Handle dolly zoom checkbox toggle."""
        self.ui.showManip.setEnabled(state)
        if state:
            self._on_focal_slider_pressed()
            self.ui.showManip.setChecked(True)
            self._on_show_manip()
        elif MAYA_AVAILABLE:
            CameraService.clear_selection()

    def _on_show_manip(self):
        """Handle show manipulator checkbox."""
        if not MAYA_AVAILABLE:
            return
        CameraService.show_manipulator(self.current_camera_shape)
        if not self.ui.showManip.isChecked():
            CameraService.activate_move_tool()

    # ─── Camera Controls ────────────────────────────────────────────

    def _on_show_frustum(self, state):
        """Handle show frustum checkbox."""
        if not MAYA_AVAILABLE:
            return
        CameraService.set_frustum_display(self.ui.listCam.currentText(), state)

    def _on_overscan_changed(self, value):
        """Handle overscan slider change."""
        if not MAYA_AVAILABLE:
            return
        overscan = (value * 0.01) + 1
        CameraService.set_overscan(self.current_camera_shape[0], float(f'{overscan:.4f}'))

    def _on_roll_changed(self, value):
        """Handle roll slider change."""
        if not MAYA_AVAILABLE:
            return
        CameraService.set_roll(self.ui.listCam.currentText(), value)

    def _on_tumble_toggle(self, state):
        """Handle tumble tool toggle."""
        if not MAYA_AVAILABLE:
            return
        CameraService.activate_tumble_tool(orbit_mode=state)

    # ─── Pan/Zoom ───────────────────────────────────────────────────

    def _on_pan_zoom_toggle(self, state):
        """Handle pan/zoom toggle."""
        if MAYA_AVAILABLE:
            CameraService.set_pan_zoom_enabled(self.current_camera_shape[0], state)
        self.ui.panZoomArea.setEnabled(state)

    def _on_reset_pan_zoom(self):
        """Handle reset pan/zoom button."""
        if not MAYA_AVAILABLE:
            return
        CameraService.reset_pan_zoom(self.current_camera_shape[0])

    def _init_pan_zoom(self, x, y):
        """Initialize pan/zoom interaction."""
        self.init_pan_zoom_x = x
        self.init_pan_zoom_y = y
        if MAYA_AVAILABLE:
            h_pan, v_pan = CameraService.get_pan_values(self.current_camera_shape[0])
            self.current_pan_zoom_x = h_pan
            self.current_pan_zoom_y = v_pan

    def _on_pan_zoom_wheel(self, delta):
        """Handle pan/zoom wheel event."""
        if not MAYA_AVAILABLE:
            return
        if not self.ui.panZoom.isChecked():
            return

        camera_shape = self.current_camera_shape[0]
        change = -0.05 * (delta / 120)
        current_zoom = CameraService.get_zoom(camera_shape)
        new_zoom = round(current_zoom + change, 3)

        if new_zoom >= 0.01:
            CameraService.set_zoom(camera_shape, new_zoom)

    def _do_pan_zoom_move(self, x, y):
        """Handle pan/zoom mouse move."""
        if not MAYA_AVAILABLE:
            return
        camera_shape = self.current_camera_shape[0]
        zoom = CameraService.get_zoom(camera_shape)

        # Panel size = 150x85px
        h_pan = (((x - self.init_pan_zoom_x) / -150) * zoom * 0.2) + self.current_pan_zoom_x
        v_pan = (((y - self.init_pan_zoom_y) / 85) * zoom * 0.2) + self.current_pan_zoom_y

        CameraService.set_pan_values(
            camera_shape,
            clip(h_pan, -1.4, 1.4),
            clip(v_pan, -1, 1)
        )

    # ─── Render Settings ────────────────────────────────────────────

    def _on_render_format(self):
        """Handle render format radio button change."""
        if not MAYA_AVAILABLE:
            return
        if self.ui.hdFormat.isChecked():
            RenderSettings.apply_format(RenderFormat.HD)
            self.ui.flatFormat.setChecked(False)
            self.ui.scopeFormat.setChecked(False)
        elif self.ui.flatFormat.isChecked():
            RenderSettings.apply_format(RenderFormat.FLAT)
            self.ui.hdFormat.setChecked(False)
            self.ui.scopeFormat.setChecked(False)
        elif self.ui.scopeFormat.isChecked():
            RenderSettings.apply_format(RenderFormat.SCOPE)
            self.ui.hdFormat.setChecked(False)
            self.ui.flatFormat.setChecked(False)

    # ─── Helpers ────────────────────────────────────────────────────

    def _activate_options(self, value):
        """Enable/disable UI elements based on state."""
        if value == 1:
            self.ui.listCam.setEnabled(True)
            self.ui.listPic.setEnabled(True)
            self.ui.preview.setEnabled(True)
        elif value == 0:
            self.ui.imagePlaneFrame.setEnabled(False)
        elif value == 2:
            self.ui.imagePlaneFrame.setEnabled(False)
            self.ui.listCam.setEnabled(False)
            self.ui.listPic.setEnabled(False)
            self.ui.preview.setEnabled(False)

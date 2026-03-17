# Changelog

## [2.0.0] - 2026-03-17

### refactor: restructure project into package architecture

- Reorganized codebase from a single `MayaFramingAssistant.py` script into a proper Python package (`maya_framing_assistant/`)
- Extracted camera operations into `core/camera_service.py` (`CameraService`)
- Extracted image plane operations into `core/image_plane_service.py` (`ImagePlaneService`)
- Extracted render settings logic into `core/render_settings.py` (`RenderSettings`, `RenderFormat`)
- Created `utils/paths.py` for centralized path management (`Paths`)
- Created `utils/qt_compat.py` for PySide6/PySide2 compatibility layer
- Moved UI file to `gui/mainWindow.ui`
- Moved framing overlay images to `images/pictures/`
- Added `main.py` as the Maya entry point (with camera detection and dialog prompt)
- Added `__main__.py` for standalone execution

### feat: add standalone mode (no Maya dependency for UI)

- Made Maya imports conditional in `gui/main_window.py` behind a `MAYA_AVAILABLE` flag
- Made core service imports (`CameraService`, `ImagePlaneService`, `RenderSettings`) conditional
- Introduced a dynamic base class: `MayaQWidgetBaseMixin + QMainWindow` inside Maya, plain `QMainWindow` standalone
- Guarded all Maya service calls so the UI loads and remains interactive without Maya
- Replaced `cmds.colorEditor` with `QColorDialog` fallback when running standalone
- Added `QApplication` creation in `__main__.py` for standalone execution with PySide6/PySide2 compat

### feat: add new framing overlays

- Added `rule_of_thirds.png` overlay
- Added `triangle.png` overlay

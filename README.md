# Maya Framing Assistant

A Maya toolbox for composition and framing. Easily create image plane overlays with framing guides like Rule of Thirds, Golden Ratio, and more.

[![Maya Framing Assistant](https://i.ibb.co/GVFVyqC/Maya-Framing-Assistant.jpg)](https://vimeo.com/701267617 "Maya Framing Assistant - Click to Watch!")

**Video Demo:** [https://vimeo.com/701267617](https://vimeo.com/701267617)

## Features

- **Framing Overlays**: Rule of Thirds, Golden Ratio, Golden Triangles, Dynamic Symmetry, and more
- **Camera Controls**: Focal length presets, dolly zoom, pan/zoom, roll, tumble tool
- **Render Presets**: HD (1920x1080), Flat (1998x1080), Scope (2048x858)
- **Customizable**: Add your own PNG overlays to the pictures folder

## Installation

**Drag & Drop:** Simply drag the `drop_to_maya_viewport.mel` file into your Maya viewport. A shelf button will be created automatically.

**Manual:**
```python
import sys
sys.path.insert(0, r"path/to/maya-framing-assistant")
import main
main.main()
```

## Compatibility

- Maya 2022-2024 (PySide2)
- Maya 2025+ (PySide6)

## Project Structure

```
maya-framing-assistant/
├── main.py                 # Entry point
├── core/
│   ├── camera_service.py   # Maya camera operations
│   ├── image_plane_service.py
│   └── render_settings.py
├── gui/
│   ├── main_window.py      # UI logic
│   └── mainWindow.ui
├── utils/
│   ├── qt_compat.py        # PySide2/6 compatibility
│   └── paths.py
└── images/
    └── pictures/           # Framing overlay PNGs
```

## Adding Custom Overlays

Add your own PNG images (with alpha transparency) to `images/pictures/`. They will automatically appear in the overlay list.

## Author

**Christophe Moreau** - [moreau.vfx@gmail.com](mailto:moreau.vfx@gmail.com)

## Version History

- **v2.0** - Refactored architecture with service-based pattern, PySide6 support
- **v1.1** - Added 2D pan/zoom with click & drag, rounded UI
- **v1.0** - Initial release

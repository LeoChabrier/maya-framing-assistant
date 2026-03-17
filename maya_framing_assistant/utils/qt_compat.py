"""Qt compatibility layer.

Imports PySide6/shiboken6 (Maya 2025+) or falls back to
PySide2/shiboken2 (Maya 2022-2024).
"""
# pylint: disable=unused-import

IS_PYSIDE6 = False

try:
    from PySide6 import QtWidgets, QtCore, QtGui
    from PySide6.QtUiTools import QUiLoader
    IS_PYSIDE6 = True

    # PySide6 event types
    MouseButtonPress = QtCore.QEvent.Type.MouseButtonPress
    MouseButtonRelease = QtCore.QEvent.Type.MouseButtonRelease
    MouseMove = QtCore.QEvent.Type.MouseMove
    Wheel = QtCore.QEvent.Type.Wheel
    MouseButtonDblClick = QtCore.QEvent.Type.MouseButtonDblClick

    # PySide6 mouse buttons
    LeftButton = QtCore.Qt.MouseButton.LeftButton
    RightButton = QtCore.Qt.MouseButton.RightButton
    MiddleButton = QtCore.Qt.MouseButton.MiddleButton

    def get_event_pos(event):
        """Get mouse event position (PySide6 uses position())."""
        return event.position()

except ImportError:
    from PySide2 import QtWidgets, QtCore, QtGui
    from PySide2.QtUiTools import QUiLoader

    # PySide2 event types
    MouseButtonPress = QtCore.QEvent.MouseButtonPress
    MouseButtonRelease = QtCore.QEvent.MouseButtonRelease
    MouseMove = QtCore.QEvent.MouseMove
    Wheel = QtCore.QEvent.Wheel
    MouseButtonDblClick = QtCore.QEvent.MouseButtonDblClick

    # PySide2 mouse buttons
    LeftButton = QtCore.Qt.LeftButton
    RightButton = QtCore.Qt.RightButton
    MiddleButton = QtCore.Qt.MiddleButton

    def get_event_pos(event):
        """Get mouse event position (PySide2 uses localPos())."""
        return event.localPos()

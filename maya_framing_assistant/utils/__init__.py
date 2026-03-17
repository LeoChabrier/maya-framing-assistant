"""Utility modules for Maya Framing Assistant."""

from .qt_compat import (
    QtWidgets, QtCore, QtGui, QUiLoader,
    MouseButtonPress, MouseButtonRelease, MouseMove, Wheel, MouseButtonDblClick,
    LeftButton, RightButton, MiddleButton, get_event_pos, IS_PYSIDE6
)
from .paths import Paths

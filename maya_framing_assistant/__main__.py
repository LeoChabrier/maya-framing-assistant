"""Entry point for the Maya Framing Assistant package as standalone script."""

# Built-in
import os
import sys

# Ensure the package root is in sys.path
PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))
if PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, PACKAGE_ROOT)

# Internal
from utils import QtWidgets, IS_PYSIDE6
from gui import MainWindow
from utils import Paths


def main():
    """Launch the Maya Framing Assistant window."""

    app = QtWidgets.QApplication.instance()
    standalone = app is None
    if standalone:
        app = QtWidgets.QApplication(sys.argv)

    # Create the main window
    window = MainWindow()
    window.show()

    if standalone:
        sys.exit(app.exec() if IS_PYSIDE6 else app.exec_())


if __name__ == '__main__':
    main()

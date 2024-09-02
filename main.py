# main.py

import sys
from PyQt6 import QtWidgets
from gpio_control_app import GPIOControlApp

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = GPIOControlApp()
    window.show()
    sys.exit(app.exec())

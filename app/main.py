"""
Point d'entrée principal de l'application.
"""

import sys
from PySide6.QtWidgets import QApplication
from app.ui import MainWindow


def main():
    """Lance l'application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

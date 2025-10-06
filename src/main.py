"""
Main Entry Point für Kapazitäts- & Auslastungsplaner
"""
import sys
from PySide6.QtWidgets import QApplication
from .views.main_window import MainWindow


def main():
    """Startet die Anwendung"""
    app = QApplication(sys.argv)
    app.setApplicationName("Kapazitäts- & Auslastungsplaner")
    app.setOrganizationName("YourOrg")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

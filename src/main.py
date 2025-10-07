"""
Main Entry Point für Kapazitäts- & Auslastungsplaner
"""
import sys
from PySide6.QtWidgets import QApplication, QDialog
from .views.main_window import MainWindow
from .views.login_dialog import LoginDialog
from .services.session_service import SessionService
from .services.database_service import DatabaseService
from .services.crypto_service import CryptoService


def main():
    """Startet die Anwendung"""
    app = QApplication(sys.argv)
    app.setApplicationName("Kapazitäts- & Auslastungsplaner")
    app.setOrganizationName("YourOrg")
    
    # EINE zentrale Datenbank-Verbindung für die gesamte App
    db_service = DatabaseService()
    db_service.initialize()
    
    # EINE zentrale Crypto-Service-Instanz
    crypto_service = CryptoService()
    crypto_service.initialize_keys()
    
    # Session-Service initialisieren
    session_service = SessionService()
    
    # Versuche gespeicherte Session zu laden
    saved_session = session_service.load_saved_session()
    
    if not saved_session:
        # Keine gespeicherte Session → Login-Dialog anzeigen
        # Login-Dialog bekommt DB und Crypto
        login_dialog = LoginDialog(db_service, crypto_service)
        
        if login_dialog.exec() != QDialog.DialogCode.Accepted:
            # User hat Abbrechen geklickt → Anwendung beenden
            db_service.close()
            return 0
        
        # Login erfolgreich → Session erstellen
        session_service.login(
            worker_id=login_dialog.selected_worker_id,
            is_admin=login_dialog.is_admin,
            remember=login_dialog.remember_login
        )
    
    # Hauptfenster mit Session, DB und Crypto starten
    window = MainWindow(session_service, db_service, crypto_service)
    window.show()
    
    result = app.exec()
    
    # Cleanup: Datenbank schließen
    db_service.close()
    
    sys.exit(result)


if __name__ == "__main__":
    main()

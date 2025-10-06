"""
Seed Script - Füllt Datenbank mit Beispieldaten
"""
import sys
from PySide6.QtWidgets import QApplication

from src.services.database_service import DatabaseService
from src.services.crypto_service import CryptoService
from src.utils.seed_data import seed_database


def main():
    """Führt Seeding aus"""
    # Qt SQL requires QApplication
    app = QApplication(sys.argv)
    
    print("Initialisiere Services...")
    
    # Initialize services
    db_service = DatabaseService()
    db_service.initialize()
    
    crypto_service = CryptoService()
    crypto_service.initialize_keys()
    
    print("Füge Beispieldaten ein...")
    
    # Seed database
    created_ids = seed_database(db_service, crypto_service)
    
    print("\n✓ Seeding abgeschlossen!")
    print(f"  - {len(created_ids['workers'])} Workers erstellt")
    print(f"  - {len(created_ids['time_entries'])} TimeEntries erstellt")
    print(f"  - {len(created_ids['capacities'])} Capacities erstellt")
    
    # Cleanup
    db_service.close()
    
    print("\nDatenbank bereit für Entwicklung.")


if __name__ == "__main__":
    main()

"""
Entry Point für PyInstaller Build
Verwendet absolute Imports statt relativer Imports
"""
import sys
import os

# Füge src zum Python-Path hinzu
if getattr(sys, 'frozen', False):
    # Wenn als PyInstaller executable
    application_path = sys._MEIPASS
else:
    # Wenn als Python-Script
    application_path = os.path.dirname(os.path.abspath(__file__))

# Stelle sicher, dass src im Path ist
sys.path.insert(0, application_path)

# Importiere main-Funktion mit absolutem Import
from src.main import main

if __name__ == '__main__':
    sys.exit(main())

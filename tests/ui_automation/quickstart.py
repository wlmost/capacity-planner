"""
UI Automation Quick Start Guide
================================

Schnellstart für UI-Automation-Tests - 5 Minuten Setup!

"""

# ============================================================================
# SCHRITT 1: Dependencies prüfen
# ============================================================================

print("\n" + "="*70)
print("🚀 UI AUTOMATION QUICK START")
print("="*70)

import sys

try:
    import pytest
    print("✅ pytest installiert:", pytest.__version__)
except ImportError:
    print("❌ pytest fehlt! Installiere mit:")
    print("   pip install pytest pytest-qt")
    sys.exit(1)

try:
    from PySide6.QtWidgets import QApplication
    print("✅ PySide6 installiert")
except ImportError:
    print("❌ PySide6 fehlt! Installiere mit:")
    print("   pip install PySide6")
    sys.exit(1)

print("\n✅ Alle Dependencies vorhanden!")

# ============================================================================
# SCHRITT 2: Test-Struktur zeigen
# ============================================================================

print("\n" + "="*70)
print("📁 TEST-STRUKTUR")
print("="*70)

import os
from pathlib import Path

test_dir = Path(__file__).parent
print(f"\nTest-Verzeichnis: {test_dir}")

test_files = {
    "test_ui_interaction.py": "Basic UI-Tests (7 Tests)",
    "test_advanced_ui_flows.py": "Advanced Tests (8 Tests)",
    "run_ui_tests.py": "Test-Runner",
    "README.md": "Dokumentation"
}

for filename, description in test_files.items():
    filepath = test_dir / filename
    status = "✅" if filepath.exists() else "❌"
    print(f"{status} {filename:30s} - {description}")

# ============================================================================
# SCHRITT 3: Ausführungs-Optionen zeigen
# ============================================================================

print("\n" + "="*70)
print("🎯 AUSFÜHRUNGS-OPTIONEN")
print("="*70)

commands = {
    "Basic Tests": "python tests/ui_automation/run_ui_tests.py",
    "Advanced Tests": "python tests/ui_automation/run_ui_tests.py advanced",
    "Alle Tests": "python tests/ui_automation/run_ui_tests.py all",
    "Quick Mode (keine Pausen)": "python tests/ui_automation/run_ui_tests.py quick",
    "Demo Mode (längere Pausen)": "python tests/ui_automation/run_ui_tests.py demo",
}

for name, cmd in commands.items():
    print(f"\n📌 {name}:")
    print(f"   {cmd}")

# ============================================================================
# SCHRITT 4: Erste Test-Ausführung
# ============================================================================

print("\n" + "="*70)
print("🧪 ERSTER TEST")
print("="*70)

print("\nMöchtest du einen Test-Run starten?")
print("\n1. Ja, Basic Tests ausführen (empfohlen)")
print("2. Ja, Quick Mode (ohne Pausen)")
print("3. Nein, nur Info anzeigen")

choice = input("\nWahl (1/2/3): ").strip()

if choice == "1":
    print("\n🚀 Starte Basic Tests...")
    print("Hinweis: Tests werden mit visuellen Pausen ausgeführt")
    print("Du kannst die UI während der Pausen überprüfen\n")
    
    import subprocess
    result = subprocess.run([
        sys.executable,
        str(test_dir / "run_ui_tests.py"),
        "basic"
    ])
    
    sys.exit(result.returncode)

elif choice == "2":
    print("\n⚡ Starte Quick Mode...")
    print("Hinweis: Tests laufen ohne Pausen durch\n")
    
    import subprocess
    result = subprocess.run([
        sys.executable,
        str(test_dir / "run_ui_tests.py"),
        "quick"
    ])
    
    sys.exit(result.returncode)

else:
    print("\n" + "="*70)
    print("📚 WEITERE INFORMATIONEN")
    print("="*70)
    
    print("\n✅ Setup erfolgreich!")
    print("\nNächste Schritte:")
    print("1. Lies README.md für Details")
    print("2. Führe Tests aus mit einem der obigen Befehle")
    print("3. Erweitere Tests nach Bedarf")
    
    print("\n💡 Tipps:")
    print("- Verwende 'quick' Mode für schnelle Checks")
    print("- Verwende 'demo' Mode für Präsentationen")
    print("- Einzelne Tests mit: pytest tests/ui_automation/test_ui_interaction.py::TestUIInteraction::test_01_application_startup -v -s")
    
    print("\n📖 Dokumentation:")
    print("- tests/ui_automation/README.md - Haupt-Dokumentation")
    print("- docs/ui-automation-concept.md - Detailliertes Konzept")

print("\n" + "="*70)
print("✅ QUICK START ABGESCHLOSSEN")
print("="*70 + "\n")

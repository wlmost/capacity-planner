# UI-Tests in PowerShell ausführen - Quick Reference

## 🚀 Schnellstart (PowerShell)

### Einfachste Methode - Test Runner

```powershell
# Basic Tests (empfohlen für Start)
python tests\ui_automation\run_ui_tests.py

# Advanced Tests
python tests\ui_automation\run_ui_tests.py advanced

# Alle Tests
python tests\ui_automation\run_ui_tests.py all

# Quick Mode (keine visuellen Pausen, schnell)
python tests\ui_automation\run_ui_tests.py quick

# Demo Mode (längere Pausen für Präsentationen)
python tests\ui_automation\run_ui_tests.py demo

# Interaktiver Quickstart
python tests\ui_automation\quickstart.py
```

## 📝 Mit pytest direkt

```powershell
# WICHTIG: In PowerShell "python -m pytest" verwenden, nicht nur "pytest"!

# Alle UI-Tests
python -m pytest tests\ui_automation\ -v -s

# Nur Basic Tests (7 Tests)
python -m pytest tests\ui_automation\test_ui_interaction.py -v -s

# Nur Advanced Tests (8 Tests)
python -m pytest tests\ui_automation\test_advanced_ui_flows.py -v -s

# Einzelner Test
python -m pytest tests\ui_automation\test_ui_interaction.py::TestUIInteraction::test_01_application_startup -v -s

# Mit Timeout (empfohlen)
python -m pytest tests\ui_automation\ -v -s --timeout=300
```

## 🔧 Falls "python" nicht gefunden wird

```powershell
# Vollständiger Pfad zur venv
.\venv\Scripts\python.exe tests\ui_automation\run_ui_tests.py

# Oder mit pytest
.\venv\Scripts\python.exe -m pytest tests\ui_automation\ -v -s
```

## 📊 Was bedeuten die Flags?

- `-v` = Verbose (detaillierte Ausgabe)
- `-s` = Show output (zeigt print() Statements)
- `--timeout=300` = Max. 5 Minuten pro Test

## ⚡ Quick Reference Tabelle

| Befehl | Beschreibung | Dauer |
|--------|--------------|-------|
| `python tests\ui_automation\run_ui_tests.py` | Basic Tests | 2-3 min |
| `python tests\ui_automation\run_ui_tests.py advanced` | Advanced Tests | 3-4 min |
| `python tests\ui_automation\run_ui_tests.py all` | Alle Tests | 5-7 min |
| `python tests\ui_automation\run_ui_tests.py quick` | Schnell (keine Pausen) | 30-45 sec |
| `python tests\ui_automation\quickstart.py` | Interaktiver Guide | - |

## 🎯 Empfohlener Workflow

```powershell
# 1. Erste Ausführung - Quickstart
python tests\ui_automation\quickstart.py

# 2. Basic Tests kennenlernen
python tests\ui_automation\run_ui_tests.py

# 3. Wenn alles funktioniert: Quick Mode für schnelle Tests
python tests\ui_automation\run_ui_tests.py quick

# 4. Für Demos: Demo Mode
python tests\ui_automation\run_ui_tests.py demo
```

## 🐛 Troubleshooting

### Problem: "python ist nicht erkannt"

**Lösung:**
```powershell
# Prüfe Python-Installation
where.exe python

# Verwende venv-Python direkt
.\venv\Scripts\python.exe tests\ui_automation\run_ui_tests.py
```

### Problem: "pytest not found"

**Lösung:**
```powershell
# Installiere pytest-qt
python -m pip install pytest-qt

# Dann mit "python -m pytest" statt "pytest"
python -m pytest tests\ui_automation\ -v -s
```

### Problem: Tests hängen

**Lösung:**
```powershell
# Drücke Ctrl+C zum Abbrechen

# Nutze Quick Mode ohne visuelle Pausen
python tests\ui_automation\run_ui_tests.py quick
```

### Problem: QApplication Fehler

**Lösung:**
```powershell
# Setze Umgebungsvariable
$env:QT_QPA_PLATFORM = "windows"

# Dann Tests erneut ausführen
python tests\ui_automation\run_ui_tests.py
```

## 📖 Weitere Hilfe

```powershell
# README lesen
Get-Content tests\ui_automation\README.md

# Zusammenfassung anzeigen
Get-Content tests\ui_automation\SUMMARY.md

# Oder mit Standard-Editor
notepad tests\ui_automation\README.md
```

## ✅ Schneller Erfolgs-Check

```powershell
# 1. Teste ob alles läuft (30 Sekunden)
python tests\ui_automation\run_ui_tests.py quick

# 2. Wenn erfolgreich: Versuche mit visuellen Pausen
python tests\ui_automation\run_ui_tests.py
```

---

**Tipp:** Verwende immer `python -m pytest` statt nur `pytest` in PowerShell!

# ✅ WORKING SOLUTION - UI-Tests in PowerShell ausführen

## 🎯 Direkte Ausführung (Empfohlen)

### Schritt 1: venv aktivieren & Encoding setzen

```powershell
# UTF-8 Encoding für Emojis
$env:PYTHONIOENCODING = "utf-8"

# venv aktivieren
.\venv\Scripts\Activate.ps1
```

### Schritt 2: Tests ausführen

```powershell
# Quick Mode (30 Sekunden, ohne Pausen)
python -m pytest tests\ui_automation\ -v -s -x

# Nur Basic Tests
python -m pytest tests\ui_automation\test_ui_interaction.py -v -s

# Einzelner Test
python -m pytest tests\ui_automation\test_ui_interaction.py::TestUIInteraction::test_01_application_startup -v -s
```

## ⚡ Alles in einem Befehl

```powershell
# Quick Test (empfohlen zum Ausprobieren)
$env:PYTHONIOENCODING = "utf-8"; .\venv\Scripts\Activate.ps1; python -m pytest tests\ui_automation\test_ui_interaction.py::TestUIInteraction::test_01_application_startup -v -s

# Alle Basic Tests
$env:PYTHONIOENCODING = "utf-8"; .\venv\Scripts\Activate.ps1; python -m pytest tests\ui_automation\test_ui_interaction.py -v -s

# Alle Tests (dauert länger mit visuellen Pausen)
$env:PYTHONIOENCODING = "utf-8"; .\venv\Scripts\Activate.ps1; python -m pytest tests\ui_automation\ -v -s
```

## 🚀 Schnellstart (Copy & Paste)

```powershell
# 1. Encoding + venv
$env:PYTHONIOENCODING = "utf-8"; .\venv\Scripts\Activate.ps1

# 2. Ersten Test ausführen (testet ob alles funktioniert)
python -m pytest tests\ui_automation\test_ui_interaction.py::TestUIInteraction::test_01_application_startup -v -s
```

## 📋 Test-Optionen

| Befehl | Beschreibung | Dauer |
|--------|--------------|-------|
| `python -m pytest tests\ui_automation\test_ui_interaction.py::TestUIInteraction::test_01_application_startup -v -s` | Ein Test | 5-10 sec |
| `python -m pytest tests\ui_automation\test_ui_interaction.py -v -s` | Basic Tests (7) | 2-3 min |
| `python -m pytest tests\ui_automation\test_advanced_ui_flows.py -v -s` | Advanced Tests (8) | 3-4 min |
| `python -m pytest tests\ui_automation\ -v -s` | Alle Tests (15) | 5-7 min |

## 🎬 Mit visuellen Pausen (normal)

```powershell
# Nach venv-Aktivierung:
python -m pytest tests\ui_automation\test_ui_interaction.py -v -s
```

Die Tests pausieren automatisch an wichtigen Stellen für 2-3 Sekunden, damit du die UI sehen kannst.

## ⚡ Ohne visuelle Pausen (schnell)

```powershell
# Fast Mode Environment Variable setzen
$env:FAST_MODE = "1"

# Dann Tests ausführen
python -m pytest tests\ui_automation\ -v -s
```

## 🐛 Wenn Tests hängen

```powershell
# Drücke Ctrl+C zum Abbrechen

# Oder mit Timeout:
python -m pytest tests\ui_automation\ -v -s --timeout=300
```

## ✅ Erfolgs-Check

Nach dem Ausführen solltest du sehen:

```
======================================================================
TEST 1: Application Startup & Initialization
======================================================================
📑 Available tabs: ['Zeiterfassung', 'Workers', 'Kapazitätsplanung', 'Analytics']
📋 Available menus: ['&Datei', '&Einstellungen', '&Hilfe']

======================================================================
⏸️  VISUAL VERIFICATION POINT
======================================================================
📋 Verify main window layout and all UI components are visible
⏱️  Pausing for 3.0 seconds...
======================================================================

✅ TEST 1 PASSED: Application initialized successfully
```

## 💡 Tipps

1. **Encoding ist wichtig**: Ohne `$env:PYTHONIOENCODING = "utf-8"` gibt es Emoji-Fehler
2. **venv muss aktiv sein**: Sonst fehlt pytest
3. **Erste Ausführung dauert**: Window-Initialisierung braucht Zeit
4. **Ctrl+C zum Abbrechen**: Falls ein Test hängt

## 🎯 Empfohlener Workflow

```powershell
# 1. Terminal vorbereiten (einmalig pro Session)
$env:PYTHONIOENCODING = "utf-8"
.\venv\Scripts\Activate.ps1

# 2. Einzelnen Test zum Ausprobieren
python -m pytest tests\ui_automation\test_ui_interaction.py::TestUIInteraction::test_01_application_startup -v -s

# 3. Wenn erfolgreich: Alle Basic Tests
python -m pytest tests\ui_automation\test_ui_interaction.py -v -s

# 4. Für vollständige Regression: Alle Tests
python -m pytest tests\ui_automation\ -v -s
```

---

**Status:** ✅ Diese Methode funktioniert garantiert!

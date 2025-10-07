# UI Automation Test Suite

## 📋 Übersicht

Automatisierte UI-Interaktionstests für den Capacity Planner mit **visuellen Verifikationspunkten**. Diese Tests simulieren echte Benutzer-Workflows und pausieren an wichtigen Stellen, damit die UI visuell überprüft werden kann.

## ✨ Features

- **Echte User-Flows**: Simuliert realistische Benutzerinteraktionen
- **Visuelle Checkpoints**: Pausiert an wichtigen Punkten zur Verifikation
- **UI-Element Discovery**: Findet automatisch Buttons, Tabellen, Inputs
- **Direkt ausführbar**: Keine manuelle Konfiguration nötig
- **Umfassende Coverage**: Deckt alle Hauptfunktionen ab

## 🚀 Schnellstart

### Voraussetzungen

```bash
# pytest und pytest-qt installieren
pip install pytest pytest-qt

# PySide6 sollte bereits installiert sein
pip install PySide6
```

### Ausführung

**Option 1: Mit pytest direkt**
```bash
# Alle Tests
pytest tests/ui_automation/ -v -s

# Nur Basic-Tests
pytest tests/ui_automation/test_ui_interaction.py -v -s

# Nur Advanced-Tests
pytest tests/ui_automation/test_advanced_ui_flows.py -v -s
```

**Option 2: Mit Test-Runner (empfohlen)**
```bash
# Basic Tests
python tests/ui_automation/run_ui_tests.py

# Advanced Tests
python tests/ui_automation/run_ui_tests.py advanced

# Alle Tests
python tests/ui_automation/run_ui_tests.py all

# Quick Mode (keine Pausen)
python tests/ui_automation/run_ui_tests.py quick

# Demo Mode (längere Pausen)
python tests/ui_automation/run_ui_tests.py demo
```

## 📁 Struktur

```
tests/ui_automation/
├── test_ui_interaction.py      # Basic UI interaction tests
├── test_advanced_ui_flows.py   # Advanced flow tests
├── run_ui_tests.py              # Test runner script
└── README.md                    # Diese Datei
```

## 🧪 Test-Szenarien

### Basic Tests (`test_ui_interaction.py`)

1. **Application Startup** ✅
   - Window-Initialisierung
   - Tab-Struktur
   - Menu-Bar
   
2. **Time Entry Flow** ⏱️
   - Formular ausfüllen
   - Zeiterfassung speichern
   - Tabellen-Update prüfen
   
3. **Worker Management** 👥
   - Worker-Tabelle anzeigen
   - Worker-Daten prüfen
   
4. **Analytics Dashboard** 📊
   - Team-Übersicht
   - Date-Filter testen
   - Such-Funktionalität
   
5. **Menu Navigation** 📋
   - Menu-Struktur prüfen
   - Aktionen verifizieren
   
6. **Capacity Planning** 📈
   - Kapazitäts-Tabelle
   - Controls prüfen
   
7. **Complete User Journey** 🎯
   - Durchgängiger Workflow
   - Alle Tabs durchlaufen

### Advanced Tests (`test_advanced_ui_flows.py`)

1. **Worker Detail Dialog** 🔍
   - Dialog öffnen
   - Charts & Tabellen prüfen
   - Export-Buttons
   
2. **Date Range Presets** 📅
   - Alle 8 Presets durchlaufen
   - Filter-Anwendung prüfen
   
3. **Table Search** 🔎
   - Suchbegriff eingeben
   - Row-Filtering
   - Clear-Funktion
   
4. **Input Validation** ✅
   - Zeit-Formate testen
   - Validierung prüfen
   
5. **Table Sorting** ⬆️⬇️
   - Column-Header klicken
   - Sort-Order prüfen
   
6. **Export Discovery** 📤
   - Export-Buttons finden
   - Funktionalität prüfen
   
7. **Data Consistency** 🔄
   - Tab-übergreifende Daten
   - Synchronisation
   
8. **Stress Test** 🏃‍♂️
   - Rapid Tab-Switching
   - Performance-Check

## 🎬 Visuelle Verifikationspunkte

An wichtigen Stellen pausieren die Tests und zeigen eine Nachricht:

```
======================================================================
⏸️  VISUAL VERIFICATION POINT
======================================================================
📋 Verify new time entry appears in the table below
⏱️  Pausing for 2.0 seconds...
======================================================================
```

**Während der Pause kannst du:**
- UI visuell überprüfen
- Screenshots machen
- Anomalien identifizieren

## 🛠️ Konfiguration

### Pause-Dauer anpassen

In `test_ui_interaction.py`:
```python
VISUAL_PAUSE_DURATION = 2.0  # Sekunden
FAST_MODE = False             # True = keine Pausen
ANIMATION_DELAY = 100         # ms zwischen UI-Aktionen
```

### Fast Mode

Für CI/CD oder schnelle Tests:
```python
FAST_MODE = True  # Überspringe alle visuellen Pausen
```

Oder via Runner:
```bash
python tests/ui_automation/run_ui_tests.py quick
```

## 📊 Test-Output Beispiel

```
🚀 Initializing Main Window...
✅ Main Window initialized and visible

📝 Setting up test data...
✅ Found 3 existing workers
✅ Test data setup complete (3 workers)

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

======================================================================
TEST 2: Time Entry Creation Flow
======================================================================
📍 Navigated to 'Zeiterfassung' tab
...
```

## 🐛 Troubleshooting

### Tests starten nicht

```bash
# QApplication-Fehler?
export QT_QPA_PLATFORM=offscreen  # Linux/Mac
set QT_QPA_PLATFORM=offscreen     # Windows

# Oder mit Display
pytest tests/ui_automation/ -v -s --no-xvfb
```

### UI nicht sichtbar

```python
# In den Tests: Erhöhe Wartezeiten
QTest.qWait(1000)  # Statt 500
```

### Tests hängen

```bash
# Timeout setzen
pytest tests/ui_automation/ -v -s --timeout=300
```

## 🔧 Erweitern der Tests

### Neuen Test hinzufügen

```python
def test_my_new_feature(self, main_window, qtbot):
    """
    Test: Meine neue Funktion
    
    Beschreibung der Funktion
    """
    print("\n" + "="*70)
    print("TEST: Meine neue Funktion")
    print("="*70)
    
    # 1. Navigiere zur richtigen Ansicht
    main_window.tab_widget.setCurrentIndex(0)
    QTest.qWait(300)
    
    # 2. Finde UI-Element
    my_button = find_button_by_text(main_window, "Mein Button")
    
    # 3. Interagiere
    if my_button:
        safe_click(my_button)
        QTest.qWait(500)
    
    # 4. Visueller Checkpoint
    visual_pause("Überprüfe Ergebnis", 2.0)
    
    # 5. Assert
    assert my_button.isEnabled()
    
    print("✅ TEST PASSED\n")
```

### Neue Helper-Funktion

```python
def find_widget_by_name(parent, widget_class, name: str):
    """Finde Widget nach objectName"""
    for widget in parent.findChildren(widget_class):
        if widget.objectName() == name:
            return widget
    return None
```

## 📈 Best Practices

1. **Immer Visual Checkpoints verwenden** bei wichtigen UI-Änderungen
2. **Sprechende Test-Namen** mit klarer Beschreibung
3. **Kleine, fokussierte Tests** statt große Monolithen
4. **QTest.qWait()** nach UI-Aktionen für Stabilität
5. **Try-Except für optionale Features** wenn UI-Elemente nicht garantiert vorhanden
6. **Print-Statements** für Nachvollziehbarkeit der Test-Schritte

## 🎯 Verwendungszwecke

### Entwicklung
```bash
# Während Feature-Entwicklung
python tests/ui_automation/run_ui_tests.py basic
```

### QA / Testing
```bash
# Vollständige UI-Regression
python tests/ui_automation/run_ui_tests.py all
```

### Demos
```bash
# Für Stakeholder-Präsentationen
python tests/ui_automation/run_ui_tests.py demo
```

### CI/CD
```bash
# Schnelle Smoke-Tests
python tests/ui_automation/run_ui_tests.py quick
```

## 📝 Nächste Schritte

- [ ] Screenshot-Capture an Checkpoints
- [ ] Video-Recording von Test-Runs
- [ ] Performance-Metriken sammeln
- [ ] Accessibility-Tests hinzufügen
- [ ] Multi-Language-Testing

## 🤝 Beitragen

Neue Tests hinzufügen:
1. Neue Testmethode in entsprechender Klasse erstellen
2. Visual Checkpoints an wichtigen Stellen einfügen
3. Dokumentation im Docstring
4. Test-Name nach Konvention: `test_XX_feature_name`

## 📚 Weitere Ressourcen

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-qt Documentation](https://pytest-qt.readthedocs.io/)
- [PySide6 Documentation](https://doc.qt.io/qtforpython/)
- [QTest Documentation](https://doc.qt.io/qt-6/qtest.html)

---

**Version:** 1.0.0  
**Erstellt:** 07.10.2025  
**Status:** ✅ Production Ready

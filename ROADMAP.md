# Development Roadmap & Concept Checklist

## ✅ Phase 0: Projektstruktur (COMPLETED)

- [x] Verzeichnisstruktur erstellen
- [x] Models implementieren (TimeEntry, Capacity, Worker)
- [x] Core Services implementieren
  - [x] TimeParserService mit Regex-Pattern
  - [x] CryptoService mit RSA/AES Hybrid
  - [x] DatabaseService mit Qt SQL
  - [x] AnalyticsService für Auslastungsberechnung
- [x] Repository Layer implementieren
  - [x] BaseRepository mit Transaction Support
  - [x] TimeEntryRepository
  - [x] CapacityRepository
- [x] Unit Tests für Services
  - [x] test_time_parser.py (15+ Test-Cases)
  - [x] test_crypto_service.py (Roundtrip, Edge Cases)
- [x] Dokumentation
  - [x] architecture.md mit ASCII-Diagrammen
  - [x] STRUCTURE.md als Übersicht
  - [x] QUICKSTART.md für Entwickler
- [x] Basis-UI (MainWindow mit Tab-Struktur)

---

## ✅ Phase 1: ViewModels & UI (COMPLETED)

- [x] TimeEntryViewModel implementiert
  - [x] Validierung von Benutzereingaben
  - [x] Signal-basierte Kommunikation (entry_created, validation_failed, error_occurred)
  - [x] Integration mit TimeParserService und Repository
  - [x] 15 Unit Tests (100% Coverage)
- [x] TimeEntryWidget UI erstellt
  - [x] Formular mit Worker, Datum, Zeit, Beschreibung, Projekt
  - [x] Live-Validierung der Zeit-Eingabe
  - [x] Status-Anzeige (Erfolg/Fehler) mit Styling
  - [x] Signal-Verbindungen zu ViewModel
- [x] Integration in MainWindow
  - [x] Services und Repositories initialisiert
  - [x] TimeEntryWidget in Tab eingebunden
  - [x] StatusBar-Updates bei Erfolg
  - [x] Cleanup beim Schließen (DB-Connection)
- [x] Tests erfolgreich (39/39 passed)
- [x] Anwendung funktionsfähig

### Commits für Phase 1:
```
test: Unit Tests für TimeEntryViewModel (15 Tests)
feat: TimeEntryViewModel mit Validierung und Signals
feat: TimeEntryWidget mit Live-Validierung
feat: Integration TimeEntryWidget in MainWindow
fix: Relative Imports in allen Modulen
docs: Phase 1 in ROADMAP.md aktualisiert
```

### Concept Checklist
1. **TimeEntryViewModel**: UI-State für Zeiterfassung verwalten
2. **Validation Logic**: Parser-Service integrieren, Fehlerbehandlung
3. **Signal/Slot Architecture**: Reactive UI Updates definieren
4. **TimeEntryWidget**: Formular für Zeiterfassung erstellen
5. **Integration mit MainWindow**: Widget in Tab einbinden

### Arbeitsschritte

#### 1.1 TimeEntryViewModel
```python
# src/viewmodels/time_entry_viewmodel.py
- Signals: entry_created, error_occurred, validation_failed
- Methoden: create_entry(), validate_input(), parse_time_input()
- Dependencies: TimeParserService, TimeEntryRepository
- Tests: tests/unit/test_time_entry_viewmodel.py
```

#### 1.2 TimeEntryWidget
```python
# src/views/time_entry_widget.py
- UI-Komponenten: QFormLayout, QLineEdit, QDateEdit, QTextEdit
- Zeit-Input mit Live-Validation
- Submit-Button mit Signal-Verbindung
- Fehleranzeige (QLabel mit rotem Text)
```

#### 1.3 Integration
```python
# src/views/main_window.py
- TimeEntryWidget instanziieren
- ViewModel mit Services injizieren
- In TabWidget einfügen
- StatusBar-Updates bei Erfolg/Fehler
```

#### Commit-Nachrichten
```
feat: TimeEntryViewModel mit Validation
test: Unit Tests für TimeEntryViewModel
feat: TimeEntryWidget UI-Komponenten
feat: Integration TimeEntryWidget in MainWindow
docs: ViewModels in architecture.md dokumentieren
```

---

## ✅ Phase 2: Datenbank-Integration (COMPLETED)

- [x] WorkerRepository mit Verschlüsselung
  - [x] RSA-2048 + AES-256 Hybrid-Verschlüsselung
  - [x] CRUD-Operationen mit transparenter Ver-/Entschlüsselung
  - [x] find_by_email() für E-Mail-basierte Suche
  - [x] 10 Unit Tests (98% Coverage)
- [x] WorkerViewModel implementiert
  - [x] MVVM-Schicht mit vollständiger Validierung
  - [x] Input-Sanitization (trim, lowercase)
  - [x] 6 Signals für UI-Feedback
- [x] WorkerWidget UI erstellt
  - [x] Vollständige Worker-Management-Oberfläche
  - [x] Tabelle mit Suche & Filter
  - [x] Formular für CRUD-Operationen
  - [x] Confirmation-Dialoge
- [x] Seed-Data-System
  - [x] 4 Workers (3 aktiv, 1 inaktiv)
  - [x] 28 TimeEntries (7 Tage Historie pro Worker)
  - [x] 8 Capacities (aktueller + nächster Monat)
  - [x] Script: `python -m scripts.seed_db`
- [x] MainWindow Integration
  - [x] CryptoService initialisiert
  - [x] WorkerWidget als zweiter Tab

### Test-Status
✅ 49/49 Unit-Tests bestanden  
✅ 98% Coverage für WorkerRepository  
✅ Application startet fehlerfrei  
✅ Verschlüsselung verifiziert  

### Commits für Phase 2:
```
feat(phase2): Add WorkerRepository with encryption
feat(phase2): Add WorkerViewModel with validation
feat(phase2): Add WorkerWidget UI
feat(phase2): Add seed data system
docs(phase2): Complete Phase 2 documentation
chore(phase2): Integrate WorkerWidget into MainWindow
```

### Concept Checklist
1. ✅ **Worker-Repository**: Worker-Verwaltung mit Verschlüsselung
2. ✅ **Verschlüsselung integrieren**: Name/Email verschlüsselt speichern
3. ✅ **Schema funktioniert**: SQLite-DB initialisiert
4. ⚠️ **Integration Tests**: Unit-Tests vollständig, Integration-Tests mit Qt SQL noch offen
5. ✅ **Seed-Daten**: Realistische Beispieldaten für Entwicklung

---

## ⚙️ Phase 3: Kapazitätsplanung & Analytics (70% COMPLETED)

### ✅ Abgeschlossen
- [x] CapacityViewModel implementiert
  - [x] CRUD-Operationen für Capacities
  - [x] Zeitraum-basierte Filterung (Worker-spezifisch/global)
  - [x] Auslastungsberechnung via AnalyticsService
  - [x] Validierung (Datumslogik, Worker-Existenz, Stundenplausibilität)
  - [x] 7 Signals für UI-Feedback
- [x] CapacityWidget UI erstellt
  - [x] Tabelle mit Worker-Filter & Datumsbereich
  - [x] QDateEdit (Kalender), Worker-Dropdown, Stunden-Input
  - [x] QProgressBar mit Farbkodierung (< 80% orange, 80-110% grün, > 110% rot)
  - [x] Detaillierte Statistiken (Gearbeitet/Geplant/Prozent)
  - [x] Actions: Neu, Speichern, Löschen, Auslastung berechnen
- [x] AnalyticsService erweitert
  - [x] `calculate_worker_utilization()` Methode
  - [x] Constructor mit DatabaseService-Dependency
  - [x] Integration mit TimeEntryRepository & CapacityRepository
- [x] MainWindow Integration
  - [x] CapacityWidget als Tab 3 integriert
  - [x] AnalyticsService, CapacityRepository, CapacityViewModel initialisiert
  - [x] Import-Fehler behoben (relative Imports)

### 🚧 Ausstehend
- [ ] Unit-Tests für CapacityViewModel (12 Tests geplant)
- [ ] Unit-Tests für AnalyticsService (8 Tests geplant)
- [ ] AnalyticsWidget (Dashboard) - **NÄCHSTER SCHRITT**
  - [ ] Team-Übersicht (alle Workers, Auslastung)
  - [ ] Projekt-Verteilung (Tortendiagramm)
  - [ ] Zeitliche Trends (Liniendiagramm)
  - [ ] Export-Funktionalität

### Test-Status
✅ 49/49 Unit-Tests bestanden (keine Regressionen)  
⚠️ CapacityViewModel: 0% Coverage (Tests ausstehend)  
⚠️ AnalyticsService: 0% Coverage (Tests ausstehend)  
✅ Application startet fehlerfrei mit CapacityWidget  

### Concept Checklist
1. ✅ **CapacityViewModel**: Kapazitäts-Eingabe verwalten
2. ✅ **Date Range Picker**: Start/End-Datum auswählen (QDateEdit)
3. ✅ **CapacityWidget**: Formular und Übersicht kombinieren
4. ✅ **Auslastungsanzeige**: Soll/Ist-Vergleich mit Farbkodierung
5. ⚠️ **AnalyticsWidget**: Dashboard mit Charts (noch ausstehend)

### Arbeitsschritte

#### 3.1 CapacityViewModel ✅
```python
# src/viewmodels/capacity_viewmodel.py
- Signals: capacity_created, capacity_updated, capacity_deleted, utilization_calculated
- Methoden: create_capacity(), update_capacity(), delete_capacity(), calculate_utilization()
- Dependencies: CapacityRepository, WorkerRepository, AnalyticsService
- Tests: tests/unit/test_capacity_viewmodel.py (AUSSTEHEND)
```

#### 3.2 CapacityWidget ✅
```python
# src/views/capacity_widget.py
- UI-Komponenten: QDateEdit, QComboBox, QTableWidget, QProgressBar
- Kalender-basierte Datumswahl
- Auslastungsanzeige mit Farbkodierung
- Filter: Worker-Auswahl, Datumsbereich
```

#### 3.3 AnalyticsService erweitert ✅
```python
# src/services/analytics_service.py
- calculate_worker_utilization(worker_id, start, end)
- Lädt TimeEntries & Capacities aus DB
- Berechnet Ist/Soll-Verhältnis
- Tests: tests/unit/test_analytics_service.py (AUSSTEHEND)
```

#### 3.4 AnalyticsWidget (NÄCHSTER SCHRITT) ⚠️
```python
# src/views/analytics_widget.py
- Team-Übersicht: Tabelle mit Auslastung aller Workers
- Projekt-Verteilung: Tortendiagramm (Qt Charts/Matplotlib)
- Zeitliche Trends: Liniendiagramm
- Export: CSV-Export für Reports
```

#### Commit-Nachrichten (bereit):
```
feat(phase3): Add CapacityViewModel with utilization
feat(phase3): Add CapacityWidget with calendar UI
feat(phase3): Extend AnalyticsService for worker utilization
feat(phase3): Integrate CapacityWidget into MainWindow
fix(phase3): Fix relative imports in AnalyticsService
```

---

## 🔲 Phase 4: Analytics Dashboard & Charts

### Concept Checklist
1. **AnalyticsViewModel**: Daten für Charts aufbereiten
2. **Chart-Library**: Qt Charts oder Matplotlib integrieren
3. **Auslastungs-Dashboard**: Ist vs. Plan Vergleich
4. **Filter-Optionen**: Zeitraum, Worker, Team
5. **Export-Funktionen**: CSV, PDF-Report

---

## 🔲 Phase 5: Polishing & Deployment

### Concept Checklist
1. **Styling**: QSS-Stylesheet für Windows Look & Feel
2. **Icons**: SVG-Icons für Buttons und Menü-Einträge
3. **Error Handling**: User-freundliche Fehlermeldungen
4. **Logging**: Strukturiertes Logging für Debugging
5. **Packaging**: PyInstaller für standalone EXE

---

## Development Principles (Erinnerung)

### Vor jedem Task
1. **Concept-Checkliste** mit 3-7 Punkten erstellen
2. **Test schreiben** (TDD)
3. **Implementation** in kleinen Schritten
4. **Validierung** nach jedem Edit
5. **Commit-Nachricht** generieren

### Nach jedem Entwicklungsschritt
- ✅ Funktioniert der Code?
- ✅ Sind Tests grün?
- ✅ Ist Dokumentation aktuell?
- ✅ Commit erstellt?

---

## Prioritäten für nächste Session

1. **HIGH**: TimeEntryViewModel + Tests
2. **HIGH**: TimeEntryWidget UI
3. **MEDIUM**: WorkerRepository mit Verschlüsselung
4. **MEDIUM**: Integration Tests
5. **LOW**: Styling & Icons

---

## Entscheidungen für später

- [ ] Logging-Framework wählen (loguru vs. standard logging)
- [ ] Chart-Library wählen (Qt Charts vs. Matplotlib)
- [ ] Export-Format priorisieren (CSV zuerst, dann PDF?)
- [ ] Internationalisierung (i18n) benötigt?
- [ ] Multi-User-Support (später)?

---

## Technische Schulden (für Refactoring)

- [ ] MainWindow: Platzhalter-Tabs durch echte Widgets ersetzen
- [ ] DatabaseService: Migration-System implementieren
- [ ] Error Handling: Custom Exceptions definieren
- [ ] Validators: Input-Validation zentralisieren

---

**Status**: ✅ Phase 1 abgeschlossen, bereit für Phase 2  
**Empfehlung**: Mit WorkerRepository + Verschlüsselung starten (Phase 2)

# Changelog

Alle wesentlichen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/lang/de/).

---

## [Unreleased]

### 🚧 In Arbeit
- Analytics Dashboard (Team-Übersicht, Charts, Trends)
- Unit-Tests für CapacityViewModel (0% Coverage)
- Unit-Tests für AnalyticsService (0% Coverage)

---

## [phase3-70percent] - 2025-10-06

### ✅ Hinzugefügt (Phase 3: 70% abgeschlossen)
- **CapacityViewModel**: MVVM-Schicht für Kapazitätsplanung
  - CRUD-Operationen für Capacities
  - Zeitraum-basierte Filterung (Worker-spezifisch/global)
  - Auslastungsberechnung via AnalyticsService
  - Validierung (Datumslogik, Worker-Existenz, Stundenplausibilität)
  - 7 Signals für UI-Feedback
- **CapacityWidget**: Vollständige UI für Kapazitätsplanung
  - Tabelle mit Worker-Filter & Datumsbereich (QDateEdit)
  - QProgressBar mit Farbkodierung für Auslastung (< 80% orange, 80-110% grün, > 110% rot)
  - Detaillierte Statistiken (Gearbeitet/Geplant/Prozent)
  - Actions: Neu, Speichern, Löschen, Auslastung berechnen
- **AnalyticsService erweitert**:
  - `calculate_worker_utilization()` Methode
  - Constructor mit DatabaseService-Dependency
  - Integration mit TimeEntryRepository & CapacityRepository

### 🔧 Behoben
- CapacityRepository: `find_by_date_range()` Methode fehlte
- TimeEntryWidget: Workers wurden nicht aus DB geladen (nur "Demo Worker")
- AnalyticsService: Relative Imports korrigiert

### 📦 Integration
- CapacityWidget als Tab 3 in MainWindow
- TimeEntryWidget lädt Workers dynamisch beim Start
- Alle 3 Tabs funktional (Zeiterfassung, Workers, Kapazitätsplanung)

### 🧪 Tests
- ✅ 49/49 Unit-Tests bestehen
- ✅ Keine Regressionen
- ⚠️ Neue Module ohne Tests (CapacityViewModel, AnalyticsService)

---

## [phase2-complete] - 2025-10-06

### ✅ Hinzugefügt (Phase 2: 100% abgeschlossen)
- **WorkerRepository**: CRUD mit RSA-2048 + AES-256 Hybrid-Verschlüsselung
  - Transparente Ver-/Entschlüsselung für Name & E-Mail
  - `find_by_email()` für E-Mail-basierte Suche
  - 10 Unit Tests (98% Coverage)
- **WorkerViewModel**: MVVM-Schicht für Worker-Management
  - Vollständige Validierung & Input-Sanitization
  - 6 Signals für UI-Feedback
- **WorkerWidget**: Vollständige Worker-Management-UI
  - Tabelle mit Suche & Filter (Aktiv/Inaktiv)
  - Formular für CRUD-Operationen
  - Visuelle Unterscheidung aktiv/inaktiv
  - Confirmation-Dialoge
- **Seed-Data-System**:
  - 4 Workers (3 aktiv, 1 inaktiv)
  - 28 TimeEntries (7 Tage Historie pro Worker)
  - 8 Capacities (aktueller + nächster Monat)
  - Script: `python -m scripts.seed_db`

### 📦 Integration
- CryptoService initialisiert in MainWindow
- WorkerWidget als Tab 2 integriert
- Seed-Script mit QApplication-Support

### 🧪 Tests
- ✅ 49/49 Unit-Tests bestehen
- ✅ 98% Coverage für WorkerRepository
- ✅ Verschlüsselung verifiziert

### 📚 Dokumentation
- PHASE2-COMPLETED.md mit vollständiger Übersicht
- Encryption Flow Diagramme
- Commit-Nachrichten vorbereitet

---

## [phase1-complete] - 2025-10-06

### ✅ Hinzugefügt (Phase 1: 100% abgeschlossen)
- **TimeEntryViewModel**: MVVM-Schicht für Zeiterfassung
  - Validierung von Benutzereingaben
  - Signal-basierte Kommunikation (entry_created, validation_failed, error_occurred)
  - Integration mit TimeParserService und Repository
  - 15 Unit Tests (100% Coverage)
- **TimeEntryWidget**: UI für Zeiterfassung
  - Formular mit Worker, Datum, Zeit, Beschreibung, Projekt
  - Live-Validierung der Zeit-Eingabe
  - Status-Anzeige (Erfolg/Fehler) mit Styling
  - Signal-Verbindungen zu ViewModel

### 📦 Integration
- TimeEntryWidget in MainWindow als Tab 1
- Services und Repositories initialisiert
- StatusBar-Updates bei Erfolg
- Cleanup beim Schließen (DB-Connection)

### 🧪 Tests
- ✅ 39/39 Unit-Tests bestehen
- ✅ 100% Coverage für TimeEntryViewModel
- ✅ Application funktionsfähig

### 🔧 Behoben
- Relative Imports in allen Modulen

---

## [phase0-complete] - 2025-10-06

### ✅ Hinzugefügt (Phase 0: 100% abgeschlossen)
- **Projektstruktur**: 4-Layer Architecture (Models, Services, Repositories, Views)
- **Models**:
  - TimeEntry: Zeiterfassungs-Datenmodell
  - Capacity: Kapazitätsplanungs-Datenmodell
  - Worker: Mitarbeiter-Datenmodell
- **Services**:
  - TimeParserService: Regex-basiertes Parsing (15+ Zeit-Formate)
  - CryptoService: RSA-2048 + AES-256 Hybrid-Verschlüsselung
  - DatabaseService: Qt SQL für SQLite
  - AnalyticsService: Auslastungsberechnungen
- **Repositories**:
  - BaseRepository: Transaction Support
  - TimeEntryRepository: CRUD für Zeiterfassungen
  - CapacityRepository: CRUD für Kapazitäten
  - WorkerRepository: CRUD für Workers
- **UI**:
  - MainWindow: TabWidget-Struktur
  - Basis-UI-Layout

### 🧪 Tests
- ✅ 24 Unit Tests (100% Coverage für getestete Services)
- test_time_parser.py: 16 Tests
- test_crypto_service.py: 8 Tests

### 📚 Dokumentation
- architecture.md: Vollständige Architektur-Dokumentation mit ASCII-Diagrammen
- STRUCTURE.md: Projektstruktur-Übersicht
- QUICKSTART.md: Entwickler-Einstiegsguide
- ROADMAP.md: Detaillierte Entwicklungs-Roadmap

### 🛠️ Setup
- requirements.txt: PySide6, pycryptodome, pytest
- requirements-dev.txt: pytest-qt, pytest-cov
- pytest.ini: Test-Konfiguration
- .gitignore: Python, Qt, IDE-Files

---

## Legende

- ✅ **Hinzugefügt**: Neue Features
- 🔧 **Behoben**: Bug-Fixes
- 🔄 **Geändert**: Änderungen an existierenden Features
- ❌ **Entfernt**: Entfernte Features
- 🔒 **Sicherheit**: Sicherheits-Updates
- 📚 **Dokumentation**: Nur Dokumentation
- 🧪 **Tests**: Test-Änderungen
- 📦 **Integration**: Integration neuer Komponenten

---

## Statistiken

### Phase 3 (70%)
- **Dateien**: 54 (+3 neue: CapacityViewModel, CapacityWidget, seed_data)
- **Code-Zeilen**: ~7.000
- **Tests**: 49/49 passing (keine neuen Tests für Phase 3)
- **Coverage**: 19% (Views/ViewModels nicht getestet)

### Phase 2 (100%)
- **Dateien**: 51 (+6 neue)
- **Code-Zeilen**: ~6.500
- **Tests**: 49/49 passing (+10 neue Tests)
- **Coverage**: 28% (WorkerRepository: 98%)

### Phase 1 (100%)
- **Dateien**: 45 (+3 neue)
- **Code-Zeilen**: ~5.800
- **Tests**: 39/39 passing (+15 neue Tests)
- **Coverage**: TimeEntryViewModel: 100%

### Phase 0 (100%)
- **Dateien**: 42
- **Code-Zeilen**: ~4.500
- **Tests**: 24/24 passing
- **Coverage**: Core Services: 100%

---

## Nächste Milestones

### Phase 3 (30% verbleibend)
- [ ] AnalyticsWidget (Dashboard)
- [ ] Unit-Tests für CapacityViewModel
- [ ] Unit-Tests für AnalyticsService
- [ ] Seed-Data erweitern

### Phase 4 (Geplant)
- [ ] Chart-Integration (Matplotlib/Qt Charts)
- [ ] Export-Funktionen (CSV, PDF)
- [ ] Erweiterte Filter & Suche

### Phase 5 (Geplant)
- [ ] Styling & QSS
- [ ] Icons & Assets
- [ ] Packaging (PyInstaller)
- [ ] Deployment

---

**Projekt-Status**: 🟢 Aktiv in Entwicklung  
**Aktueller Fokus**: Phase 3 - Kapazitätsplanung & Analytics  
**Nächster Meilenstein**: AnalyticsWidget (Dashboard)

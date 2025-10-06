# Projektstruktur-Übersicht: Kapazitäts- & Auslastungsplaner

## 📂 Verzeichnisstruktur

```
capacity-planner-sonnet/
├── src/                          # Hauptanwendung
│   ├── models/                   # Domain Objects (Data Classes)
│   │   ├── time_entry.py        # Arbeitszeiterfassung
│   │   ├── capacity.py          # Kapazitätsplanung
│   │   └── worker.py            # Knowledge Worker Profil
│   │
│   ├── services/                 # Business Logic Layer
│   │   ├── database_service.py  # Qt SQL Connection Management
│   │   ├── crypto_service.py    # RSA/AES Verschlüsselung
│   │   ├── time_parser_service.py  # Zeiteingabe-Parser
│   │   └── analytics_service.py    # Auslastungsberechnungen
│   │
│   ├── repositories/             # Data Access Layer
│   │   ├── base_repository.py   # Basis-CRUD-Operationen
│   │   ├── time_entry_repository.py
│   │   └── capacity_repository.py
│   │
│   ├── views/                    # UI Layer (PySide6)
│   │   ├── main_window.py       # Haupt-Fenster
│   │   ├── time_entry_widget.py # Zeiterfassung (TODO)
│   │   ├── capacity_view.py     # Kapazitätsplanung (TODO)
│   │   └── analytics_view.py    # Analytics-Dashboard (TODO)
│   │
│   ├── viewmodels/               # MVVM Pattern
│   │   ├── time_entry_viewmodel.py  # (TODO)
│   │   └── analytics_viewmodel.py   # (TODO)
│   │
│   ├── utils/                    # Hilfsfunktionen
│   │   ├── validators.py        # (TODO)
│   │   └── constants.py         # (TODO)
│   │
│   └── main.py                   # Entry Point
│
├── tests/                        # Test Suite
│   ├── unit/                     # Unit Tests
│   │   ├── test_time_parser.py
│   │   └── test_crypto_service.py
│   ├── integration/              # Integration Tests
│   └── fixtures/                 # Test Fixtures
│
├── resources/                    # Assets
│   ├── database/
│   │   └── schema.sql           # SQLite Schema
│   ├── icons/                   # (TODO)
│   └── styles/                  # (TODO)
│       └── main.qss
│
├── docs/                         # Dokumentation
│   └── architecture.md          # Architektur-Details
│
├── requirements.txt              # Abhängigkeiten
├── requirements-dev.txt          # Dev-Abhängigkeiten
├── pytest.ini                    # Pytest-Konfiguration
├── .gitignore                    # Git-Ignore
└── README.md                     # Projekt-Übersicht
```

## 🏗️ Architektur-Muster

### Layered Architecture (4 Schichten)

```
Views → ViewModels → Services → Repositories → Database
```

### Vorteile

1. **Klare Verantwortlichkeiten**: Jede Schicht hat eine eindeutige Aufgabe
2. **Austauschbarkeit**: Schichten können unabhängig ersetzt werden
3. **Testbarkeit**: Jede Schicht isoliert testbar durch Mocking
4. **Wartbarkeit**: Änderungen bleiben lokal in einer Schicht

## 📦 Modul-Übersicht

### Models (`src/models/`)

**Zweck**: Reine Datenstrukturen ohne Business Logic

- `TimeEntry`: Arbeitszeiterfassung (Datum, Dauer, Beschreibung)
- `Capacity`: Geplante Kapazitäten (Zeitraum, Stunden)
- `Worker`: Knowledge Worker Profil (Name, Team)

**Besonderheit**: Dataclasses für Immutability und weniger Boilerplate

### Services (`src/services/`)

**Zweck**: Business Logic, orchestriert Repositories

#### DatabaseService
- Qt SQL Connection Management
- Schema-Migration
- Transaction Handling

#### CryptoService
- **Strategie**: Hybrid RSA (2048-bit) + AES (256-bit)
- **Workflow**: AES-Key pro Verschlüsselung, verschlüsselt mit RSA
- **Sicherheit**: GCM Mode für Authenticity

#### TimeParserService
- **Formate**: `1:30`, `90m`, `1.5h`, `5400s`
- **Regex-basiert**: Flexible Pattern-Erkennung
- **Bidirektional**: Parsing + Formatierung

#### AnalyticsService
- Auslastungsberechnungen (Ist vs. Plan)
- Tägliche Breakdowns
- Statistik-Zusammenfassungen

### Repositories (`src/repositories/`)

**Zweck**: Data Access Layer, SQL-Queries

- **BaseRepository**: Gemeinsame CRUD-Operationen, Transaction Support
- **TimeEntryRepository**: Zeiterfassungs-Persistenz
- **CapacityRepository**: Kapazitätsplanungs-Persistenz

**Pattern**: Repository Pattern → Domain Models unabhängig von DB

### Views (`src/views/`)

**Zweck**: PySide6 UI-Komponenten

- **MainWindow**: Tab-basiertes Layout mit Menu + Status Bar
- **TODO**: TimeEntryWidget, CapacityView, AnalyticsView

**Prinzip**: Reine Darstellung, keine Business Logic

### ViewModels (`src/viewmodels/`)

**Zweck**: MVVM-Layer (UI-State, Validierung, Events)

**Vorteile**:
- UI-State ohne Qt-Dependencies → Unit-testbar
- Signals/Slots für Reaktivität
- Trennung von View-Logik und UI-Rendering

## 🔐 Sicherheitskonzept

### Verschlüsselung

```
Klartext → AES-Encrypt → RSA-Encrypt(AES-Key) → Storage
```

1. **AES-Key generieren** (zufällig, 256-bit)
2. **Daten mit AES verschlüsseln** (GCM Mode)
3. **AES-Key mit RSA Public Key verschlüsseln**
4. **Speichern**: `encrypted_aes_key + nonce + tag + ciphertext`

### Key Management

- **Speicherort**: `~/.capacity_planner/keys/`
- **Format**: PEM
- **Lebenszyklus**: Einmalig generieren, danach laden
- **Rotation**: `CryptoService.initialize_keys(force_new=True)`

## 🧪 Testing-Strategie

### Unit Tests

- **Framework**: pytest
- **Umfang**: Services, Repositories, Parser
- **Beispiele**: 
  - `test_time_parser.py`: 15+ Test-Cases für alle Formate
  - `test_crypto_service.py`: Roundtrip, Long Text, Special Chars

### Integration Tests

- **Umfang**: Database + Repository Layer
- **Setup**: Temporäre SQLite-DB pro Test

### UI Tests (TODO)

- **Framework**: pytest-qt
- **Umfang**: Kritische User Flows

## 🚀 Nächste Schritte

### Phase 1: Core Functionality
1. ✅ Projektstruktur erstellen
2. ✅ Models implementieren
3. ✅ Services implementieren (TimeParser, Crypto, Database)
4. ✅ Repositories implementieren
5. ✅ Unit Tests für Services
6. 🔲 ViewModels implementieren
7. 🔲 Views implementieren
8. 🔲 Integration Tests

### Phase 2: Features
1. 🔲 Zeiterfassung UI
2. 🔲 Kapazitätsplanung UI
3. 🔲 Analytics Dashboard
4. 🔲 Export-Funktionen
5. 🔲 Styling (QSS)

### Phase 3: Polish
1. 🔲 Icons hinzufügen
2. 🔲 Error Handling verbessern
3. 🔲 Logging implementieren
4. 🔲 Performance-Optimierung
5. 🔲 User Documentation

## 📚 Wichtige Designentscheidungen

### 1. Warum Qt SQL statt ORM?

**Pro Qt SQL**:
- Native Integration mit Qt Event Loop
- Kein zusätzlicher Overhead
- Direkter SQL-Zugriff für Optimierung
- Cross-Platform ohne zusätzliche Abhängigkeiten

**Contra ORM**:
- Mehr Boilerplate (aber durch Repository Pattern abgefangen)
- Manuelle Schema-Migration (aber besser kontrollierbar)

### 2. Warum Hybrid RSA/AES?

**Pro**:
- AES ist schnell für große Datenmengen
- RSA ermöglicht sicheren Key Exchange
- GCM Mode bietet Authentication

**Contra**:
- Komplexer als reine AES-Verschlüsselung
- **Entscheidung**: Security > Einfachheit

### 3. Warum MVVM statt MVC?

**Pro MVVM**:
- Qt nutzt Signals/Slots → passt zu MVVM
- ViewModels testbar ohne GUI
- Bessere Separation of Concerns

**Pro MVC**:
- Einfacher für kleine Apps

**Entscheidung**: MVVM für Skalierbarkeit

### 4. Warum Dataclasses?

**Pro**:
- Weniger Boilerplate
- Immutability (frozen=True möglich)
- Type Hints integriert

**Contra**:
- Weniger Kontrolle als custom Classes

**Entscheidung**: Clean Code > Kontrolle

## 🔧 Erweiterungspunkte

### Neue Datenquelle
1. Model in `models/` erstellen
2. Repository in `repositories/` erstellen (von `BaseRepository` erben)
3. Service-Methoden hinzufügen
4. UI in `views/` + `viewmodels/`

### Neue Analytics-Funktion
1. Methode in `AnalyticsService` hinzufügen
2. Unit Test schreiben
3. ViewModel erweitern
4. UI-Darstellung in `AnalyticsView`

### Neues Export-Format
1. `ExportService` in `services/` erstellen
2. Format-spezifische Methoden (CSV, PDF, Excel)
3. Menu-Eintrag in `MainWindow`
4. Dialog für Export-Optionen

## 📖 Dokumentation

- **Architektur**: `docs/architecture.md` (detailliert)
- **API**: `docs/api.md` (TODO)
- **User Guide**: `docs/user_guide.md` (TODO)

## 🎯 Entwicklungsprinzipien (aus copilot-instructions.md)

1. **Clean Code**: Sprechende Namen, klare Struktur
2. **TDD**: Tests zuerst
3. **Best Practices**: State-of-the-Art Standards
4. **Dokumentation**: Parallel zur Entwicklung
5. **Kleine Schritte**: Iterative Entwicklung

---

**Status**: ✅ Grundstruktur komplett  
**Nächster Schritt**: ViewModels implementieren oder Tests ausführen

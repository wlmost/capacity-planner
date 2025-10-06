# Architektur-Dokumentation

## Übersicht

Der Kapazitäts- & Auslastungsplaner ist eine PySide6-Desktopanwendung für Windows, die nach dem **Layered Architecture Pattern** mit **MVVM** für die UI-Schicht aufgebaut ist.

## Architektur-Diagramm

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ MainWindow   │  │TimeEntryView │  │AnalyticsView │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │           │
│  ┌──────▼─────────────────▼──────────────────▼───────┐  │
│  │            ViewModels (MVVM)                      │  │
│  └──────────────────────┬──────────────────────────┘   │
└─────────────────────────┼─────────────────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────┐
│                    Service Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │DatabaseSvc   │  │CryptoService │  │TimeParser   │ │
│  └──────┬───────┘  └──────────────┘  └─────────────┘ │
│         │                                              │
└─────────┼──────────────────────────────────────────────┘
          │
┌─────────▼──────────────────────────────────────────────┐
│                  Repository Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │TimeEntryRepo │  │CapacityRepo  │  │WorkerRepo   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘  │
└─────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼─────────┐
│                    Data Layer                            │
│               SQLite (via Qt SQL)                        │
└──────────────────────────────────────────────────────────┘
```

## Schichten-Beschreibung

### 1. Presentation Layer (Views + ViewModels)

**Verantwortlichkeit**: UI-Darstellung und Benutzerinteraktion

**Komponenten**:
- `views/`: PySide6-Widgets (reine Darstellung)
- `viewmodels/`: MVVM-Layer (UI-State, Validierung, Events)

**Kommunikation**: 
- Views binden an ViewModels via Signals/Slots
- ViewModels rufen Services auf

**Vorteile**:
- UI ohne Business Logic testbar
- ViewModels ohne Qt-Dependencies → Unit-Tests einfach

### 2. Service Layer

**Verantwortlichkeit**: Business Logic, Orchestrierung

**Komponenten**:
- `DatabaseService`: Connection Management, Migrations
- `CryptoService`: Verschlüsselung (RSA/AES)
- `TimeParserService`: Flexible Zeiteingabe-Parsing
- `AnalyticsService`: Auslastungsberechnungen

**Kommunikation**:
- Services nutzen Repositories für Datenzugriff
- Services sind zustandslos (außer DatabaseService)

**Vorteile**:
- Zentralisierte Business Logic
- Einfach austauschbar/mockbar
- Transaction-Management an einem Ort

### 3. Repository Layer

**Verantwortlichkeit**: Data Access, SQL-Queries

**Komponenten**:
- `BaseRepository`: Gemeinsame CRUD-Operationen
- `TimeEntryRepository`: Zeiterfassungs-Persistenz
- `CapacityRepository`: Kapazitätsplanungs-Persistenz

**Kommunikation**:
- Nutzt DatabaseService für Queries
- Returned Domain Models (keine DTOs nötig)

**Vorteile**:
- SQL-Logik isoliert
- Einfacher Wechsel zu anderem Storage
- Mocken in Tests trivial

### 4. Data Layer

**Technologie**: SQLite via Qt SQL

**Schema**: Siehe `resources/database/schema.sql`

**Vorteile von Qt SQL**:
- Native Integration mit Qt Event Loop
- Prepared Statements
- Transaction Support
- Cross-Platform

## Design Patterns

### Repository Pattern
- Abstrahiert Datenzugriff
- Domain Models unabhängig von Persistenz-Technologie

### MVVM (Model-View-ViewModel)
- View: PySide6 UI (deklarativ)
- ViewModel: UI-State + Presentation Logic
- Model: Domain Objects aus `models/`

### Service Layer Pattern
- Business Logic zentral
- Mehrere Repositories orchestrieren
- Transaction Boundaries

### Dependency Injection
- Services werden in ViewModels injiziert
- Repositories werden in Services injiziert
- Erleichtert Testing

## Sicherheitsarchitektur

### Verschlüsselung
- **Strategie**: Hybrid RSA/AES
- **RSA**: Key Exchange (2048-bit)
- **AES**: Daten-Verschlüsselung (256-bit, GCM Mode)

### Workflow
1. RSA-Keypair generieren/laden (einmalig)
2. Pro Verschlüsselung: neuer AES-Key
3. AES-Key mit RSA-Public-Key verschlüsseln
4. Daten mit AES verschlüsseln
5. Speichern: `encrypted_aes_key + nonce + tag + ciphertext`

### Key Management
- Keys in `~/.capacity_planner/keys/`
- Private Key niemals committen (.gitignore!)
- Rotation: `CryptoService.initialize_keys(force_new=True)`

## Erweiterbarkeit

### Neue Datenquelle hinzufügen
1. Neues Repository in `repositories/` erstellen
2. Von `BaseRepository` erben
3. Model in `models/` definieren
4. Service-Methoden hinzufügen

### Neues UI-Feature
1. Widget in `views/` erstellen
2. ViewModel in `viewmodels/` erstellen
3. Services injizieren
4. In MainWindow integrieren

### Neue Analytics-Funktion
1. Methode in `AnalyticsService` hinzufügen
2. Tests in `tests/unit/test_analytics.py`
3. UI-Darstellung in `AnalyticsView`

## Testing-Strategie

### Unit Tests
- **Umfang**: Services, Repositories, Models
- **Framework**: pytest
- **Mocking**: In-Memory SQLite, Fake Services

### Integration Tests
- **Umfang**: Database + Repository Layer
- **Setup**: Temporäre SQLite-DB pro Test

### UI Tests
- **Framework**: pytest-qt
- **Umfang**: Kritische User Flows

## Performance-Überlegungen

### Datenzugriff
- Indizes auf Foreign Keys
- Lazy Loading über Repositories
- Query-Optimierung in BaseRepository

### UI-Responsiveness
- Lange Operationen → QThread
- Analytics-Berechnungen asynchron
- Signals/Slots für UI-Updates

### Verschlüsselung
- AES für Bulk-Daten (schnell)
- RSA nur für Key Exchange
- Caching von entschlüsselten Daten (memory only)

## Deployment

### Packaging
- PyInstaller für Windows EXE
- Siehe `docs/deployment.md` (TODO)

### Daten-Migration
- Versionierung via `schema_version` Table
- Migrations-Scripts in `resources/database/migrations/`

## Weiterführende Dokumentation

- [API Reference](api.md)
- [User Guide](user_guide.md)
- [Development Setup](../README.md)

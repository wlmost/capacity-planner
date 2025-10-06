# Quick Start Guide

## Installation

1. **Repository klonen** (falls noch nicht geschehen)
   ```powershell
   cd C:\cygwin64\home\wleid\Entwicklung\01-Projekte\capacity-planner-sonnet
   ```

2. **Virtuelle Umgebung erstellen**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Dependencies installieren**
   ```powershell
   pip install -r requirements-dev.txt
   ```

## Tests ausführen

```powershell
# Alle Tests
pytest

# Mit Coverage Report
pytest --cov=src --cov-report=html

# Nur Unit Tests
pytest tests/unit/

# Spezifischer Test
pytest tests/unit/test_time_parser.py -v
```

## Anwendung starten

```powershell
python src/main.py
```

## Entwicklung

### Test-Driven Development Workflow

1. **Test schreiben**
   ```python
   # tests/unit/test_new_feature.py
   def test_new_feature():
       assert my_function() == expected_result
   ```

2. **Test ausführen (sollte fehlschlagen)**
   ```powershell
   pytest tests/unit/test_new_feature.py
   ```

3. **Implementation**
   ```python
   # src/services/my_service.py
   def my_function():
       return expected_result
   ```

4. **Test erneut ausführen (sollte erfolgreich sein)**
   ```powershell
   pytest tests/unit/test_new_feature.py
   ```

### Code Quality Checks

```powershell
# Code formatieren mit Black
black src/ tests/

# Linting mit Ruff
ruff check src/ tests/

# Type Checking mit mypy
mypy src/
```

## Nächste Entwicklungsschritte

### 1. ViewModels implementieren

**Datei**: `src/viewmodels/time_entry_viewmodel.py`

```python
from PySide6.QtCore import QObject, Signal
from services.time_parser_service import TimeParserService
from repositories.time_entry_repository import TimeEntryRepository

class TimeEntryViewModel(QObject):
    entry_created = Signal(int)  # emittiert neue Entry-ID
    error_occurred = Signal(str)  # emittiert Fehlermeldung
    
    def __init__(self, time_parser: TimeParserService, 
                 repository: TimeEntryRepository):
        super().__init__()
        self.time_parser = time_parser
        self.repository = repository
    
    def create_entry(self, worker_id: int, date_str: str, 
                     time_str: str, description: str):
        # Implementierung...
        pass
```

### 2. UI Widgets implementieren

**Datei**: `src/views/time_entry_widget.py`

```python
from PySide6.QtWidgets import QWidget, QFormLayout, QLineEdit, QPushButton
from viewmodels.time_entry_viewmodel import TimeEntryViewModel

class TimeEntryWidget(QWidget):
    def __init__(self, viewmodel: TimeEntryViewModel):
        super().__init__()
        self.viewmodel = viewmodel
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        # Formular erstellen...
        pass
```

### 3. Integration Tests

**Datei**: `tests/integration/test_database.py`

```python
def test_create_and_retrieve_time_entry():
    # Setup temporäre DB
    # TimeEntry erstellen
    # TimeEntry abrufen
    # Assertions
    pass
```

## Troubleshooting

### Problem: PySide6 ImportError

**Lösung**:
```powershell
pip install --upgrade PySide6
```

### Problem: SQLite Permissions Error

**Lösung**:
```powershell
# Verzeichnis erstellen
New-Item -ItemType Directory -Path "$env:USERPROFILE\.capacity_planner" -Force
```

### Problem: Crypto Keys nicht gefunden

**Lösung**: Keys werden automatisch beim ersten Start generiert. Wenn Fehler auftritt:
```python
from src.services.crypto_service import CryptoService
crypto = CryptoService()
crypto.initialize_keys(force_new=True)
```

## Ressourcen

- **Architektur**: `docs/architecture.md`
- **Struktur-Übersicht**: `STRUCTURE.md`
- **Copilot-Guide**: `.github/copilot-instructions.md`

## Git Workflow

```powershell
# Feature Branch erstellen
git checkout -b feature/time-entry-ui

# Änderungen committen (nach jedem Entwicklungsschritt)
git add .
git commit -m "feat: TimeEntryWidget hinzugefügt"

# Branch mergen
git checkout main
git merge feature/time-entry-ui
```

### Commit Message Conventions

- `feat:` Neue Features
- `fix:` Bugfixes
- `docs:` Dokumentation
- `test:` Tests hinzufügen/ändern
- `refactor:` Code-Refactoring
- `style:` Formatierung
- `chore:` Build/Config-Änderungen

## Support

Bei Fragen oder Problemen:
1. Architektur-Dokumentation konsultieren
2. Existierende Tests als Beispiele nutzen
3. GitHub Copilot fragen (gemäß `.github/copilot-instructions.md`)

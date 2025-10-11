# Kapazitäts- & Auslastungsplaner

Eine PySide6-Desktopanwendung für Windows zur Erfassung und Auswertung von Arbeitszeiten und Kapazitäten für Knowledge Worker.

## Features

- 📊 Flexible Zeiterfassung mit intelligentem Parser (z.B. "1:30", "90m", "1.5h")
- ⏱️ **Integrierter Timer** für Live-Zeiterfassung mit Start/Stop-Buttons
- ✏️ **Editierbare Zeiteinträge** direkt in der Tabelle (Doppelklick)
- 🔐 Verschlüsselte Datenspeicherung (RSA/AES)
- 📈 Auslastungsanalysen und Reports
- 💾 SQLite-Datenbank via Qt SQL
- 🎨 Native Windows-GUI mit PySide6

## Installation

```bash
pip install -r requirements.txt
```

## Entwicklung

```bash
pip install -r requirements-dev.txt
pytest
```

## Architektur

Siehe [docs/architecture.md](docs/architecture.md) für Details zur Projektstruktur.

## Lizenz

TBD

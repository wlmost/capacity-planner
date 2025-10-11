# Timer Feature - Visuelle Übersicht

## Zeiterfassungs-Tabelle mit Timer-Spalte

```
╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                    📋 Alle Zeitbuchungen                                                        ║
╠═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                                 ║
║  Von: [11.10.2025 ▼]    Bis: [11.10.2025 ▼]    [Filter anwenden]                                             ║
║                                                                                                                 ║
╠════════╤═══════╤═══════╤══════════════╤═══════════╤════════════════════╤═════════════════╤════════════════╤═════════╣
║ Datum  │Worker │ Typ   │   Projekt    │ Kategorie │    Beschreibung    │      Dauer      │     Timer      │ Aktion  ║
╠════════╪═══════╪═══════╪══════════════╪═══════════╪════════════════════╪═════════════════╪════════════════╪═════════╣
║        │       │       │              │           │                    │                 │                │         ║
║11.10.  │ Max   │Arbeit │ Project-X    │Development│ Feature-Impl...    │  45m (0.75h)   │ 00:45:23  ■   │🗑️ Lösch. ║
║2025    │ Muster│       │              │           │ [editierbar]       │  [editierbar]  │   [rot]        │         ║
║        │       │       │ [editierbar] │[editierbar]│                    │                │                │         ║
╟────────┼───────┼───────┼──────────────┼───────────┼────────────────────┼─────────────────┼────────────────┼─────────╢
║        │       │       │              │           │                    │                 │                │         ║
║11.10.  │ Anna  │Arbeit │ Project-Y    │ Meeting   │ Daily Standup      │ 15m (0.25h)    │ 00:00:00  ▶   │🗑️ Lösch. ║
║2025    │ Klein │       │              │           │                    │                 │  [grün]        │         ║
║        │       │       │              │           │                    │                 │                │         ║
╟────────┼───────┼───────┼──────────────┼───────────┼────────────────────┼─────────────────┼────────────────┼─────────╢
║        │       │       │              │           │                    │                 │                │         ║
║10.10.  │ Max   │Arbeit │ Project-X    │Testing    │ Unit Tests ge...   │ 120m (2.00h)   │ 02:05:45  ■   │🗑️ Lösch. ║
║2025    │ Muster│       │              │           │                    │                 │   [rot]        │         ║
║        │       │       │              │           │                    │                 │                │         ║
╟────────┼───────┼───────┼──────────────┼───────────┼────────────────────┼─────────────────┼────────────────┼─────────╢
║        │       │       │              │           │                    │                 │                │         ║
║10.10.  │ Anna  │Urlaub │              │           │ [Urlaub] Jahres... │ 480m (8.00h)   │ 08:00:00  ▶   │🗑️ Lösch. ║
║2025    │ Klein │       │              │           │                    │                 │  [grün]        │         ║
║        │       │       │              │           │                    │                 │                │         ║
╚════════╧═══════╧═══════╧══════════════╧═══════════╧════════════════════╧═════════════════╧════════════════╧═════════╝
```

## Timer-Widget Detail-Ansicht

### Timer gestoppt (bereit zum Starten)
```
┌──────────────────────────────┐
│  00:00:00  │  ▶             │
│            │  [Grün]         │
│            │  Tooltip:       │
│            │  "Timer starten"│
└──────────────────────────────┘
```

### Timer läuft
```
┌──────────────────────────────┐
│  00:15:47  │  ■             │
│  [live]    │  [Rot]          │
│            │  Tooltip:       │
│            │  "Timer stoppen"│
└──────────────────────────────┘
```

### Nach dem Stoppen
```
┌──────────────────────────────┐
│  00:15:47  │  ▶             │
│  [gespeich.]│ [Grün]         │
│            │  Tooltip:       │
│            │  "Timer starten"│
└──────────────────────────────┘
```

## Editier-Modus

### Vor dem Editieren (Normal)
```
┌────────────────┐
│  Project-X     │  ← Doppelklick zum Editieren
└────────────────┘
```

### Im Editier-Modus
```
┌────────────────┐
│  Project-Y▐    │  ← Text ist editierbar, Cursor blinkt
└────────────────┘
```

### Nach dem Speichern
```
┌────────────────┐
│  Project-Y     │  ← ✓ Änderung gespeichert (Status-Meldung)
└────────────────┘
```

## Dauer-Eingabe Beispiele

### Flexible Eingabe-Formate
```
Eingabe:    Ergebnis:           Anzeige in Tabelle:
────────    ─────────           ──────────────────
1:30    →   90 Minuten    →     90m (1.50h)
90m     →   90 Minuten    →     90m (1.50h)
1.5h    →   90 Minuten    →     90m (1.50h)
2       →   120 Minuten   →     120m (2.00h)
```

## User Flow: Timer verwenden

### 1. Timer starten
```
User                              System
  │                                 │
  │  Klick auf ▶ Button            │
  ├────────────────────────────────>│
  │                                 │
  │                                 │ Timer startet
  │                                 │ Button → ■ (rot)
  │                                 │ Start-Zeit gespeichert
  │                                 │
  │  Zeit läuft live (jede Sekunde) │
  │<────────────────────────────────│
  │  00:00:01, 00:00:02, ...       │
```

### 2. Timer stoppen
```
User                              System
  │                                 │
  │  Klick auf ■ Button            │
  ├────────────────────────────────>│
  │                                 │
  │                                 │ Verstrichene Zeit berechnen
  │                                 │ Entry.duration_minutes updaten
  │                                 │ Repository.update() aufrufen
  │                                 │ DB-Update durchführen
  │                                 │ Tabellen-Zelle aktualisieren
  │                                 │ Button → ▶ (grün)
  │                                 │
  │  ✓ Timer gestoppt: 15 Minuten  │
  │<────────────────────────────────│
  │  erfasst (Status-Meldung)      │
```

### 3. Zelle editieren
```
User                              System
  │                                 │
  │  Doppelklick auf "Projekt"     │
  ├────────────────────────────────>│
  │                                 │
  │                                 │ Editier-Modus aktivieren
  │  Editor angezeigt              │
  │<────────────────────────────────│
  │                                 │
  │  Text ändern: "Project-Y"      │
  │  Enter drücken                  │
  ├────────────────────────────────>│
  │                                 │
  │                                 │ Entry.project updaten
  │                                 │ Repository.update() aufrufen
  │                                 │ DB-Update durchführen
  │                                 │
  │  ✓ Änderung gespeichert        │
  │<────────────────────────────────│
  │  (Status-Meldung)              │
```

## Status-Meldungen

### Erfolg (grün)
```
╔═══════════════════════════════════════════════╗
║ ✓ Timer gestoppt: 45 Minuten erfasst         ║
╚═══════════════════════════════════════════════╝
```

### Fehler (rot)
```
╔═══════════════════════════════════════════════╗
║ ✗ Fehler beim Speichern der Dauer            ║
╚═══════════════════════════════════════════════╝
```

### Info (blau)
```
╔═══════════════════════════════════════════════╗
║ ℹ Ungültige Dauer-Eingabe                    ║
╚═══════════════════════════════════════════════╝
```

## Tastatur-Shortcuts

```
Aktion                  Shortcut
──────────────────────  ────────
Zelle editieren         F2 oder Doppelklick
Änderung speichern      Enter
Änderung verwerfen      ESC
Nächste Zelle           Tab
Vorherige Zelle         Shift+Tab
```

## Button-Styling

### Start-Button (Grün)
```css
QPushButton {
    background-color: #28a745;  /* Grün */
    color: white;
    border: none;
    padding: 5px;
    border-radius: 3px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #218838;  /* Dunkleres Grün */
}
```

### Stop-Button (Rot)
```css
QPushButton {
    background-color: #dc3545;  /* Rot */
    color: white;
    border: none;
    padding: 5px;
    border-radius: 3px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #c82333;  /* Dunkleres Rot */
}
```

## Technischer Überblick

```
┌─────────────────────────────────────────────────────────────┐
│                      TimeEntryWidget                         │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              Zeiterfassungs-Tabelle                 │    │
│  │                                                      │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │  Row 1: Entry #123                           │  │    │
│  │  │  ┌──────────────┐  ┌──────────────────────┐ │  │    │
│  │  │  │ TimerWidget  │  │  Löschen-Button     │ │  │    │
│  │  │  │  - entry_id  │  │                      │ │  │    │
│  │  │  │  - timer     │  └──────────────────────┘ │  │    │
│  │  │  │  - display   │                           │  │    │
│  │  │  └──────────────┘                           │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  │                                                      │    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │  Row 2: Entry #124                           │  │    │
│  │  │  ┌──────────────┐  ┌──────────────────────┐ │  │    │
│  │  │  │ TimerWidget  │  │  Löschen-Button     │ │  │    │
│  │  │  └──────────────┘  └──────────────────────┘ │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  │                                                      │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  Tracking:                                                  │
│  • _timer_widgets: {entry_id → TimerWidget}                │
│  • _entry_row_map: {entry_id → row_index}                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ timer_stopped signal
                            ↓
                    _on_timer_stopped()
                            │
                            ↓
                    TimeEntryRepository
                            │
                            ↓
                        Database
```

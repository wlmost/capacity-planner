# Pagination UI - Visual Guide

## UI Layout Übersicht

```
┌─────────────────────────────────────────────────────────────────────┐
│  Zeiterfassung                                                      │
├─────────────────────────────────────────────────────────────────────┤
│  ╔═══════════════════════════════════════════════════════════════╗ │
│  ║ FORMULAR BEREICH (40%)                                        ║ │
│  ║                                                               ║ │
│  ║ Worker: [Alice ▼]            Datum: [12.10.2025]            ║ │
│  ║ Typ: [Arbeit ▼]              End-Datum: [versteckt]         ║ │
│  ║ Projekt: [Projekt X ▼]       Kategorie: [Development]       ║ │
│  ║ Beschreibung: [Meeting...]                                   ║ │
│  ║ Dauer: [90m]                 ✓ 1:30 (1.50h)                 ║ │
│  ║                                                               ║ │
│  ║ [💾 Speichern]  [🔄 Zurücksetzen]                            ║ │
│  ╚═══════════════════════════════════════════════════════════════╝ │
├─────────────────────────────────────────────────────────────────────┤
│  ╔═══════════════════════════════════════════════════════════════╗ │
│  ║ 📋 Alle Zeitbuchungen                                        ║ │
│  ║                                                               ║ │
│  ║ [Von: 01.10.2025]  [Bis: 31.10.2025]                        ║ │
│  ║ [🔍 Datum, Worker, Projekt oder Beschreibung suchen...]     ║ │
│  ║                                                    5 Treffer  ║ │
│  ║ ┌───────────────────────────────────────────────────────────┐ ║ │
│  ║ │ Datum   │Worker │Typ    │Projekt │Kategorie│Dauer│Timer│ │ ║ │
│  ║ ├─────────┼───────┼───────┼────────┼─────────┼─────┼─────┤ │ ║ │
│  ║ │06.10.25 │Alice  │Arbeit │Proj X  │Dev      │90m  │▶    │ │ ║ │
│  ║ │05.10.25 │Bob    │Arbeit │Proj Y  │Meeting  │120m │▶    │ │ ║ │
│  ║ │04.10.25 │Alice  │Arbeit │Proj X  │Dev      │180m │▶    │ │ ║ │
│  ║ │03.10.25 │Charlie│Urlaub │-       │-        │480m │▶    │ │ ║ │
│  ║ │02.10.25 │Alice  │Arbeit │Proj Z  │Testing  │90m  │▶    │ │ ║ │
│  ║ │...      │...    │...    │...     │...      │...  │...  │ │ ║ │
│  ║ └───────────────────────────────────────────────────────────┘ ║ │
│  ║                                                               ║ │
│  ║ ┌─────────────────────────────────────────────────────────┐ ║ │
│  ║ │ PAGINATION CONTROLS                                     │ ║ │
│  ║ │                                                         │ ║ │
│  ║ │ Einträge pro Seite: [25 ▼]                            │ ║ │
│  ║ │                                                         │ ║ │
│  ║ │       Zeige 1-25 von 150 Einträgen                     │ ║ │
│  ║ │                                                         │ ║ │
│  ║ │  [◀ Zurück]  [Seite 1 von 6]  [Weiter ▶]             │ ║ │
│  ║ └─────────────────────────────────────────────────────────┘ ║ │
│  ╚═══════════════════════════════════════════════════════════════╝ │
└─────────────────────────────────────────────────────────────────────┘
```

## Pagination-Widget Details

### Layout-Komponenten

```
┌──────────────────────────────────────────────────────────────────┐
│  Einträge pro Seite: [10 ▼]    Zeige 26-50 von 150 Einträgen   │
│                                                                   │
│            [◀ Zurück]  [Seite 2 von 15]  [Weiter ▶]            │
└──────────────────────────────────────────────────────────────────┘
 └─────┬─────┘          └───────┬───────┘          └─────┬──────┘
       │                        │                         │
   Dropdown              Seiten-Info              Navigation
```

### Komponenten-Beschreibung

1. **Einträge pro Seite Dropdown**
   - Optionen: 10, 25, 50, 100
   - Standard: 25
   - Wird in QSettings gespeichert
   - Bei Änderung: Reset auf Seite 1

2. **Info-Label**
   - Format: "Zeige {start}-{end} von {total} Einträgen"
   - Beispiele:
     - "Zeige 1-25 von 150 Einträgen"
     - "Zeige 26-50 von 150 Einträgen"
     - "Zeige 141-150 von 150 Einträgen"
   - Bei 0 Einträgen: Leer

3. **Navigation Buttons**
   - **Zurück-Button**: "◀ Zurück"
     - Deaktiviert auf Seite 1
     - Hover-Effekt: Hellgrauer Hintergrund
   - **Seiten-Info**: "Seite X von Y"
     - Fett formatiert
     - Zentriert
     - Min-Width: 120px
   - **Weiter-Button**: "Weiter ▶"
     - Deaktiviert auf letzter Seite
     - Hover-Effekt: Hellgrauer Hintergrund

## States & Szenarien

### Szenario 1: Erste Seite (Standard)
```
Einträge pro Seite: [25 ▼]    Zeige 1-25 von 150 Einträgen
              
         [◀ Zurück]  [Seite 1 von 6]  [Weiter ▶]
         └─────┬────┘                  └────┬────┘
         Deaktiviert                   Aktiviert
```

### Szenario 2: Mittlere Seite
```
Einträge pro Seite: [25 ▼]    Zeige 51-75 von 150 Einträgen
              
         [◀ Zurück]  [Seite 3 von 6]  [Weiter ▶]
         └─────┬────┘                  └────┬────┘
          Aktiviert                    Aktiviert
```

### Szenario 3: Letzte Seite
```
Einträge pro Seite: [25 ▼]    Zeige 126-150 von 150 Einträgen
              
         [◀ Zurück]  [Seite 6 von 6]  [Weiter ▶]
         └─────┬────┘                  └────┬────┘
          Aktiviert                   Deaktiviert
```

### Szenario 4: Weniger Einträge als Seitengröße
```
Einträge pro Seite: [25 ▼]    Zeige 1-15 von 15 Einträgen
              
         [◀ Zurück]  [Seite 1 von 1]  [Weiter ▶]
         └─────┬────┘                  └────┬────┘
         Deaktiviert                  Deaktiviert
```

### Szenario 5: Keine Einträge
```
Einträge pro Seite: [25 ▼]    
              
         [◀ Zurück]  [Keine Einträge]  [Weiter ▶]
         └─────┬────┘                   └────┬────┘
         Deaktiviert                   Deaktiviert
```

### Szenario 6: Nach Suche (5 Treffer)
```
[🔍 "Meeting" suchen...]                        5 Treffer

┌─────────────────────────────────────────────────────────┐
│ Datum   │Worker │Typ    │Projekt │Beschreibung          │
├─────────┼───────┼───────┼────────┼─────────────────────┤
│06.10.25 │Alice  │Arbeit │Proj X  │Meeting mit Team     │
│05.10.25 │Bob    │Arbeit │Proj Y  │Meeting Kunde        │
│04.10.25 │Alice  │Arbeit │Proj X  │Standup Meeting      │
│02.10.25 │Charlie│Arbeit │Proj Z  │Review Meeting       │
│01.10.25 │Alice  │Arbeit │Proj X  │Planning Meeting     │
└─────────────────────────────────────────────────────────┘

Einträge pro Seite: [25 ▼]    Zeige 1-5 von 5 Einträgen
              
         [◀ Zurück]  [Seite 1 von 1]  [Weiter ▶]
         └─────┬────┘                  └────┬────┘
         Deaktiviert                  Deaktiviert
```

## Interaktions-Flows

### Flow 1: Seitengröße ändern
```
User wählt "50" im Dropdown
    ↓
_on_page_size_changed("50")
    ↓
page_size = 50
current_page = 1 (automatischer Reset)
    ↓
Signals emittiert:
  - page_size_changed(50)
  - page_changed(1)
    ↓
_on_page_size_changed(50) im Parent
    ↓
Speichere in QSettings
    ↓
_update_paginated_table()
    ↓
Tabelle zeigt Einträge 1-50
```

### Flow 2: Seite wechseln
```
User klickt "Weiter ▶"
    ↓
_on_next_clicked()
    ↓
current_page += 1
    ↓
Signal: page_changed(2)
    ↓
_on_page_changed(2) im Parent
    ↓
_update_paginated_table()
    ↓
Tabelle zeigt Einträge 26-50
```

### Flow 3: Suche + Pagination
```
User gibt "Meeting" ein
    ↓
_on_search("Meeting")
    ↓
_apply_search_filter()
  → _filtered_entries = [5 Einträge]
    ↓
pagination.reset_to_first_page()
    ↓
_update_paginated_table()
  → set_total_items(5)
  → Zeige Einträge 1-5
    ↓
Tabelle zeigt gefilterte Einträge
```

## Styling-Details

### Colors
- **Border**: #ccc (grau)
- **Background**: white
- **Hover Background**: #f0f0f0 (hellgrau)
- **Disabled Text**: #999 (dunkelgrau)
- **Disabled Background**: #f5f5f5 (sehr hellgrau)
- **Info Text**: #666 (mittelgrau)

### Spacing
- **Container Margins**: 0px 5px (oben/unten)
- **Element Spacing**: 10px
- **Button Padding**: 5px 15px
- **Dropdown Padding**: 5px

### Typography
- **Info Label**: 10pt, normal weight
- **Seiten-Info**: Standard, bold
- **Buttons**: Standard, normal weight

### Border-Radius
- Alle Elemente: 4px

## Accessibility

### Keyboard Navigation
- Tab-Order: Dropdown → Zurück-Button → Weiter-Button
- Enter/Space auf Buttons: Trigger Click
- Dropdown: Pfeiltasten für Navigation

### Screen Reader
- Buttons haben beschreibende Labels
- Dropdown hat Label "Einträge pro Seite"
- Info-Label ist lesbar

### Visual Feedback
- Hover-States auf allen interaktiven Elementen
- Disabled-State klar erkennbar
- Aktive Seite hervorgehoben

## Responsive Design

Das Widget passt sich an die Container-Breite an:
- Min-Width: ~500px (für alle Elemente nebeneinander)
- Bei kleinerer Breite: Elements wrappen automatisch

```
Desktop (>800px):
[Dropdown] [stretch] [Info] [stretch] [Buttons]

Tablet (500-800px):
[Dropdown] [Info] [Buttons]

Mobile (<500px):
[Dropdown]
[Info]
[Buttons]
```

## Testing Checklist

- [ ] Navigation funktioniert (Vor/Zurück)
- [ ] Buttons korrekt aktiviert/deaktiviert
- [ ] Seitengröße änderbar
- [ ] Info-Label korrekt
- [ ] Seiten-Anzeige korrekt
- [ ] Reset bei Suche funktioniert
- [ ] Settings werden gespeichert
- [ ] Edge-Cases behandelt (0 Einträge, 1 Seite, etc.)
- [ ] Hover-Effekte funktionieren
- [ ] Keyboard-Navigation möglich

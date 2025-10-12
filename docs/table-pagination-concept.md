# Tabellen-Pagination - Konzept & Implementierung

**Status:** ✅ **IMPLEMENTIERT**  
**Datum:** 12.10.2025  
**Feature:** Pagination für Zeiteinträge-Tabelle

---

## 📋 Übersicht

Die Pagination-Funktion ermöglicht es, große Mengen an Zeiteinträgen übersichtlich darzustellen, indem sie in Seiten aufgeteilt werden. Die Implementierung folgt dem Muster des `TableSearchWidget` und ist wiederverwendbar für andere Tabellen.

### Hauptfeatures
- ✅ Einstellbare Seitengröße (10, 25, 50, 100 Einträge)
- ✅ Navigation zwischen Seiten (Vor/Zurück)
- ✅ Anzeige der aktuellen Seite und Gesamtanzahl
- ✅ Anzeige des sichtbaren Bereichs (z.B. "Zeige 26-50 von 150 Einträgen")
- ✅ Integration mit Such- und Filterfunktion
- ✅ Persistierung der Seitengröße in QSettings

---

## 🎯 Implementierte Komponenten

### 1. TablePaginationWidget (Wiederverwendbar)

**Datei:** `src/views/table_pagination_widget.py`

#### **Features:**
- Pagination-Controls (Vorherige/Nächste Buttons)
- Dropdown für Einträge pro Seite
- Seitenanzeige (z.B. "Seite 2 von 10")
- Info-Label (z.B. "Zeige 1-25 von 150 Einträgen")
- Signal-Emission bei Änderungen

#### **Signals:**
```python
page_changed = Signal(int)       # Emittiert wenn Seite sich ändert
page_size_changed = Signal(int)  # Emittiert wenn Seitengröße sich ändert
```

#### **Wichtige Methoden:**
```python
set_total_items(total: int)      # Setzt Gesamtanzahl der Einträge
get_current_page() -> int        # Gibt aktuelle Seite zurück (1-basiert)
get_page_size() -> int           # Gibt Seitengröße zurück
get_offset() -> int              # Berechnet Offset für Datenbankabfragen
get_limit() -> int               # Gibt Limit zurück
reset_to_first_page()            # Setzt auf erste Seite zurück
```

#### **Code-Beispiel:**
```python
# Initialisierung
pagination = TablePaginationWidget(default_page_size=25)
pagination.page_changed.connect(self._on_page_changed)
pagination.page_size_changed.connect(self._on_page_size_changed)

# Nach Laden der Daten
pagination.set_total_items(150)

# Für Datenbankabfragen
offset = pagination.get_offset()  # z.B. 25 für Seite 2
limit = pagination.get_limit()    # z.B. 25
entries = repository.find_with_pagination(offset, limit)
```

---

### 2. TimeEntryWidget Integration

**Datei:** `src/views/time_entry_widget.py`

#### **Neue Instanzvariablen:**
```python
self._all_entries = []        # Alle geladenen Einträge (ungefiltert)
self._filtered_entries = []   # Nach Suche gefilterte Einträge
```

#### **Neue Methoden:**

##### `_apply_search_filter()`
Wendet Suchfilter auf alle Einträge an und aktualisiert `_filtered_entries`.

```python
def _apply_search_filter(self):
    """Wendet Suchfilter auf alle Einträge an"""
    search_text = self.search_widget.get_search_text().lower()
    
    if not search_text:
        self._filtered_entries = self._all_entries[:]
    else:
        # Filtere Einträge basierend auf Suchtext
        self._filtered_entries = []
        for entry in self._all_entries:
            if search_text in entry.description.lower():
                self._filtered_entries.append(entry)
```

##### `_update_paginated_table()`
Aktualisiert Tabelle mit aktueller Seite der gefilterten Einträge.

```python
def _update_paginated_table(self):
    """Aktualisiert Tabelle mit aktueller Seite"""
    # Update Pagination Widget
    self.pagination_widget.set_total_items(len(self._filtered_entries))
    
    # Berechne welche Einträge angezeigt werden
    offset = self.pagination_widget.get_offset()
    limit = self.pagination_widget.get_limit()
    paginated_entries = self._filtered_entries[offset:offset + limit]
    
    # Fülle Tabelle mit paginierten Einträgen
    # ... (siehe Code für Details)
```

#### **Modifizierte Methoden:**

##### `_refresh_entries_list()`
- Lädt alle Einträge aus DB (ohne Pagination auf DB-Ebene)
- Speichert in `_all_entries`
- Wendet Suchfilter an
- Ruft `_update_paginated_table()` auf

##### `_on_search(search_text: str)`
- Wendet Suchfilter an
- Setzt Pagination auf Seite 1 zurück
- Aktualisiert Tabelle

#### **Neue Event-Handler:**
```python
def _on_page_changed(self, page: int):
    """Handler für Seitenwechsel"""
    self._update_paginated_table()

def _on_page_size_changed(self, size: int):
    """Handler für Änderung der Seitengröße"""
    settings = QSettings()
    settings.setValue("time_entry_page_size", size)
    self._update_paginated_table()
```

---

## 🔄 Ablauf & Interaktion

### 1. Initiales Laden
```
User öffnet Zeiterfassung
  → _refresh_entries_list()
  → Lade alle Einträge aus DB
  → _all_entries = entries
  → _apply_search_filter() (leer → alle Einträge)
  → _filtered_entries = _all_entries
  → _update_paginated_table()
  → Zeige Seite 1 (Einträge 1-25)
```

### 2. Suche
```
User gibt Suchtext ein
  → _on_search(search_text)
  → _apply_search_filter()
  → Filtere _all_entries → _filtered_entries
  → pagination.reset_to_first_page()
  → _update_paginated_table()
  → Zeige gefilterte Einträge (Seite 1)
```

### 3. Seitenwechsel
```
User klickt "Weiter ▶"
  → pagination._on_next_clicked()
  → current_page = 2
  → page_changed.emit(2)
  → _on_page_changed(2)
  → _update_paginated_table()
  → Zeige Einträge 26-50
```

### 4. Seitengrößen-Änderung
```
User wählt "50" im Dropdown
  → pagination._on_page_size_changed("50")
  → page_size = 50
  → current_page = 1 (Reset)
  → page_size_changed.emit(50)
  → _on_page_size_changed(50)
  → Speichere in QSettings
  → _update_paginated_table()
  → Zeige Einträge 1-50
```

---

## 🎨 UI Layout

```
┌─────────────────────────────────────────────────────────┐
│  📋 Alle Zeitbuchungen                                  │
├─────────────────────────────────────────────────────────┤
│  [Datumsfilter: Von ... Bis ...]                        │
│  [🔍 Suche ...]                        [5 Treffer]      │
├─────────────────────────────────────────────────────────┤
│  ┌─────┬─────────┬──────┬──────────┬───────────────┐   │
│  │Datum│Worker   │Typ   │Projekt   │Beschreibung   │   │
│  ├─────┼─────────┼──────┼──────────┼───────────────┤   │
│  │06.10│Alice    │Arbeit│Projekt X │Meeting        │   │
│  │05.10│Bob      │Urlaub│-         │Urlaub         │   │
│  │...  │...      │...   │...       │...            │   │
│  └─────┴─────────┴──────┴──────────┴───────────────┘   │
├─────────────────────────────────────────────────────────┤
│  Einträge pro Seite: [25 ▼]                             │
│  Zeige 1-25 von 150 Einträgen                           │
│  [◀ Zurück]  [Seite 1 von 6]  [Weiter ▶]              │
└─────────────────────────────────────────────────────────┘
```

---

## 🧪 Tests

**Datei:** `tests/unit/views/test_table_pagination_widget.py`

### Test-Abdeckung:
1. ✅ `test_initialization_defaults` - Standardwerte korrekt
2. ✅ `test_initialization_custom_page_size` - Custom Seitengröße
3. ✅ `test_set_total_items` - Gesamtanzahl setzen
4. ✅ `test_page_navigation` - Navigation funktioniert
5. ✅ `test_page_size_change` - Seitengrößen-Änderung
6. ✅ `test_button_states` - Button-States korrekt
7. ✅ `test_reset_to_first_page` - Reset funktioniert
8. ✅ `test_offset_calculation` - Offset-Berechnung
9. ✅ `test_empty_list` - Leere Liste behandeln
10. ✅ `test_page_out_of_range_resets` - Out-of-range Reset

---

## 📊 Vorteile

### Performance
- **Weniger DOM-Elemente**: Nur 25-100 Zeilen statt 1000+
- **Schnelleres Rendering**: Tabelle lädt deutlich schneller
- **Bessere Responsiveness**: UI bleibt flüssig

### Usability
- **Übersichtlichkeit**: Nutzer sieht nicht mehr alle Einträge auf einmal
- **Flexibilität**: Seitengröße anpassbar
- **Konsistenz**: Gleiche UX wie bei anderen Business-Anwendungen

### Wartbarkeit
- **Wiederverwendbar**: `TablePaginationWidget` kann für andere Tabellen verwendet werden
- **Testbar**: Klare Trennung von Concerns
- **Erweiterbar**: Einfach weitere Optionen hinzuzufügen (z.B. "Springe zu Seite X")

---

## 🔮 Mögliche Erweiterungen

1. **"Springe zu Seite"**: Textfeld für direkte Seiteneingabe
2. **"Erste/Letzte Seite"**: Buttons für schnelle Navigation
3. **Keyboard Shortcuts**: Pfeiltasten für Navigation
4. **URL State**: Aktuelle Seite in URL speichern (falls Web-Version)
5. **Scroll to Top**: Automatisch nach oben scrollen bei Seitenwechsel
6. **Loading Indicator**: Ladeanimation während Datenabruf
7. **DB-Level Pagination**: Für sehr große Datenmengen (>10.000 Einträge)

---

## 📝 Verwendung in anderen Widgets

Das `TablePaginationWidget` kann einfach in anderen Tabellen-Widgets verwendet werden:

```python
from .table_pagination_widget import TablePaginationWidget

class MyTableWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # ... Tabelle erstellen ...
        
        # Pagination hinzufügen
        self.pagination = TablePaginationWidget(default_page_size=25)
        self.pagination.page_changed.connect(self._on_page_changed)
        layout.addWidget(self.pagination)
    
    def _load_data(self):
        # Lade alle Daten
        self._all_items = repository.find_all()
        
        # Update Pagination
        self.pagination.set_total_items(len(self._all_items))
        
        # Zeige aktuelle Seite
        self._show_current_page()
    
    def _show_current_page(self):
        offset = self.pagination.get_offset()
        limit = self.pagination.get_limit()
        
        current_items = self._all_items[offset:offset + limit]
        
        # Fülle Tabelle mit current_items
        # ...
    
    def _on_page_changed(self, page):
        self._show_current_page()
```

---

## 🎓 Lessons Learned

1. **In-Memory Pagination**: Für <10.000 Einträge ist In-Memory Pagination ausreichend
2. **State Management**: Wichtig, `_all_entries` und `_filtered_entries` getrennt zu halten
3. **Reset bei Änderungen**: Immer auf Seite 1 zurück bei Suche oder Filteränderung
4. **Settings Persistence**: Nutzer-Präferenzen (Seitengröße) speichern
5. **Wiederverwendbarkeit**: Generisches Widget ist wertvoller als spezifische Implementierung

---

## 🔗 Related Documentation

- `docs/table-search-concept.md` - Such-Funktionalität
- `docs/timeentry-widget-redesign.md` - TimeEntryWidget Design
- `docs/architecture.md` - Architektur-Übersicht

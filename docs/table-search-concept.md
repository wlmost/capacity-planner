# Tabellen-Suche - Konzept & Checkliste

## Datum: 2025-01-07

## 🎯 Ziel
Implementierung einer wiederverwendbaren Such-Komponente für alle Tabellen-Widgets mit Live-Suche, Multi-Spalten-Support und Treffer-Highlighting.

---

## 1. Concept-Checkliste

### Phase 1: TableSearchWidget Komponente (Wiederverwendbar)
- [ ] Neue Datei: `src/views/table_search_widget.py`
- [ ] QLineEdit mit Suchsymbol und Placeholder
- [ ] Clear-Button (X) zum Löschen
- [ ] Treffer-Anzeige (z.B. "5 Treffer")
- [ ] Signal `search_changed(str)` für Parent-Widget

### Phase 2: AnalyticsWidget Integration
- [ ] SearchWidget oberhalb der Tabelle einfügen
- [ ] Live-Filterung in _update_table()
- [ ] Multi-Spalten-Suche (Name, Email, Team)
- [ ] Case-insensitive Matching

### Phase 3: TimeEntryWidget Integration
- [ ] SearchWidget hinzufügen
- [ ] Suche in: Worker, Projekt, Beschreibung, Datum
- [ ] Filterung der Tabellen-Zeilen

### Phase 4: WorkerWidget Integration
- [ ] SearchWidget hinzufügen
- [ ] Suche in: Name, Email, Team
- [ ] Status-Filter kombinierbar mit Suche

### Phase 5: CapacityWidget Integration
- [ ] SearchWidget hinzufügen
- [ ] Suche in: Worker, Datum, Beschreibung
- [ ] Filterung kombinierbar mit Datumsfilter

### Phase 6: Testing
- [ ] Unit-Tests für TableSearchWidget
- [ ] Integration-Tests für alle Widgets
- [ ] Edge Cases (leere Tabelle, keine Treffer)

### Phase 7: Dokumentation
- [ ] README-Update
- [ ] Code-Dokumentation
- [ ] User Guide

---

## 2. Technische Spezifikation

### 2.1 TableSearchWidget Klasse

```python
class TableSearchWidget(QWidget):
    """
    Wiederverwendbare Such-Komponente für QTableWidget
    
    Features:
    - Live-Suche während Tippen
    - Clear-Button zum Zurücksetzen
    - Treffer-Anzeige
    - Signal-Emission bei Änderung
    """
    
    search_changed = Signal(str)
    
    def __init__(self, placeholder: str = "🔍 Suchen..."):
        super().__init__()
        self._placeholder = placeholder
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Such-Eingabefeld
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(self._placeholder)
        self._search_input.setClearButtonEnabled(True)  # Built-in Clear Button
        self._search_input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._search_input)
        
        # Treffer-Anzeige
        self._result_label = QLabel("")
        self._result_label.setStyleSheet("color: grey; font-size: 10pt;")
        layout.addWidget(self._result_label)
    
    def _on_text_changed(self, text: str):
        """Emittiert Signal wenn Text sich ändert"""
        self.search_changed.emit(text)
    
    def set_result_count(self, count: int, total: int):
        """Aktualisiert Treffer-Anzeige"""
        if not self._search_input.text():
            self._result_label.setText("")
        elif count == 0:
            self._result_label.setText("Keine Treffer")
        elif count == total:
            self._result_label.setText(f"{total} Einträge")
        else:
            self._result_label.setText(f"{count} von {total} Treffern")
    
    def clear(self):
        """Löscht Suchtext"""
        self._search_input.clear()
    
    def get_search_text(self) -> str:
        """Gibt aktuellen Suchtext zurück"""
        return self._search_input.text()
```

### 2.2 Integration-Pattern für Parent-Widgets

```python
class SomeTableWidget(QWidget):
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header...
        
        # Search Widget (NEU)
        self._search_widget = TableSearchWidget("🔍 Worker, Email oder Team suchen...")
        self._search_widget.search_changed.connect(self._on_search)
        layout.addWidget(self._search_widget)
        
        # Tabelle
        self._table = QTableWidget()
        layout.addWidget(self._table)
    
    def _on_search(self, search_text: str):
        """Handler für Suche"""
        self._filter_table(search_text)
    
    def _filter_table(self, search_text: str):
        """Filtert Tabellenzeilen basierend auf Suchtext"""
        if not search_text:
            # Alle Zeilen anzeigen
            for row in range(self._table.rowCount()):
                self._table.setRowHidden(row, False)
            self._search_widget.set_result_count(
                self._table.rowCount(), 
                self._table.rowCount()
            )
            return
        
        search_lower = search_text.lower()
        visible_count = 0
        
        for row in range(self._table.rowCount()):
            # Prüfe alle relevanten Spalten
            match = False
            for col in [0, 1, 2]:  # Name, Email, Team
                item = self._table.item(row, col)
                if item and search_lower in item.text().lower():
                    match = True
                    break
            
            self._table.setRowHidden(row, not match)
            if match:
                visible_count += 1
        
        self._search_widget.set_result_count(visible_count, self._table.rowCount())
```

---

## 3. UI/UX Design

### Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ Analytics Dashboard                              🔄 Aktualisieren   │
├─────────────────────────────────────────────────────────────────────┤
│ 🔍 Worker, Email oder Team suchen...  [×]      5 von 10 Treffern    │
├─────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┬──────────────┬─────────┬──────────┬─────────────┐  │
│ │ Worker      │ Email        │ Team    │ Geplant  │ Auslastung  │  │
│ ├─────────────┼──────────────┼─────────┼──────────┼─────────────┤  │
│ │ Max Muster  │ max@...      │ Dev     │ 160 h    │ 95%  ✓      │  │ <- Visible (match)
│ │ Anna Test   │ anna@...     │ QA      │ 120 h    │ 88%  ✓      │  │ <- Hidden (no match)
│ │ Tom Dev     │ tom@...      │ Dev     │ 140 h    │ 92%  ✓      │  │ <- Visible (match)
│ └─────────────┴──────────────┴─────────┴──────────┴─────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### States

**Empty Search**:
- Alle Zeilen sichtbar
- Result Label: leer oder "X Einträge"

**Active Search with Results**:
- Passende Zeilen sichtbar
- Nicht-passende Zeilen ausgeblendet (setRowHidden)
- Result Label: "5 von 10 Treffern"

**Active Search without Results**:
- Alle Zeilen ausgeblendet
- Result Label: "Keine Treffer" (rot)

**Styling**:
```css
QLineEdit {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 11pt;
}

QLineEdit:focus {
    border: 2px solid #4CAF50;
}

/* Result Label */
.no-results {
    color: #f44336;
    font-weight: bold;
}

.has-results {
    color: #4CAF50;
}

.all-results {
    color: grey;
}
```

---

## 4. Alternativen & Designentscheidungen

### Option A: setRowHidden() (GEWÄHLT)
✅ Einfach zu implementieren  
✅ Performance gut (keine Tabellen-Rebuilds)  
✅ Erhält Zeilen-Indizes  
⚠️ Scrollbar-Verhalten kann irritieren  

**Begründung**: Beste Balance aus Einfachheit und Performance.

### Option B: Table Rebuild (Filter Data)
✅ Saubere Darstellung  
❌ Performance-Problem bei großen Tabellen  
❌ Zeilen-Indizes ändern sich  

### Option C: Proxy Model (QSortFilterProxyModel)
✅ Qt-Standard Ansatz  
✅ Sehr mächtig  
❌ Komplexer (Model/View Architektur nötig)  
❌ Nicht für einfache QTableWidget geeignet  

**Entscheidung**: Option A für aktuelle Architektur optimal.

---

## 5. Implementierungs-Reihenfolge

### Schritt 1: TableSearchWidget (30 min)
```python
# Wiederverwendbare Komponente
# In: src/views/table_search_widget.py
```

### Schritt 2: AnalyticsWidget (30 min)
```python
# Integration in Analytics-Tabelle
# Spalten: Name, Email, Team
```

### Schritt 3: TimeEntryWidget (30 min)
```python
# Integration in Zeitbuchungs-Tabelle
# Spalten: Worker, Projekt, Beschreibung, Datum
```

### Schritt 4: WorkerWidget (30 min)
```python
# Integration in Worker-Tabelle
# Spalten: Name, Email, Team, Status
```

### Schritt 5: CapacityWidget (30 min)
```python
# Integration in Kapazitäts-Tabelle
# Spalten: Worker, Datum, Stunden, Beschreibung
```

### Schritt 6: Tests (45 min)
```python
# Unit-Tests für TableSearchWidget
# Integration-Tests für alle Widgets
```

### Schritt 7: Dokumentation (15 min)
```markdown
# README-Update
# User Guide
```

**TOTAL**: ~3.5 Stunden

---

## 6. Multi-Spalten Suche

### AnalyticsWidget (Team-Übersicht)
**Spalten**: 
- 0: Worker Name
- 1: Email
- 2: Team
- 3: Geplant (Stunden)
- 4: Gearbeitet (Stunden)
- 5: Differenz
- 6: Auslastung
- 7: Status

**Suchbare Spalten**: 0, 1, 2 (Name, Email, Team)

### TimeEntryWidget (Zeitbuchungen)
**Spalten**:
- 0: Datum
- 1: Worker
- 2: Dauer
- 3: Projekt
- 4: Beschreibung

**Suchbare Spalten**: 1, 3, 4 (Worker, Projekt, Beschreibung)

### WorkerWidget (Worker-Liste)
**Spalten**:
- 0: Name
- 1: Email
- 2: Team
- 3: Status
- 4: Erstellt

**Suchbare Spalten**: 0, 1, 2 (Name, Email, Team)

### CapacityWidget (Kapazitäten)
**Spalten**:
- 0: Datum
- 1: Worker
- 2: Stunden/Tag
- 3: Beschreibung

**Suchbare Spalten**: 1, 3 (Worker, Beschreibung)

---

## 7. Testing-Strategie

### Unit-Tests (test_table_search_widget.py)

```python
class TestTableSearchWidget:
    def test_widget_creation(self, qapp):
        """Widget kann erstellt werden"""
        widget = TableSearchWidget()
        assert widget is not None
    
    def test_placeholder_text(self, qapp):
        """Placeholder kann gesetzt werden"""
        widget = TableSearchWidget("Custom Placeholder")
        assert widget._search_input.placeholderText() == "Custom Placeholder"
    
    def test_search_signal_emission(self, qapp, qtbot):
        """Signal wird bei Texteingabe emittiert"""
        widget = TableSearchWidget()
        
        with qtbot.waitSignal(widget.search_changed) as blocker:
            widget._search_input.setText("test")
        
        assert blocker.args[0] == "test"
    
    def test_result_count_display(self, qapp):
        """Treffer-Anzeige wird korrekt aktualisiert"""
        widget = TableSearchWidget()
        
        # Keine Suche
        widget.set_result_count(10, 10)
        assert widget._result_label.text() == "10 Einträge"
        
        # Gefilterte Ergebnisse
        widget._search_input.setText("test")
        widget.set_result_count(5, 10)
        assert widget._result_label.text() == "5 von 10 Treffern"
        
        # Keine Treffer
        widget.set_result_count(0, 10)
        assert widget._result_label.text() == "Keine Treffer"
    
    def test_clear_button(self, qapp):
        """Clear-Button löscht Text"""
        widget = TableSearchWidget()
        widget._search_input.setText("test")
        
        widget.clear()
        assert widget.get_search_text() == ""
    
    def test_get_search_text(self, qapp):
        """get_search_text gibt aktuellen Text zurück"""
        widget = TableSearchWidget()
        widget._search_input.setText("hello")
        
        assert widget.get_search_text() == "hello"
```

### Integration-Tests

```python
class TestAnalyticsWidgetSearch:
    def test_search_filters_rows(self, qapp, sample_data):
        """Suche filtert Tabellenzeilen korrekt"""
        widget = AnalyticsWidget(...)
        
        # Initial: Alle Zeilen sichtbar
        assert widget._team_table.rowCount() == 10
        for row in range(10):
            assert not widget._team_table.isRowHidden(row)
        
        # Suche: "Dev"
        widget._search_widget._search_input.setText("Dev")
        
        # Nur Dev-Team Zeilen sichtbar
        visible = [row for row in range(10) 
                  if not widget._team_table.isRowHidden(row)]
        assert len(visible) == 3
    
    def test_search_case_insensitive(self, qapp, sample_data):
        """Suche ist case-insensitive"""
        widget = AnalyticsWidget(...)
        
        widget._search_widget._search_input.setText("MAX")
        visible = [row for row in range(10) 
                  if not widget._team_table.isRowHidden(row)]
        
        # Findet "Max Mustermann"
        assert len(visible) > 0
```

---

## 8. Performance-Optimierung

### Strategie

**Debouncing nicht nötig**: 
- setRowHidden() ist sehr schnell
- O(n) Komplexität bei Live-Suche akzeptabel
- Typische Tabellengröße: < 100 Zeilen

**Wenn Performance-Problem auftritt**:
```python
from PySide6.QtCore import QTimer

class TableSearchWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._emit_search)
        
    def _on_text_changed(self, text: str):
        # Debounce: Warte 300ms nach letzter Eingabe
        self._search_timer.stop()
        self._search_timer.start(300)
    
    def _emit_search(self):
        self.search_changed.emit(self._search_input.text())
```

---

## 9. Future Enhancements

### Phase 2 (v0.6.0)
- [ ] RegEx-Suche (Checkbox "Reguläre Ausdrücke")
- [ ] Spalten-spezifische Suche (Dropdown "Suche in...")
- [ ] Treffer-Highlighting mit Hintergrundfarbe
- [ ] Keyboard Navigation (Ctrl+F, Enter = Nächster Treffer)

### Phase 3 (v0.7.0)
- [ ] Suche speichern (Favoriten)
- [ ] Suche-History
- [ ] Export gefilterte Daten
- [ ] Erweiterte Filter kombinieren (Suche + Datum + Status)

---

## 10. Commit-Plan

**Commit 1**: TableSearchWidget Komponente
```
feat(search): Add reusable TableSearchWidget component

- Create TableSearchWidget with search input and result display
- Implement search_changed signal
- Add set_result_count() method
- Built-in clear button
- Unit tests for widget
```

**Commit 2**: AnalyticsWidget Integration
```
feat(search): Add table search to AnalyticsWidget

- Integrate TableSearchWidget above team table
- Multi-column search (Name, Email, Team)
- Live filtering with setRowHidden()
- Case-insensitive matching
- Integration tests
```

**Commit 3**: TimeEntryWidget Integration
```
feat(search): Add table search to TimeEntryWidget

- Search in Worker, Project, Description
- Row hiding based on match
- Result count display
```

**Commit 4**: WorkerWidget + CapacityWidget
```
feat(search): Add table search to Worker and Capacity widgets

- WorkerWidget: Search in Name, Email, Team
- CapacityWidget: Search in Worker, Description
- Complete all table widgets with search
```

---

## 11. Nächste Schritte

1. ✅ Konzept erstellen (DONE)
2. 🔄 TableSearchWidget implementieren (NEXT)
3. ⏳ AnalyticsWidget Integration
4. ⏳ TimeEntryWidget Integration
5. ⏳ WorkerWidget Integration
6. ⏳ CapacityWidget Integration
7. ⏳ Tests schreiben
8. ⏳ Dokumentation

**Status**: 📋 Konzept abgeschlossen, bereit für Implementierung

# Erweiterte Datumsfilter - Konzept & Checkliste

## Datum: 2025-01-07

## 🎯 Ziel
Implementierung eines erweiterten Datumsfilters mit Quick-Select Buttons für vordefinierte Zeiträume im Analytics-Widget.

---

## 1. Concept-Checkliste

### Phase 1: DateRangeWidget Komponente
- [ ] Neue Datei: `src/views/date_range_widget.py`
- [ ] Quick-Select Buttons für Presets erstellen
- [ ] Signal `date_range_changed(QDate, QDate)` definieren
- [ ] Layout mit Button-Gruppe + Custom Range

### Phase 2: Preset-Funktionen
- [ ] **Heute**: Start = Ende = heute
- [ ] **Diese Woche**: Montag bis heute (oder Sonntag)
- [ ] **Dieser Monat**: 1. bis letzter Tag des Monats
- [ ] **Dieses Quartal**: Q1-Q4 Start/Ende
- [ ] **Dieses Jahr**: 1. Januar bis 31. Dezember
- [ ] **Letzte 7 Tage**: heute - 7 Tage bis heute
- [ ] **Letzte 30 Tage**: heute - 30 Tage bis heute
- [ ] **Letzte 90 Tage**: heute - 90 Tage bis heute

### Phase 3: Integration in AnalyticsWidget
- [ ] Bestehende QDateEdit-Felder beibehalten
- [ ] DateRangeWidget oberhalb der Date-Edits einfügen
- [ ] Signal-Verbindung: Preset-Click → Update QDateEdit
- [ ] State Management: Aktiver Preset visuell hervorheben

### Phase 4: Testing
- [ ] Unit-Tests für DateRangeWidget
- [ ] Preset-Berechnungen testen
- [ ] Signal-Emission testen
- [ ] Integration-Test mit AnalyticsWidget

### Phase 5: Dokumentation
- [ ] README-Update mit Screenshots
- [ ] Code-Dokumentation
- [ ] User Guide Abschnitt

---

## 2. Technische Spezifikation

### 2.1 DateRangeWidget Klasse

```python
class DateRangeWidget(QWidget):
    """
    Widget für schnelle Datums-Bereichsauswahl
    
    Features:
    - 8 vordefinierte Zeiträume (Quick-Select Buttons)
    - Signal-Emission bei Auswahl
    - Visual Feedback für aktiven Preset
    """
    
    date_range_changed = Signal(QDate, QDate)
    
    def __init__(self):
        super().__init__()
        self._active_preset = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel("Schnellauswahl:")
        layout.addWidget(label)
        
        # Preset Buttons
        self._create_preset_button("Heute", self._select_today)
        self._create_preset_button("Diese Woche", self._select_this_week)
        # ... weitere Buttons
    
    def _create_preset_button(self, text, callback):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.clicked.connect(callback)
        return btn
    
    def _select_today(self):
        today = QDate.currentDate()
        self.date_range_changed.emit(today, today)
        self._set_active_preset("Heute")
```

### 2.2 Preset-Berechnungen

#### Heute
```python
def _select_today(self):
    today = QDate.currentDate()
    self.date_range_changed.emit(today, today)
```

#### Diese Woche (Montag bis Heute)
```python
def _select_this_week(self):
    today = QDate.currentDate()
    monday = today.addDays(-(today.dayOfWeek() - 1))
    self.date_range_changed.emit(monday, today)
```

#### Dieser Monat
```python
def _select_this_month(self):
    today = QDate.currentDate()
    first_day = QDate(today.year(), today.month(), 1)
    last_day = QDate(today.year(), today.month(), today.daysInMonth())
    self.date_range_changed.emit(first_day, last_day)
```

#### Dieses Quartal
```python
def _select_this_quarter(self):
    today = QDate.currentDate()
    month = today.month()
    
    # Q1: Jan-März, Q2: Apr-Jun, Q3: Jul-Sep, Q4: Okt-Dez
    quarter_start_month = ((month - 1) // 3) * 3 + 1
    quarter_end_month = quarter_start_month + 2
    
    start = QDate(today.year(), quarter_start_month, 1)
    end = QDate(today.year(), quarter_end_month, 
                QDate(today.year(), quarter_end_month, 1).daysInMonth())
    
    self.date_range_changed.emit(start, end)
```

#### Dieses Jahr
```python
def _select_this_year(self):
    today = QDate.currentDate()
    start = QDate(today.year(), 1, 1)
    end = QDate(today.year(), 12, 31)
    self.date_range_changed.emit(start, end)
```

#### Letzte X Tage
```python
def _select_last_7_days(self):
    today = QDate.currentDate()
    start = today.addDays(-7)
    self.date_range_changed.emit(start, today)

def _select_last_30_days(self):
    today = QDate.currentDate()
    start = today.addDays(-30)
    self.date_range_changed.emit(start, today)

def _select_last_90_days(self):
    today = QDate.currentDate()
    start = today.addDays(-90)
    self.date_range_changed.emit(start, today)
```

### 2.3 Integration in AnalyticsWidget

```python
# In _setup_ui() von AnalyticsWidget
filter_group = QGroupBox("Zeitraum")
filter_layout = QVBoxLayout(filter_group)

# Quick-Select Buttons (NEU)
self._date_range_widget = DateRangeWidget()
self._date_range_widget.date_range_changed.connect(self._on_preset_selected)
filter_layout.addWidget(self._date_range_widget)

# Bestehende Date-Edits (darunter)
date_edit_layout = QHBoxLayout()
# ... QDateEdit Felder wie bisher
filter_layout.addLayout(date_edit_layout)

# Handler
def _on_preset_selected(self, start_date: QDate, end_date: QDate):
    """Aktualisiert QDateEdit-Felder wenn Preset gewählt wird"""
    self._start_date_filter.setDate(start_date)
    self._end_date_filter.setDate(end_date)
    # _on_filter_changed() wird automatisch getriggert
```

---

## 3. UI/UX Design

### Button-Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ Schnellauswahl: [Heute] [Woche] [Monat] [Quartal] [Jahr]            │
│                 [Letzte 7T] [Letzte 30T] [Letzte 90T]                │
├─────────────────────────────────────────────────────────────────────┤
│ Von: [📅 01.01.2025]  Bis: [📅 07.01.2025]  Team: [Alle] Status: [✓] │
└─────────────────────────────────────────────────────────────────────┘
```

### Visual States

**Normal Button**:
```css
QPushButton {
    background-color: #e0e0e0;
    border: 1px solid #c0c0c0;
    border-radius: 4px;
    padding: 5px 10px;
}
```

**Active (Checked) Button**:
```css
QPushButton:checked {
    background-color: #4CAF50;
    color: white;
    border: 2px solid #45a049;
    font-weight: bold;
}
```

**Hover**:
```css
QPushButton:hover {
    background-color: #d0d0d0;
}
```

---

## 4. Alternativen

### Option A: Nur Buttons (GEWÄHLT)
✅ Einfach zu bedienen  
✅ Klar und übersichtlich  
✅ Mobile-friendly (große Targets)  
⚠️ Nimmt etwas Platz ein  

### Option B: Dropdown-Menü
✅ Platzsparend  
❌ Zusätzlicher Klick nötig  
❌ Weniger offensichtlich  

### Option C: Context-Menü (Rechtsklick)
✅ Platzsparend  
❌ Nicht intuitiv  
❌ Nicht entdeckbar  

**Entscheidung**: Option A - Buttons bieten beste UX

---

## 5. Testing-Strategie

### Unit-Tests (test_date_range_widget.py)

```python
class TestDateRangeWidget:
    def test_widget_creation(self, qapp):
        """Widget kann erstellt werden"""
        widget = DateRangeWidget()
        assert widget is not None
    
    def test_today_preset(self, qapp):
        """Heute-Button setzt korrektes Datum"""
        widget = DateRangeWidget()
        with qtbot.waitSignal(widget.date_range_changed) as blocker:
            widget._today_btn.click()
        
        start, end = blocker.args
        assert start == QDate.currentDate()
        assert end == QDate.currentDate()
    
    def test_this_week_preset(self, qapp):
        """Diese-Woche-Button berechnet Montag-Heute korrekt"""
        widget = DateRangeWidget()
        with qtbot.waitSignal(widget.date_range_changed) as blocker:
            widget._week_btn.click()
        
        start, end = blocker.args
        today = QDate.currentDate()
        expected_start = today.addDays(-(today.dayOfWeek() - 1))
        
        assert start == expected_start
        assert end == today
    
    def test_last_30_days_preset(self, qapp):
        """Letzte-30-Tage berechnet korrekt"""
        widget = DateRangeWidget()
        with qtbot.waitSignal(widget.date_range_changed) as blocker:
            widget._last_30_btn.click()
        
        start, end = blocker.args
        today = QDate.currentDate()
        
        assert end == today
        assert start == today.addDays(-30)
    
    def test_active_preset_visual_feedback(self, qapp):
        """Aktiver Preset wird visuell hervorgehoben"""
        widget = DateRangeWidget()
        widget._today_btn.click()
        
        assert widget._today_btn.isChecked()
        assert not widget._week_btn.isChecked()
```

---

## 6. Aufwand-Schätzung

| Phase | Aufgabe | Aufwand |
|-------|---------|---------|
| 1 | DateRangeWidget erstellen | 30 min |
| 2 | 8 Preset-Funktionen implementieren | 45 min |
| 3 | Integration in AnalyticsWidget | 30 min |
| 4 | Styling & Visual Feedback | 20 min |
| 5 | Unit-Tests schreiben | 40 min |
| 6 | Dokumentation | 15 min |
| **TOTAL** | | **3h** |

---

## 7. Dependencies

**Keine neuen Libraries erforderlich!**
- ✅ PySide6 (bereits installiert)
- ✅ QDate API (Teil von Qt)

---

## 8. Future Enhancements

### Phase 2 (v0.5.0)
- [ ] Kalender-Popup mit visueller Range-Selection
- [ ] Custom Presets speichern (z.B. "Geschäftsjahr 2024")
- [ ] Relative Presets ("Nächste 30 Tage", "Kommende Woche")

### Phase 3 (v0.6.0)
- [ ] Preset-Shortcuts (Tastatur: T=Heute, W=Woche, etc.)
- [ ] Preset-Favoriten pinnen
- [ ] Mehrsprachige Preset-Namen

---

## 9. Commit-Plan

**Commit 1**: DateRangeWidget Komponente
```
feat(filters): Add DateRangeWidget with preset buttons

- Create new DateRangeWidget class with 8 presets
- Implement date calculation methods
- Add date_range_changed signal
- Visual feedback for active preset
```

**Commit 2**: Integration & Testing
```
feat(analytics): Integrate DateRangeWidget into AnalyticsWidget

- Add DateRangeWidget above date edit fields
- Connect preset signals to date filters
- Add 8 unit tests for preset calculations
- Update documentation
```

---

## 10. Nächste Schritte

1. ✅ Konzept erstellen (DONE)
2. 🔄 DateRangeWidget implementieren (NEXT)
3. ⏳ In AnalyticsWidget integrieren
4. ⏳ Tests schreiben
5. ⏳ Dokumentation ergänzen
6. ⏳ Commit & Push

**Status**: 📋 Konzept abgeschlossen, bereit für Implementierung

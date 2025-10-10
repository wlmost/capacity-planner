# Feature: Datumsbereich-Auswahl bei Urlaub

**Status:** 🚧 In Entwicklung  
**Datum:** Januar 2025  
**Feature-Request:** Issue "Feature: Datumsbereich-Auswahl bei Typ Urlaub"

---

## 📋 Sinn & Zweck

### Problem
Aktuell muss der Benutzer beim Eintragen von Urlaub:
1. Jeden Urlaubstag einzeln eingeben
2. Die Dauer manuell pro Tag berechnen und eingeben
3. Dies für jeden Tag des Urlaubs wiederholen

**Beispiel:** 2 Wochen Urlaub (10 Arbeitstage) = 10 separate Einträge mit je 8h Dauer

### Lösung
Bei Auswahl des Typs "Urlaub":
1. Zusätzliches End-Datum-Feld wird sichtbar
2. Benutzer gibt Start- und End-Datum ein
3. System berechnet automatisch:
   - Anzahl der Werktage (Mo-Fr) im Zeitraum
   - Gesamtdauer = Werktage × Regelarbeitszeit
4. Dauer-Feld wird automatisch befüllt
5. **Optional:** Mehrere Einträge für jeden Urlaubstag erstellen

### Vorteile
✅ **Zeitersparnis**: Schnellere Urlaubseingabe (1 Eintrag statt 10)  
✅ **Weniger Fehler**: Automatische Berechnung verhindert Rechenfehler  
✅ **Bessere UX**: Intuitive Bereichsauswahl wie in Kalendern üblich  
✅ **Konsistenz**: Regelarbeitszeit wird aus Profil übernommen

---

## 🤔 Alternativen

### Alternative 1: Batch-Eingabe mit Wiederholung
**Ansatz:** Ein Dialog mit "Wiederholen für N Tage" Button
- **Pro:** Einfach zu implementieren
- **Contra:** Immer noch manuelles Rechnen nötig, nicht intuitiv

### Alternative 2: Kalender-Widget mit Multi-Select
**Ansatz:** Kalender-Ansicht wo mehrere Tage markiert werden können
- **Pro:** Sehr visuell, flexibel (auch nicht-zusammenhängende Tage)
- **Contra:** Aufwändig zu implementieren, braucht mehr Platz

### Alternative 3: Automatische Berechnung ohne End-Datum
**Ansatz:** Nur "Anzahl Tage" Eingabe + Start-Datum
- **Pro:** Sehr einfach
- **Contra:** Weniger flexibel, kein konkretes End-Datum sichtbar

### ✅ Gewählte Lösung: Datumsbereich (Von-Bis)
**Warum:**
- Nutzt bestehende `QDateEdit` Komponenten
- Konkretes End-Datum ist für Planung wichtig
- Standard-Pattern bei Urlaubsverwaltung
- Erweiterbar für spätere Features (z.B. halbe Tage)

---

## ⚙️ Funktionsweise

### UI-Änderungen

#### Vorher:
```
Worker:     [Dropdown]
Datum:      [06.01.2025 📅]
Typ:        [Urlaub ▼]
Projekt:    [Optional...]
Kategorie:  [Optional...]
Beschreibung: [Textfeld]
Dauer:      [8h________] ✓ 08:00 (8.00h)
```

#### Nachher (bei Typ "Urlaub"):
```
Worker:     [Dropdown]
Datum (Von):    [06.01.2025 📅]
Datum (Bis):    [17.01.2025 📅]  ← NEU, nur sichtbar bei "Urlaub"
Typ:            [Urlaub ▼]
Projekt:        [Optional...]
Kategorie:      [Optional...]
Beschreibung:   [Textfeld]
Dauer:          [80h________] ✓ 80:00 (80.00h)  ← Automatisch berechnet
                ℹ️ 10 Werktage × 8.0h/Tag
```

### Berechnungslogik

```python
def calculate_vacation_duration(start_date: QDate, end_date: QDate, daily_hours: float) -> int:
    """
    Berechnet Urlaubsdauer in Minuten
    
    Args:
        start_date: Start-Datum
        end_date: End-Datum (inklusiv)
        daily_hours: Regelarbeitszeit pro Tag (z.B. 8.0)
        
    Returns:
        Dauer in Minuten
    """
    # Anzahl Werktage berechnen (Mo-Fr)
    workdays = 0
    current = start_date
    
    while current <= end_date:
        # Qt dayOfWeek: 1=Montag, 7=Sonntag
        if current.dayOfWeek() <= 5:  # Mo-Fr
            workdays += 1
        current = current.addDays(1)
    
    # Minuten berechnen
    total_hours = workdays * daily_hours
    return int(total_hours * 60)
```

### Regelarbeitszeit laden

```python
def get_daily_hours_for_worker(worker_id: int) -> float:
    """Lädt Regelarbeitszeit aus QSettings"""
    settings = QSettings("CapacityPlanner", "Settings")
    return settings.value(f"worker_{worker_id}_daily_hours", 8.0, type=float)
```

### UI-Verhalten bei Typ-Änderung

```python
def _on_type_changed(self, index: int):
    """Wird aufgerufen wenn Typ geändert wird"""
    entry_type = self.type_combo.currentText()
    
    if entry_type == "Urlaub":
        # End-Datum-Feld anzeigen
        self.end_date_edit.setVisible(True)
        self.end_date_label.setVisible(True)
        
        # Datum-Label ändern
        self.date_label.setText("Datum (Von):")
        
        # Dauer automatisch berechnen
        self._calculate_vacation_duration()
        
        # Dauer-Feld readonly machen (wird automatisch berechnet)
        self.time_input.setReadOnly(True)
        self.time_input.setStyleSheet("background-color: #f0f0f0;")
        
    else:
        # End-Datum-Feld verstecken
        self.end_date_edit.setVisible(False)
        self.end_date_label.setVisible(False)
        
        # Datum-Label zurücksetzen
        self.date_label.setText("Datum:")
        
        # Dauer-Feld wieder editierbar
        self.time_input.setReadOnly(False)
        self.time_input.setStyleSheet("")
        self.time_input.clear()
```

### Auto-Berechnung bei Datumsänderung

```python
def _calculate_vacation_duration(self):
    """Berechnet und setzt Urlaubsdauer automatisch"""
    if self.type_combo.currentText() != "Urlaub":
        return
    
    # Worker-ID holen
    worker_id = self.worker_combo.currentData()
    if not worker_id:
        return
    
    # Datumsbereich
    start_date = self.date_edit.date()
    end_date = self.end_date_edit.date()
    
    # Validierung
    if end_date < start_date:
        self.time_preview.setText("⚠️ End-Datum muss >= Start-Datum sein")
        self.time_preview.setStyleSheet("color: red; font-style: italic;")
        self.time_input.clear()
        return
    
    # Regelarbeitszeit laden
    daily_hours = get_daily_hours_for_worker(worker_id)
    
    # Dauer berechnen
    duration_minutes = calculate_vacation_duration(start_date, end_date, daily_hours)
    
    # Werktage für Anzeige
    workdays = duration_minutes / (daily_hours * 60)
    
    # Dauer-Feld setzen
    hours = duration_minutes / 60.0
    self.time_input.setText(f"{hours}h")
    
    # Preview aktualisieren
    self.time_preview.setText(f"ℹ️ {int(workdays)} Werktage × {daily_hours}h/Tag")
    self.time_preview.setStyleSheet("color: #666; font-style: italic;")
```

---

## 🎯 Implementierungs-Schritte

### 1. UI-Komponenten hinzufügen
- [x] End-Datum `QDateEdit` in `_create_form_widget()` hinzufügen
- [x] Initial versteckt setzen
- [x] Label "Datum (Bis):" hinzufügen

### 2. Signal-Verbindungen
- [x] `type_combo.currentIndexChanged` → `_on_type_changed`
- [x] `date_edit.dateChanged` → `_calculate_vacation_duration`
- [x] `end_date_edit.dateChanged` → `_calculate_vacation_duration`
- [x] `worker_combo.currentIndexChanged` → `_calculate_vacation_duration`

### 3. Berechnungs-Logik
- [x] Methode `_calculate_vacation_duration()` implementieren
- [x] Hilfsmethode `_count_workdays()` für Werktage-Berechnung
- [x] Regelarbeitszeit aus QSettings laden

### 4. Validierung
- [x] End-Datum >= Start-Datum prüfen
- [x] Warnung wenn Zeitraum nur Wochenenden enthält
- [x] Worker muss ausgewählt sein

### 5. Formular-Reset
- [x] `_clear_form()` erweitern: End-Datum verstecken
- [x] Typ auf "Arbeit" zurücksetzen

---

## 🧪 Test-Strategie

### Unit-Tests

```python
# tests/unit/views/test_time_entry_widget_vacation.py

def test_end_date_visible_when_vacation_selected():
    """End-Datum wird bei Urlaub angezeigt"""
    widget = TimeEntryWidget(...)
    
    widget.type_combo.setCurrentText("Urlaub")
    assert widget.end_date_edit.isVisible()
    assert widget.end_date_label.isVisible()

def test_end_date_hidden_when_work_selected():
    """End-Datum wird bei Arbeit versteckt"""
    widget = TimeEntryWidget(...)
    
    widget.type_combo.setCurrentText("Arbeit")
    assert not widget.end_date_edit.isVisible()

def test_vacation_duration_calculation():
    """Urlaubsdauer wird korrekt berechnet"""
    # 5 Werktage (Mo-Fr), 8h/Tag = 40h = 2400min
    start = QDate(2025, 1, 6)  # Montag
    end = QDate(2025, 1, 10)   # Freitag
    
    minutes = calculate_vacation_duration(start, end, 8.0)
    assert minutes == 2400  # 40 Stunden

def test_vacation_duration_with_weekend():
    """Wochenende wird nicht mitgezählt"""
    # Mo-So (7 Tage) = 5 Werktage
    start = QDate(2025, 1, 6)   # Montag
    end = QDate(2025, 1, 12)    # Sonntag
    
    minutes = calculate_vacation_duration(start, end, 8.0)
    assert minutes == 2400  # 5 Werktage × 8h

def test_vacation_duration_single_day():
    """Einzelner Tag wird korrekt berechnet"""
    start = QDate(2025, 1, 6)  # Montag
    end = QDate(2025, 1, 6)    # Montag
    
    minutes = calculate_vacation_duration(start, end, 8.0)
    assert minutes == 480  # 8 Stunden

def test_validation_end_before_start():
    """Validierung: End-Datum < Start-Datum"""
    widget = TimeEntryWidget(...)
    
    widget.type_combo.setCurrentText("Urlaub")
    widget.date_edit.setDate(QDate(2025, 1, 10))
    widget.end_date_edit.setDate(QDate(2025, 1, 6))
    
    # Sollte Fehler anzeigen
    assert "End-Datum" in widget.time_preview.text()
```

---

## 📊 Erwartete Änderungen

### Dateien
- `src/views/time_entry_widget.py` (~80 Zeilen hinzufügen)
- `tests/unit/views/test_time_entry_widget_vacation.py` (neu, ~150 Zeilen)
- `docs/vacation-date-range-feature.md` (dieses Dokument)

### Breaking Changes
❌ **Keine** - Die Änderung ist vollständig abwärtskompatibel:
- Bestehende Formulare funktionieren weiterhin (Standard: "Arbeit")
- End-Datum ist optional und nur bei "Urlaub" sichtbar
- Einzelne Urlaubstage können weiterhin manuell eingegeben werden

---

## 🔮 Zukünftige Erweiterungen

### Phase 2: Batch-Erstellung
Statt einem Eintrag mit 80h, mehrere Einträge erstellen:
- 10 separate TimeEntry-Objekte (je 8h)
- Bessere Übersicht in Zeiterfassungs-Liste
- Einzelne Tage können bei Bedarf bearbeitet/gelöscht werden

### Phase 3: Halbe Urlaubstage
Checkbox "Nur halber Tag" für flexiblere Eingabe:
- Morgens oder Nachmittags frei
- Automatische Berechnung: 0.5 × Regelarbeitszeit

### Phase 4: Feiertags-Erkennung
Integration von Feiertags-API:
- Automatisches Überspringen von Feiertagen
- Warnung bei Urlaubseingabe über Feiertage
- Länderspezifische Feiertags-Kalender

---

## ✅ Akzeptanzkriterien

- [x] End-Datum-Feld wird nur bei Typ "Urlaub" angezeigt
- [x] Dauer wird automatisch berechnet (Werktage × Regelarbeitszeit)
- [x] Wochenenden werden nicht mitgezählt
- [x] Regelarbeitszeit wird aus Worker-Profil geladen
- [x] Validierung: End-Datum >= Start-Datum
- [x] Formular-Reset versteckt End-Datum wieder
- [x] Dauer-Feld ist readonly bei Urlaub (automatische Berechnung)
- [x] Live-Preview zeigt Werktage-Berechnung an
- [x] Bestehende Funktionalität bleibt unverändert

---

## 📚 Referenzen

- Siehe `src/views/profile_dialog.py` für QSettings-Zugriff
- Siehe `src/views/date_range_widget.py` für QDate-Berechnungen
- Siehe `src/models/capacity.py` für Tage-Berechnung (`.days_count()`)

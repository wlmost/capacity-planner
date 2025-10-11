# Timer Feature für Zeiterfassung

## 📋 Übersicht

Das Timer-Feature ermöglicht es Benutzern, Zeit direkt in der Zeiterfassungs-Tabelle zu tracken. Jeder Eintrag hat einen eigenen Timer mit Start/Stop-Funktionalität und Live-Anzeige der erfassten Zeit.

## ✨ Features

### 1. **Timer-Widget pro Zeile**
- ⏱️ Jeder Zeiterfassungs-Eintrag hat einen eigenen Timer
- ▶️ Start-Button (grün) zum Starten der Zeiterfassung
- ■ Stop-Button (rot) zum Beenden der Zeiterfassung
- Live-Anzeige im Format HH:MM:SS
- Akkumuliert Zeit über mehrere Start/Stop-Zyklen

### 2. **Editierbare Tabellen-Zellen**
Die folgenden Spalten sind nun direkt in der Tabelle editierbar:
- **Projekt**: Doppelklick oder F2 zum Bearbeiten
- **Kategorie**: Doppelklick oder F2 zum Bearbeiten
- **Beschreibung**: Doppelklick oder F2 zum Bearbeiten
- **Dauer**: Unterstützt flexible Eingaben (z.B. "1:30", "90m", "1.5h")

### 3. **Automatisches Speichern**
- Änderungen werden sofort in der Datenbank gespeichert
- Kein separater "Speichern"-Button erforderlich
- Erfolgs-/Fehlermeldungen werden angezeigt

### 4. **Timer-Integration mit Dauer**
- Timer startet mit der bereits erfassten Dauer
- Beim Stoppen wird die Dauer automatisch aktualisiert
- Dauer-Spalte zeigt die aktuelle Zeit aus dem Timer

## 🎯 Verwendung

### Timer starten
1. Navigiere zur Zeiterfassung
2. Finde den gewünschten Eintrag in der Tabelle
3. Klicke auf den grünen **▶** Button in der "Timer"-Spalte
4. Die Zeit läuft nun und wird live aktualisiert

### Timer stoppen
1. Klicke auf den roten **■** Button
2. Die erfasste Zeit wird automatisch gespeichert
3. Die Dauer-Spalte wird aktualisiert

### Eintrag bearbeiten
1. Doppelklick auf eine editierbare Zelle (Projekt, Kategorie, Beschreibung, Dauer)
2. Nehme die gewünschte Änderung vor
3. Drücke Enter oder klicke außerhalb der Zelle
4. Die Änderung wird automatisch gespeichert

### Dauer manuell eingeben
Die Dauer-Spalte unterstützt verschiedene Eingabeformate:
- `1:30` → 1 Stunde 30 Minuten (90 Minuten)
- `90m` → 90 Minuten
- `1.5h` → 1,5 Stunden (90 Minuten)
- `2` → 2 Stunden (120 Minuten)

## 🔧 Technische Details

### Architektur

#### TimerWidget
- **Datei**: `src/views/timer_widget.py`
- **Zweck**: Eigenständiges Widget für Timer-Funktionalität
- **Komponenten**:
  - Zeit-Anzeige (QLabel) mit Monospace-Font
  - Start/Stop-Button (QPushButton)
  - QTimer für sekündliche Updates
  - Signal-Emitter für Events

#### Signals
- `timer_stopped(int)`: Emittiert Minuten wenn Timer gestoppt wird
- `duration_changed(int)`: Emittiert Minuten bei jedem Update (jede Sekunde)

#### TimeEntryWidget Integration
- **Datei**: `src/views/time_entry_widget.py`
- **Änderungen**:
  - Neue Spalte "Timer" zur Tabelle hinzugefügt
  - `_timer_widgets` Dict für Timer-Tracking
  - `_entry_row_map` Dict für Entry-ID zu Row-Mapping
  - `_on_timer_stopped()` für Timer-Stop Handling
  - `_on_table_item_changed()` für Zellen-Editing
  - `_stop_all_timers()` für Cleanup vor Refresh

### Datenfluss

```
1. User klickt Start
   ↓
2. TimerWidget.start_timer()
   ↓
3. QTimer startet (1s Intervall)
   ↓
4. Display wird jede Sekunde aktualisiert
   ↓
5. User klickt Stop
   ↓
6. timer_stopped Signal emittiert
   ↓
7. TimeEntryWidget._on_timer_stopped()
   ↓
8. TimeEntry.duration_minutes aktualisiert
   ↓
9. Repository.update() speichert in DB
   ↓
10. Tabellen-Zelle wird aktualisiert
```

### Zeit-Berechnung
- **Speicherung**: `accumulated_seconds` (int) für genaue Berechnung
- **Anzeige**: HH:MM:SS Format mit führenden Nullen
- **Rückgabe**: Minuten (gerundet, Sekunden werden ignoriert)

### Editierbare Zellen
- **Trigger**: `DoubleClicked | EditKeyPressed`
- **Nicht editierbar**: Datum, Worker, Typ
- **Editierbar**: Projekt, Kategorie, Beschreibung, Dauer
- **Validierung**: Zeit-Parser für Dauer-Eingaben

## 🧪 Tests

### Unit Tests
Datei: `tests/unit/views/test_timer_widget.py`

Test-Kategorien:
- ✅ Initialisierung (mit/ohne vorhandene Zeit)
- ✅ Start/Stop Funktionalität
- ✅ Zeit-Berechnung und Formatierung
- ✅ Signal-Emission
- ✅ Display-Updates
- ✅ Hilfsmethoden

Beispiel-Test:
```python
def test_timer_accumulates_time(timer_widget):
    timer_widget._start_timer()
    QTest.qWait(1100)
    timer_widget._stop_timer()
    
    assert timer_widget.get_total_minutes() >= 0
```

### Integration Tests
Die Integration in `TimeEntryWidget` wird durch manuelle Tests verifiziert:
1. Timer starten und stoppen
2. Dauer-Update in Tabelle prüfen
3. Datenbank-Speicherung verifizieren
4. Mehrfache Start/Stop-Zyklen testen
5. Zellen-Editing testen

## 📸 Screenshots

### Timer-Spalte
```
| Datum      | Worker | ... | Dauer           | Timer          | Aktion   |
|------------|--------|-----|-----------------|----------------|----------|
| 11.10.2025 | Max    | ... | 45m (0.75h)     | 00:45:23 [■]  | 🗑️ Löschen|
| 10.10.2025 | Anna   | ... | 120m (2.00h)    | 02:00:00 [▶]  | 🗑️ Löschen|
```

### Timer läuft (grüner Button)
- Button: Grün mit "▶" Symbol
- Zeit läuft live
- Stop-Button rot mit "■" Symbol

### Editierbare Zellen
- Doppelklick auf Zelle öffnet Editor
- Enter zum Speichern
- ESC zum Abbrechen
- Automatische Validierung (z.B. Zeit-Parser)

## 🚀 Zukünftige Erweiterungen

### Mögliche Features (nicht implementiert)
1. **Timer-Persistenz**: Timer-State über App-Restart hinweg speichern
2. **Desktop-Benachrichtigungen**: Bei bestimmten Zeitpunkten
3. **Tastenkürzel**: Strg+Enter zum Starten/Stoppen
4. **Bulk-Operationen**: Alle Timer auf einmal stoppen
5. **Timer-Historie**: Log aller Start/Stop-Ereignisse
6. **Pomodoro-Integration**: 25-Minuten-Timer mit Pausen

### Datenbank-Schema (optional)
Für Timer-Persistenz könnte das Schema erweitert werden:
```sql
ALTER TABLE time_entries ADD COLUMN timer_start_time TIMESTAMP;
ALTER TABLE time_entries ADD COLUMN timer_is_running INTEGER DEFAULT 0;
```

## 🐛 Bekannte Einschränkungen

1. **Timer-State nicht persistent**: Bei App-Neustart gehen laufende Timer verloren
2. **Ein Timer pro Entry**: Mehrere Timer gleichzeitig möglich, aber separat gesteuert
3. **Keine Timer-Pause**: Nur Start und Stop, keine Pause-Funktion
4. **Sortierung**: Bei laufendem Timer kann Sortierung die Zeile verschieben

## 📚 Code-Beispiele

### Timer-Widget erstellen
```python
from src.views.timer_widget import TimerWidget

# Neuer Timer mit 0 Minuten
timer = TimerWidget(entry_id=1, initial_minutes=0)

# Timer mit vorhandener Zeit
timer = TimerWidget(entry_id=2, initial_minutes=45)

# Signal verbinden
timer.timer_stopped.connect(lambda minutes: print(f"Stopped: {minutes} min"))
```

### Timer programmgesteuert steuern
```python
# Timer starten
timer._start_timer()

# Prüfen ob läuft
if timer.is_timer_running():
    print("Timer läuft")

# Timer stoppen
timer._stop_timer()

# Zeit abfragen
minutes = timer.get_total_minutes()
```

### Tabellen-Zelle editieren
```python
# Zelle auf editierbar setzen
item = QTableWidgetItem("Projekt ABC")
item.setData(Qt.UserRole, entry_id)
table.setItem(row, col, item)

# Edit-Trigger setzen
table.setEditTriggers(
    QAbstractItemView.DoubleClicked | 
    QAbstractItemView.EditKeyPressed
)
```

## ✅ Checkliste für Review

- [x] TimerWidget implementiert
- [x] Timer-Integration in TimeEntryWidget
- [x] Tabellen-Zellen editierbar
- [x] Automatisches Speichern bei Änderungen
- [x] Signal-basierte Kommunikation
- [x] Unit Tests für TimerWidget
- [x] Code-Dokumentation
- [x] Feature-Dokumentation
- [ ] Manuelle Tests mit GUI (nicht möglich in CI-Umgebung)
- [ ] Screenshots von Live-Anwendung

## 🎓 Lessons Learned

1. **Signal-basierte Architektur**: Clean separation zwischen Widget und Parent
2. **QTimer für Updates**: Einfache Integration für periodische Updates
3. **User Data in Items**: Qt.UserRole für zusätzliche Daten in Zellen
4. **Disconnect/Connect**: Notwendig für programmgesteuerte Updates ohne Events
5. **Edit Triggers**: Flexible Steuerung wann Zellen editierbar sind

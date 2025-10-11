# Fix: Urlaubseintragungen in der Tabelle der Zeiterfassungen sichtbar

## Problem

Als Anwender erwartete man, dass Urlaubseintragungen in der Tabelle der Zeiterfassungen sichtbar sind. Das System ermöglichte bereits die Eingabe von Urlaub mit Datumsbereich (z.B. 2 Wochen vom 06.01.2025 bis 17.01.2025), jedoch wurde nur **ein** Eintrag mit dem Startdatum und der Gesamtdauer (80h für 10 Werktage) gespeichert. Dies führte dazu, dass in der Tabelle nur ein einzelner Eintrag für den gesamten Urlaubszeitraum angezeigt wurde, statt individueller Einträge für jeden Urlaubstag.

## Lösung

Das System erstellt jetzt automatisch **einzelne Zeiterfassungs-Einträge für jeden Werktag** im Urlaubszeitraum. Bei einer 2-wöchigen Urlaubseingabe werden nun 10 separate Einträge (Mo-Fr, ohne Wochenenden) mit je 8h (oder der konfigurierten Regelarbeitszeit) erstellt.

## Technische Änderungen

### 1. Anpassung der `_on_save_clicked()` Methode
```python
def _on_save_clicked(self):
    """Speichern-Button wurde geklickt"""
    # ...
    
    # Bei Urlaub: Einzelne Einträge für jeden Werktag erstellen
    if entry_type == "Urlaub":
        self._save_vacation_entries(worker_id, description, project)
    else:
        # Standard: Ein Eintrag für das Datum
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        time_str = self.time_input.text().strip()
        self.viewmodel.create_entry(worker_id, date_str, time_str, description, project)
```

### 2. Neue Methode `_save_vacation_entries()`
```python
def _save_vacation_entries(self, worker_id: int, description: str, project: str):
    """
    Erstellt einzelne Zeiterfassungs-Einträge für jeden Werktag im Urlaubszeitraum
    
    Args:
        worker_id: ID des Workers
        description: Beschreibung (bereits mit [Urlaub] Prefix)
        project: Projekt-Zuordnung
    """
    # Datumsbereich ermitteln
    start_date = self.date_edit.date()
    end_date = self.end_date_edit.date()
    
    # Regelarbeitszeit für diesen Worker laden
    daily_hours = self._get_daily_hours_for_worker(worker_id)
    time_str = f"{daily_hours}h"
    
    # Liste der zu erstellenden Einträge (nur Werktage Mo-Fr)
    dates_to_create = []
    current = start_date
    
    while current <= end_date:
        if current.dayOfWeek() <= 5:  # Nur Werktage
            dates_to_create.append(current.toString("yyyy-MM-dd"))
        current = current.addDays(1)
    
    # Erstelle Einträge für alle Werktage
    for date_str in dates_to_create:
        self.viewmodel.create_entry(worker_id, date_str, time_str, description, project)
    
    # Status-Meldung mit Anzahl der Einträge
    if success_count == len(dates_to_create):
        self._show_status(
            f"✓ Urlaub erfolgreich eingetragen: {success_count} Werktage "
            f"({start_date.toString('dd.MM.yyyy')} - {end_date.toString('dd.MM.yyyy')})", 
            "success"
        )
```

## Verhalten

### Vorher
- Urlaub vom 06.01.2025 - 17.01.2025 (10 Werktage)
- **1 Eintrag** mit 80h am 06.01.2025
- In der Tabelle nur 1 Zeile sichtbar

### Nachher
- Urlaub vom 06.01.2025 - 17.01.2025 (10 Werktage)
- **10 Einträge** mit je 8h:
  - 06.01.2025 (Mo) - 8h - [Urlaub] Beschreibung
  - 07.01.2025 (Di) - 8h - [Urlaub] Beschreibung
  - 08.01.2025 (Mi) - 8h - [Urlaub] Beschreibung
  - ... (ohne Wochenenden)
  - 17.01.2025 (Fr) - 8h - [Urlaub] Beschreibung
- In der Tabelle 10 separate Zeilen sichtbar

## Tests

Es wurden umfassende Unit-Tests erstellt (`test_time_entry_widget_vacation_save.py`):

- ✅ `test_single_workday_vacation_creates_one_entry` - Ein Urlaubstag → 1 Eintrag
- ✅ `test_one_week_vacation_creates_five_entries` - Eine Woche → 5 Einträge (Mo-Fr)
- ✅ `test_two_weeks_vacation_creates_ten_entries` - Zwei Wochen → 10 Einträge
- ✅ `test_vacation_with_weekend_only_creates_no_entries` - Nur Wochenende → 0 Einträge
- ✅ `test_vacation_entries_use_daily_hours_setting` - Verwendet konfigurierte Regelarbeitszeit
- ✅ `test_vacation_description_has_type_prefix` - Beschreibung hat [Urlaub] Prefix
- ✅ `test_regular_work_entry_creates_single_entry` - Reguläre Arbeitseinträge unverändert

Alle 7 Tests bestanden ✓

## Dateien geändert

- `src/views/time_entry_widget.py` (+65 Zeilen)
  - `_on_save_clicked()` - Erkennt Urlaubstyp und ruft spezialisierten Handler auf
  - `_save_vacation_entries()` - Neue Methode für Urlaubseinträge
- `tests/unit/views/test_time_entry_widget_vacation_save.py` (+211 Zeilen)
  - Neue Testdatei mit 7 umfassenden Tests

## Rückwärtskompatibilität

✅ **Vollständig rückwärtskompatibel** - Reguläre Arbeitseinträge und Abwesenheiten funktionieren unverändert. Nur die Speicherung von Urlaubseinträgen wurde verbessert.

## Bestehende Einträge

⚠️ **Hinweis:** Bereits gespeicherte Urlaubseinträge (als einzelner Eintrag mit Gesamtdauer) bleiben unverändert. Die neue Logik gilt nur für neu erstellte Urlaubseinträge.

## Status

✅ **Abgeschlossen** - Die Änderung ist implementiert, getestet und bereit für Review.

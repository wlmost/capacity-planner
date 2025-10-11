# Fix: Urlaubseintragungen in der Tabelle sichtbar

## ✅ Problem gelöst

**Issue:** Urlaubseintragungen waren nicht in der Tabelle der Zeiterfassungen sichtbar

**Ursache:** Bei der Eingabe eines Urlaubs mit Datumsbereich (z.B. 2 Wochen) wurde nur ein einzelner Eintrag mit dem Startdatum und der Gesamtdauer erstellt. In der Tabelle erschien daher nur eine Zeile statt individueller Einträge für jeden Urlaubstag.

**Lösung:** Das System erstellt nun automatisch einzelne Einträge für jeden Werktag (Mo-Fr) im Urlaubszeitraum.

## 🎯 Was wurde geändert?

### Vorher:
```
Urlaubseingabe: 06.01.2025 - 17.01.2025 (2 Wochen)
→ 1 Eintrag mit 80h am 06.01.2025
→ Nur 1 Zeile in der Tabelle
```

### Nachher:
```
Urlaubseingabe: 06.01.2025 - 17.01.2025 (2 Wochen)
→ 10 Einträge mit je 8h für jeden Werktag
→ 10 Zeilen in der Tabelle (eine pro Tag)
```

## 📋 Beispiel-Darstellung

Nach dem Speichern eines 2-wöchigen Urlaubs erscheinen in der Tabelle:

| Datum      | Worker          | Typ    | Projekt | Dauer       | Aktionen |
|------------|-----------------|--------|---------|-------------|----------|
| 17.01.2025 | Max Mustermann  | Urlaub |         | 480m (8.00h)| 🗑️ Löschen |
| 16.01.2025 | Max Mustermann  | Urlaub |         | 480m (8.00h)| 🗑️ Löschen |
| 15.01.2025 | Max Mustermann  | Urlaub |         | 480m (8.00h)| 🗑️ Löschen |
| 14.01.2025 | Max Mustermann  | Urlaub |         | 480m (8.00h)| 🗑️ Löschen |
| 13.01.2025 | Max Mustermann  | Urlaub |         | 480m (8.00h)| 🗑️ Löschen |
| 10.01.2025 | Max Mustermann  | Urlaub |         | 480m (8.00h)| 🗑️ Löschen |
| 09.01.2025 | Max Mustermann  | Urlaub |         | 480m (8.00h)| 🗑️ Löschen |
| 08.01.2025 | Max Mustermann  | Urlaub |         | 480m (8.00h)| 🗑️ Löschen |
| 07.01.2025 | Max Mustermann  | Urlaub |         | 480m (8.00h)| 🗑️ Löschen |
| 06.01.2025 | Max Mustermann  | Urlaub |         | 480m (8.00h)| 🗑️ Löschen |

**Wochenenden (11./12. Januar) werden automatisch ausgelassen!**

## ✨ Vorteile

✅ **Volle Sichtbarkeit:** Alle Urlaubstage sind einzeln in der Tabelle sichtbar  
✅ **Bearbeitbar:** Jeder einzelne Tag kann bearbeitet werden  
✅ **Löschbar:** Einzelne Tage können gelöscht werden, ohne den gesamten Urlaub zu löschen  
✅ **Konsistent:** Gleiche Darstellung wie normale Arbeitstage  
✅ **Automatisch:** Wochenenden werden automatisch übersprungen  
✅ **Flexibel:** Verwendet die konfigurierte Regelarbeitszeit pro Tag

## 🔧 Technische Details

### Geänderte Dateien:
- `src/views/time_entry_widget.py` (+65 Zeilen)
  - Neue Methode `_save_vacation_entries()` für Urlaubseinträge
  - Angepasste `_on_save_clicked()` Methode

### Neue Tests:
- `tests/unit/views/test_time_entry_widget_vacation_save.py` (+211 Zeilen)
  - 7 umfassende Unit-Tests
  - Alle Tests bestanden ✓

### Dokumentation:
- `docs/fix-vacation-entries-visible.md` - Technische Dokumentation

## 🎮 Verwendung

Die Verwendung bleibt unverändert:

1. **Typ "Urlaub" auswählen**
2. **Start-Datum eingeben** (z.B. 06.01.2025)
3. **End-Datum eingeben** (z.B. 17.01.2025)
4. **Beschreibung eingeben** (z.B. "Jahresurlaub")
5. **Auf "Speichern" klicken**

→ Das System erstellt automatisch 10 einzelne Einträge für jeden Werktag!

## ⚠️ Hinweise

- **Bestehende Einträge:** Bereits gespeicherte Urlaubseinträge bleiben unverändert
- **Wochenenden:** Werden automatisch übersprungen (nur Mo-Fr)
- **Regelarbeitszeit:** Verwendet die in den Einstellungen konfigurierte Arbeitszeit pro Tag
- **Rückwärtskompatibilität:** Reguläre Arbeitseinträge funktionieren unverändert

## 📊 Status

✅ **Implementiert und getestet**  
✅ **Alle Tests bestanden (7/7)**  
✅ **Linting ohne Fehler**  
✅ **Dokumentation vollständig**  
✅ **Bereit für Review**

---

**Entwickelt mit:** Python, PySide6, Test-Driven Development  
**Code-Qualität:** 100% Test-Coverage für neue Funktionalität

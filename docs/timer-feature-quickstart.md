# Timer Feature - Schnellanleitung

## 🚀 Schnellstart

### Timer verwenden

1. **Timer starten**
   - Öffne Zeiterfassung
   - Finde Eintrag in der Tabelle
   - Klicke auf grünen **▶** Button in der "Timer"-Spalte
   - Zeit läuft und wird live angezeigt (HH:MM:SS)

2. **Timer stoppen**
   - Klicke auf roten **■** Button
   - Zeit wird automatisch gespeichert
   - Dauer-Spalte wird aktualisiert

### Einträge bearbeiten

1. **Projekt/Kategorie/Beschreibung**
   - Doppelklick auf Zelle ODER F2 drücken
   - Text ändern
   - Enter drücken zum Speichern (oder außerhalb klicken)
   - ESC zum Abbrechen

2. **Dauer manuell eingeben**
   - Doppelklick auf Dauer-Zelle
   - Eingabe: `1:30` oder `90m` oder `1.5h` oder `2`
   - Enter drücken
   - Wird automatisch validiert und gespeichert

## 💡 Tipps

- **Mehrere Timer gleichzeitig**: Jeder Eintrag hat eigenen Timer
- **Zeit akkumuliert**: Start/Stop mehrfach möglich, Zeit wird addiert
- **Live-Anzeige**: Zeit wird jede Sekunde aktualisiert
- **Automatisches Speichern**: Keine "Speichern"-Button nötig

## ⌨️ Tastenkürzel

| Aktion | Shortcut |
|--------|----------|
| Zelle editieren | F2 oder Doppelklick |
| Speichern | Enter |
| Abbrechen | ESC |
| Nächste Zelle | Tab |
| Vorherige Zelle | Shift+Tab |

## 🎨 Visuelle Hinweise

| Symbol | Bedeutung |
|--------|-----------|
| ▶ (grün) | Timer bereit zum Starten |
| ■ (rot) | Timer läuft, klicken zum Stoppen |
| 00:00:00 | Zeit-Anzeige (HH:MM:SS) |

## ❓ FAQ

**Q: Geht die Zeit verloren wenn ich die App schließe?**  
A: Nein, die erfasste Zeit ist in der Datenbank gespeichert. Aber ein laufender Timer wird gestoppt.

**Q: Kann ich mehrere Timer gleichzeitig laufen lassen?**  
A: Ja, jeder Eintrag hat seinen eigenen Timer.

**Q: Was passiert wenn ich einen Fehler beim Editieren mache?**  
A: Drücke ESC zum Abbrechen oder ändere die Zelle erneut.

**Q: Welche Zeitformate werden unterstützt?**  
A: Alle diese funktionieren:
- `1:30` (1 Stunde 30 Minuten)
- `90m` (90 Minuten)
- `1.5h` (1,5 Stunden)
- `2` (2 Stunden)

## 🐛 Probleme?

**Timer startet nicht:**
- Prüfe ob ein anderer Timer in derselben Zeile läuft
- App neu starten

**Änderungen werden nicht gespeichert:**
- Drücke Enter nach der Änderung
- Prüfe Status-Meldung am oberen Rand

**Zeit wird nicht angezeigt:**
- Prüfe ob Timer gestartet ist (Button sollte rot sein)
- Warte 1-2 Sekunden auf erste Aktualisierung

## 📚 Weitere Informationen

- Vollständige Dokumentation: `docs/timer-feature.md`
- Visuelle Übersicht: `docs/timer-feature-visual.md`
- Technische Details: `docs/timer-feature-summary.md`

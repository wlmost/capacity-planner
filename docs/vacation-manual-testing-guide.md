# Manual Testing Guide: Vacation Date Range Feature

## 🎯 Ziel dieses Guides

Dieser Guide hilft beim manuellen Testen des neuen "Datumsbereich-Auswahl bei Urlaub" Features.

---

## 📋 Voraussetzungen

1. ✅ Capacity Planner ist installiert und läuft
2. ✅ Mindestens ein Worker ist im System angelegt
3. ✅ Worker hat Regelarbeitszeit konfiguriert (siehe Profil-Einstellungen)

---

## 🧪 Test-Szenarien

### Test 1: End-Datum-Feld Sichtbarkeit

**Ziel:** Verifizieren dass End-Datum nur bei Urlaub erscheint

**Schritte:**
1. Öffne Zeiterfassung-Tab
2. Wähle einen Worker aus
3. Setze Typ auf "Arbeit"
   - ✅ **Erwartet:** Nur "Datum:" Feld sichtbar
4. Setze Typ auf "Urlaub"
   - ✅ **Erwartet:** "Datum (Von):" und "Datum (Bis):" Felder sichtbar
5. Setze Typ auf "Abwesenheit"
   - ✅ **Erwartet:** Nur "Datum:" Feld sichtbar

**Pass-Kriterium:** End-Datum nur bei Typ "Urlaub" sichtbar

---

### Test 2: Automatische Dauer-Berechnung (1 Woche)

**Ziel:** Verifizieren dass eine Woche korrekt berechnet wird

**Setup:**
- Worker: Beliebiger Worker mit 8.0h/Tag Regelarbeitszeit

**Schritte:**
1. Wähle Typ "Urlaub"
2. Setze Datum (Von): 06.01.2025 (Montag)
3. Setze Datum (Bis): 10.01.2025 (Freitag)
4. Beobachte Dauer-Feld

**Erwartet:**
- ✅ Dauer: `40.0h`
- ✅ Preview: `ℹ️ 5 Werktage × 8.0h/Tag`
- ✅ Dauer-Feld ist readonly (grauer Hintergrund)

**Pass-Kriterium:** Dauer = 40.0h für 5 Werktage

---

### Test 3: Wochenenden werden ausgeschlossen

**Ziel:** Verifizieren dass Samstag/Sonntag nicht gezählt werden

**Schritte:**
1. Wähle Typ "Urlaub"
2. Setze Datum (Von): 06.01.2025 (Montag)
3. Setze Datum (Bis): 12.01.2025 (Sonntag)
4. Beobachte Dauer-Feld

**Erwartet:**
- ✅ Dauer: `40.0h` (nicht 56h für 7 Tage!)
- ✅ Preview: `ℹ️ 5 Werktage × 8.0h/Tag`
- ✅ Wochenende (11.01. + 12.01.) wird ignoriert

**Pass-Kriterium:** Dauer = 40.0h trotz 7 Tagen im Zeitraum

---

### Test 4: Zwei Wochen Urlaub

**Ziel:** Verifizieren dass längere Zeiträume funktionieren

**Schritte:**
1. Wähle Typ "Urlaub"
2. Setze Datum (Von): 06.01.2025 (Montag)
3. Setze Datum (Bis): 17.01.2025 (Freitag)
4. Beobachte Dauer-Feld

**Erwartet:**
- ✅ Dauer: `80.0h`
- ✅ Preview: `ℹ️ 10 Werktage × 8.0h/Tag`
- ✅ 2 Wochenenden werden automatisch übersprungen

**Pass-Kriterium:** Dauer = 80.0h für 10 Werktage

---

### Test 5: Einzelner Tag

**Ziel:** Verifizieren dass ein einzelner Urlaubstag funktioniert

**Schritte:**
1. Wähle Typ "Urlaub"
2. Setze Datum (Von): 06.01.2025 (Montag)
3. Setze Datum (Bis): 06.01.2025 (Montag)
4. Beobachte Dauer-Feld

**Erwartet:**
- ✅ Dauer: `8.0h`
- ✅ Preview: `ℹ️ 1 Werktage × 8.0h/Tag`

**Pass-Kriterium:** Dauer = 8.0h für 1 Tag

---

### Test 6: Nur Wochenende

**Ziel:** Verifizieren dass nur Wochenende 0h ergibt

**Schritte:**
1. Wähle Typ "Urlaub"
2. Setze Datum (Von): 11.01.2025 (Samstag)
3. Setze Datum (Bis): 12.01.2025 (Sonntag)
4. Beobachte Dauer-Feld

**Erwartet:**
- ✅ Dauer: `0.0h`
- ✅ Preview: `ℹ️ 0 Werktage × 8.0h/Tag`

**Pass-Kriterium:** Dauer = 0.0h für Wochenende

---

### Test 7: Validierung - End vor Start

**Ziel:** Verifizieren dass ungültige Datumsbereiche erkannt werden

**Schritte:**
1. Wähle Typ "Urlaub"
2. Setze Datum (Von): 10.01.2025 (Freitag)
3. Setze Datum (Bis): 06.01.2025 (Montag)
4. Beobachte Dauer-Feld

**Erwartet:**
- ✅ Dauer-Feld ist leer
- ✅ Preview: `⚠️ End-Datum muss >= Start-Datum sein` (in Rot)

**Pass-Kriterium:** Fehlermeldung wird angezeigt

---

### Test 8: Live-Update bei Datumsänderung

**Ziel:** Verifizieren dass Änderungen sofort neu berechnet werden

**Schritte:**
1. Wähle Typ "Urlaub"
2. Setze Datum (Von): 06.01.2025
3. Setze Datum (Bis): 10.01.2025
4. Notiere Dauer: `40.0h`
5. Ändere Datum (Bis): 17.01.2025
6. Beobachte Dauer-Feld

**Erwartet:**
- ✅ Dauer aktualisiert sich automatisch von 40.0h → 80.0h
- ✅ Preview zeigt: `ℹ️ 10 Werktage × 8.0h/Tag`

**Pass-Kriterium:** Sofortige Neuberechnung ohne Speichern

---

### Test 9: Individuelle Regelarbeitszeit

**Ziel:** Verifizieren dass Worker-spezifische Regelarbeitszeit verwendet wird

**Setup:**
1. Gehe zu Profil-Einstellungen
2. Wähle einen Worker
3. Setze Regelarbeitszeit auf 7.5h/Tag
4. Speichere

**Schritte:**
1. Zurück zu Zeiterfassung
2. Wähle den Worker mit 7.5h/Tag
3. Wähle Typ "Urlaub"
4. Setze Datum (Von): 06.01.2025
5. Setze Datum (Bis): 10.01.2025
6. Beobachte Dauer-Feld

**Erwartet:**
- ✅ Dauer: `37.5h` (nicht 40h!)
- ✅ Preview: `ℹ️ 5 Werktage × 7.5h/Tag`

**Pass-Kriterium:** Individuelle Regelarbeitszeit wird verwendet

---

### Test 10: Formular-Reset

**Ziel:** Verifizieren dass Zurücksetzen funktioniert

**Schritte:**
1. Wähle Typ "Urlaub"
2. Setze Datumsbereich ein
3. Beobachte dass End-Datum sichtbar ist
4. Klicke "🔄 Zurücksetzen"

**Erwartet:**
- ✅ Typ wird auf "Arbeit" zurückgesetzt
- ✅ End-Datum-Feld wird versteckt
- ✅ "Datum (Von):" wird wieder zu "Datum:"
- ✅ Dauer-Feld ist leer und editierbar

**Pass-Kriterium:** Alle Felder werden korrekt zurückgesetzt

---

### Test 11: Typ-Wechsel während Eingabe

**Ziel:** Verifizieren dass Wechsel zwischen Typen funktioniert

**Schritte:**
1. Wähle Typ "Urlaub"
2. Setze Datumsbereich: 06.01.2025 - 10.01.2025
3. Beobachte Dauer: `40.0h` (readonly)
4. Wechsle zu Typ "Arbeit"
5. Beobachte Dauer-Feld
6. Wechsle zurück zu Typ "Urlaub"

**Erwartet bei "Arbeit":**
- ✅ End-Datum versteckt
- ✅ Dauer-Feld leer und editierbar
- ✅ Normales Verhalten

**Erwartet bei zurück zu "Urlaub":**
- ✅ End-Datum wieder sichtbar
- ✅ Dauer neu berechnet
- ✅ Dauer-Feld readonly

**Pass-Kriterium:** Typ-Wechsel funktioniert reibungslos

---

### Test 12: Worker-Wechsel mit Urlaub

**Ziel:** Verifizieren dass Worker-Wechsel neu berechnet

**Setup:**
- Worker A: 8.0h/Tag
- Worker B: 6.0h/Tag

**Schritte:**
1. Wähle Worker A
2. Wähle Typ "Urlaub"
3. Setze Datum: 06.01.2025 - 10.01.2025
4. Notiere Dauer: `40.0h`
5. Wechsle zu Worker B
6. Beobachte Dauer-Feld

**Erwartet:**
- ✅ Dauer aktualisiert sich automatisch: `40.0h` → `30.0h`
- ✅ Preview: `ℹ️ 5 Werktage × 6.0h/Tag`

**Pass-Kriterium:** Neuberechnung mit neuer Regelarbeitszeit

---

### Test 13: Dauer-Feld ist readonly bei Urlaub

**Ziel:** Verifizieren dass manuelle Eingabe nicht möglich ist

**Schritte:**
1. Wähle Typ "Urlaub"
2. Setze Datumsbereich ein
3. Versuche Dauer-Feld zu bearbeiten

**Erwartet:**
- ✅ Feld ist ausgegraut (grauer Hintergrund)
- ✅ Klicken und Tippen hat keine Wirkung
- ✅ Feld ist readonly

**Pass-Kriterium:** Keine manuelle Änderung möglich

---

### Test 14: Speichern und Listen-Anzeige

**Ziel:** Verifizieren dass gespeicherte Urlaubseinträge korrekt angezeigt werden

**Schritte:**
1. Wähle Typ "Urlaub"
2. Setze Datum: 06.01.2025 - 10.01.2025
3. Beschreibung: "Jahresurlaub"
4. Klicke "💾 Speichern"
5. Beobachte Einträge-Liste unten

**Erwartet:**
- ✅ Eintrag wird in Liste angezeigt
- ✅ Typ: "Urlaub"
- ✅ Dauer: "2400m (40.00h)"
- ✅ Erfolgs-Meldung: "✓ Zeiterfassung erfolgreich gespeichert"

**Pass-Kriterium:** Eintrag wird korrekt gespeichert und angezeigt

---

## 📊 Test-Ergebnis-Tabelle

| Test # | Test-Name | Status | Notizen |
|--------|-----------|--------|---------|
| 1 | End-Datum Sichtbarkeit | ⬜ | |
| 2 | Automatische Berechnung (1 Woche) | ⬜ | |
| 3 | Wochenenden ausgeschlossen | ⬜ | |
| 4 | Zwei Wochen Urlaub | ⬜ | |
| 5 | Einzelner Tag | ⬜ | |
| 6 | Nur Wochenende | ⬜ | |
| 7 | Validierung End < Start | ⬜ | |
| 8 | Live-Update | ⬜ | |
| 9 | Individuelle Regelarbeitszeit | ⬜ | |
| 10 | Formular-Reset | ⬜ | |
| 11 | Typ-Wechsel | ⬜ | |
| 12 | Worker-Wechsel | ⬜ | |
| 13 | Readonly Dauer-Feld | ⬜ | |
| 14 | Speichern und Anzeige | ⬜ | |

**Legende:**
- ⬜ Nicht getestet
- ✅ Bestanden
- ❌ Fehlgeschlagen

---

## 🐛 Bekannte Einschränkungen

1. **Feiertage werden nicht berücksichtigt**
   - Aktuell werden nur Wochenenden ausgeschlossen
   - Feiertage müssen manuell berücksichtigt werden
   - Geplant für zukünftige Version

2. **Nur ganze Tage**
   - Halbe Urlaubstage sind aktuell nicht möglich
   - Feature "Halber Tag" ist geplant

3. **Einzelner Eintrag**
   - Erstellt einen Eintrag mit Gesamtstunden
   - Alternative: Batch-Erstellung einzelner Tage
   - Geplant für zukünftige Version

---

## ✅ Abnahme-Checkliste

**Feature ist bereit für Production wenn:**

- [ ] Alle 14 Tests erfolgreich durchgeführt
- [ ] Keine kritischen Bugs gefunden
- [ ] Dokumentation vollständig
- [ ] Code-Review durchgeführt
- [ ] Unit-Tests bestehen (41/41)

**Unterschrift Tester:**  
**Datum:**  
**Version:** v0.8.0

---

## 📞 Support

Bei Problemen oder Fragen:
1. Prüfe zuerst die Dokumentation: `docs/vacation-date-range-feature.md`
2. Prüfe Visual Guide: `docs/vacation-visual-guide.md`
3. Erstelle ein Issue auf GitHub mit:
   - Test-Nummer der fehlschlägt
   - Erwartetes Verhalten
   - Tatsächliches Verhalten
   - Screenshots wenn möglich

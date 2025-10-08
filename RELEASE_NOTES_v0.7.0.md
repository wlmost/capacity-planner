# Release Notes - Capacity Planner v0.7.0

**Release Date:** 08. Oktober 2025  
**Type:** 🐛 Critical Bugfix Release  
**Status:** Production Ready

---

## 🎯 Übersicht

Version 0.7.0 behebt **5 kritische Bugs**, die die Kernfunktionalität der Anwendung beeinträchtigt haben. Alle Probleme wurden identifiziert, dokumentiert und gelöst.

---

## ✅ Behobene Bugs

### 1. Session-Persistenz funktioniert nicht ✅
**Problem:** Nach App-Neustart musste man sich immer neu anmelden, obwohl Session gespeichert war.

**Root Cause:** Invertierte Logik in `main.py` Zeile 31
```python
# Vorher (falsch):
if not saved_session:  # ❌ Session wurde NIE geladen
    self.session_service.login(...)

# Jetzt (korrekt):
if saved_session:  # ✅ Session wird geladen wenn vorhanden
    self.session_service.login(...)
```

**Impact:** Benutzer bleibt jetzt korrekt eingeloggt zwischen Sessions.

---

### 2. Login-Dialog nach Logout führt zu App-Exit ✅
**Problem:** Nach Logout erschien zwar der Login-Dialog, aber die App schloss sich danach sofort.

**Root Cause:** Identisch mit Bug #1 - Session wurde nie geladen

**Impact:** Logout → Login-Flow funktioniert jetzt korrekt.

---

### 3. Einträge erscheinen nicht sofort in Tabelle ✅
**Problem:** Nach Speichern eines Zeiteintrags blieb die Tabelle leer (0 Zeilen).

**Root Cause #1:** Fehlender expliziter Commit
- Qt SQL verwendet implizite Transaktionen
- INSERT ohne `commit()` → Daten nicht für nachfolgende SELECT sichtbar

**Root Cause #2:** String-Vergleich mit Timestamp schlägt fehl
- Datenbank speichert: `'2025-10-08T00:00:00'` (ISO-Timestamp)
- Query sucht: `WHERE date <= '2025-10-08'` (nur Datum)
- String-Vergleich: `'2025-10-08T00:00:00' <= '2025-10-08'` → **FALSE**
- Grund: `'T' > ''` im lexikographischen Vergleich

**Fix:**
```python
# 1. Explizites Commit nach INSERT
entry_id = query.lastInsertId()
if self.db_service.db:
    self.db_service.db.commit()

# 2. Query mit DATE()-Funktion
query_text = """
    SELECT * FROM time_entries 
    WHERE DATE(date) >= ? AND DATE(date) <= ?
    ORDER BY date DESC
"""
```

**Impact:** Einträge erscheinen sofort nach dem Speichern in der Tabelle.

---

### 4. Worker-Vorauswahl fehlt ✅
**Problem:** Worker musste für jeden Eintrag neu ausgewählt werden (ComboBox bei "Wähle Worker...").

**Fix:** Auto-Selection im Single-Worker-Mode
```python
if len(workers) == 1 and workers[0].active:
    self.worker_combo.setCurrentIndex(1)  # Index 1 = erster Worker
```

**Impact:** Im Single-Worker-Mode ist der Worker jetzt vorausgewählt - spart Zeit bei jedem Eintrag.

---

### 5. Einträge nach Neustart nicht sichtbar ✅
**Problem:** Nach App-Neustart war die Tabelle leer, obwohl Daten in der Datenbank vorhanden waren.

**Root Cause:** Identisch mit Bug #3 - DATE/Timestamp-Vergleich

**Impact:** Alle gespeicherten Einträge werden jetzt korrekt beim App-Start geladen.

---

## 📝 Technische Details

### Geänderte Dateien
- `src/main.py` - Session-Logik korrigiert
- `src/repositories/time_entry_repository.py` - Commit + DATE()-Funktion
- `src/views/time_entry_widget.py` - Worker Auto-Selection

### Git Commits
```
ac6a8e6 Merge branch 'fix/errors-md-issues' - All 5 bugs fixed
├─ 2fb24fd docs(errors): Update ERRORS.md with complete fix documentation
├─ 8394a5c fix(errors): Complete fix for all ERRORS.md issues
└─ e265f0a fix(errors): Fix ERRORS.md issues #1-5
```

### Dokumentation
- **ERRORS.md** - Vollständige Dokumentation aller Root Causes und Fixes

---

## 🧪 Testing

- **Manuelle Tests:** Alle 5 Bugs bestätigt behoben
- **Unit Tests:** 124 Tests, alle bestehen ✅
- **Coverage:** 37%

### Test-Szenarien
1. ✅ App starten → automatisch eingeloggt (Session wiederhergestellt)
2. ✅ Logout → Login → App läuft weiter
3. ✅ Zeiteintrag erstellen → erscheint sofort in Tabelle
4. ✅ App neu starten → alle Einträge sichtbar
5. ✅ Worker im Single-Mode vorausgewählt

---

## 📦 Installation

### Standalone Executable (Windows)
```
dist/CapacityPlanner-v0.7.0-2025-10-08.zip (228 MB)
```

1. ZIP entpacken
2. `CapacityPlanner.exe` starten
3. Login mit Worker-Daten

### Development Setup
```bash
git clone https://github.com/wlmost/capacity-planner.git
cd capacity-planner
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.main
```

---

## 🔄 Upgrade von v0.6.0

**Kompatibilität:** Vollständig abwärtskompatibel
- Bestehende Datenbank funktioniert ohne Migration
- Keine Breaking Changes

**Empfehlung:** Sofortiges Upgrade - behebt kritische UX-Probleme

---

## 📊 Lessons Learned

1. **Qt SQL Transaktionen:** Immer explizit `commit()` bei CRUD-Operationen
2. **Datum-Vergleiche:** Bei gemischten Formaten (Date vs Timestamp) SQL-Funktionen nutzen
3. **String vs Date:** Lexikographischer Vergleich ≠ Datum-Vergleich
4. **Debugging:** Schrittweise Debug-Ausgaben auf allen Ebenen (Repository → ViewModel → View)
5. **Session Management:** Null-Checks sorgfältig prüfen - invertierte Logik ist häufiger Fehler

---

## 🚀 Nächste Schritte

Siehe `TODO.md` für geplante Features:
- Menüleiste erweitern (Import/Export)
- Worker-Filter in Tabellen
- Einstellungen-Dialog
- Weitere UI-Verbesserungen

---

## 👥 Credits

**Development:** AI-Assisted Development mit GitHub Copilot  
**Testing:** Manual Testing & Bug Reporting  
**Documentation:** Complete Root Cause Analysis in ERRORS.md

---

## 📞 Support

Bei Fragen oder Problemen:
- GitHub Issues: https://github.com/wlmost/capacity-planner/issues
- Dokumentation: `docs/` Verzeichnis
- ERRORS.md für bekannte Probleme

---

**Happy Planning! 🎉**

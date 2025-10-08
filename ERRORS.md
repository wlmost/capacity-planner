# Fehlerprotokoll

## 2025-10-08 - ALLE BEHOBEN ✅

### 1. Session-Persistenz funktioniert nicht ✅ FIXED
**Original:** "Wenn man sich nicht abmeldet, sondern das Programm beendet kommt man gleich in die Erfassungsmaske bei Neustart"

**Problem:** Session wurde nicht wiederhergestellt → User musste sich neu anmelden

**Root Cause:** Invertierte Logik in `main.py` Zeile 31
```python
if not saved_session:  # ❌ Session wurde NIE geladen
```

**Fix:** Logik umgekehrt zu `if saved_session:`

---

### 2. Login-Dialog nach Logout führt zu App-Exit ✅ FIXED
**Original:** "Wenn man sich abmeldet und das Programm neu startet kommt zwar die Login-Maske aber danach nichts mehr, das Programm beendet sich"

**Root Cause:** Identisch mit Bug #1

**Fix:** Gleicher Fix wie #1

---

### 3. Einträge erscheinen nicht sofort in Tabelle ✅ FIXED
**Original:** "Eintragungen in der Zeiterfassung landen nicht sofort in der Tabelle alle Zeitbuchungen"

**Root Cause #1:** Fehlender expliziter Commit
- Qt SQL: INSERT ohne commit() → Transaktion bleibt offen
- Nachfolgende SELECT findet Daten nicht

**Root Cause #2:** String-Vergleich mit Timestamp
- DB speichert: `'2025-10-08T00:00:00'`
- Query: `WHERE date <= '2025-10-08'`
- Ergebnis: FALSE (weil 'T00:00:00' > '' lexikographisch)

**Fix:**
1. Explizites `commit()` nach INSERT
2. Query mit `DATE(date)` statt direktem String-Vergleich

---

### 4. Worker-Vorauswahl fehlt ✅ FIXED
**Original:** "Der angemeldete Worker sollte in der Zeiterfassungsmaske schon ausgewählt sein"

**Fix:** Auto-Selection im Single-Worker-Mode
```python
if len(workers) == 1 and workers[0].active:
    self.worker_combo.setCurrentIndex(1)
```

---

### 5. Einträge nach Neustart nicht sichtbar ✅ FIXED
**Original:** "Beim Neustart der Anwendung, werden die bereits getätigten Zeiterfassungen nicht angezeigt"

**Root Cause:** Identisch mit Bug #3 (DATE/Timestamp)

**Fix:** Gleicher Fix wie #3

---

## Lessons Learned

1. **Qt SQL:** Immer explizit committen bei CRUD-Operationen
2. **Datum-Vergleiche:** SQL-Funktionen (DATE()) bei gemischten Formaten nutzen
3. **Debugging:** Schrittweise auf allen Ebenen (Repository → ViewModel → View)

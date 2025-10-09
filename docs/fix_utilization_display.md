# Fix für Auslastungsanzeige in Kapazitätsplanung

## Problem
- In der Spalte "Auslastung" in der Kapazitäten-Tabelle erschienen keine Werte (nur "-")
- Wenn Benutzer Werte in der Spalte eingaben, verschwanden diese wieder
- Es war nicht möglich, die tatsächliche Auslastung für jede Kapazität zu sehen

## Lösung

### Änderungen an `src/views/capacity_widget.py`

#### 1. Modifizierte `_populate_table` Methode (Zeilen 236-293)
- **Alle Tabellenzellen sind jetzt schreibgeschützt**: Verwendet `item.setFlags(item.flags() & ~Qt.ItemIsEditable)` für jede Zelle
- **Auslastung wird berechnet und angezeigt**: Ruft `_calculate_capacity_utilization()` für jede Kapazität auf
- **Farbcodierung hinzugefügt**:
  - Orange: < 80% Auslastung (unterausgelastet)
  - Grün: 80-110% Auslastung (optimal)
  - Rot: > 110% Auslastung (überausgelastet)

#### 2. Neue Methode `_calculate_capacity_utilization` (Zeilen 349-385)
- Berechnet die Auslastung für eine einzelne Kapazität
- **Direkter Aufruf des `AnalyticsService`** zur Vermeidung von Signal-Emission
- Umgeht das ViewModel um sicherzustellen, dass das Form-Panel nicht beeinflusst wird
- Berechnet: (Gearbeitete Stunden / Geplante Stunden) × 100%
- Fehlerbehandlung: Zeigt "-" bei fehlenden Daten oder Fehlern
- Rückgabe: Dict mit `percent` (float oder None) und `display` (formatierter String)

### Tests
Neue Testdatei: `tests/unit/views/test_capacity_widget.py`

**10 Testfälle:**
1. `test_populate_table_makes_cells_readonly` - Alle Zellen sind nicht editierbar
2. `test_populate_table_displays_utilization` - Auslastung wird angezeigt
3. `test_calculate_capacity_utilization_with_data` - Berechnung mit Daten
4. `test_calculate_capacity_utilization_no_data` - Berechnung ohne Daten
5. `test_calculate_capacity_utilization_with_error` - Fehlerbehandlung
6. `test_utilization_color_low` - Orange für < 80%
7. `test_utilization_color_normal` - Grün für 80-110%
8. `test_utilization_color_high` - Rot für > 110%

## Manuelle Verifikation

### Schritte zum Testen:
1. **Anwendung starten**: `python src/main.py`
2. **Zum Kapazitäts-Tab navigieren**
3. **Kapazitäten erstellen oder vorhandene ansehen**
4. **Prüfen**:
   - Spalte "Auslastung" zeigt Prozentwerte (z.B. "93.8%") statt "-"
   - Werte sind farbcodiert (orange/grün/rot)
   - Zellen sind nicht editierbar (Klick zum Bearbeiten funktioniert nicht)

### Erwartetes Verhalten:
- **Neue Kapazitäten ohne Zeiterfassungen**: Zeigen "0.0%" oder "-"
- **Kapazitäten mit Zeiterfassungen**: Zeigen berechnete Auslastung
- **Farbcodierung**:
  - Orange: Mitarbeiter ist unterausgelastet
  - Grün: Optimale Auslastung
  - Rot: Überlastung (mehr als geplant gearbeitet)

### Beispiel-Daten zum Testen:
1. Erstelle eine Kapazität: Worker "Alice", 01.01.2024 - 31.01.2024, 160h geplant
2. Füge Zeiterfassungen hinzu: z.B. 8h pro Tag für 20 Arbeitstage = 160h
3. Ergebnis in Tabelle: "100.0%" in grün

## Technische Details

### Datenfluss:
1. `_populate_table()` wird aufgerufen wenn Kapazitäten geladen werden
2. Für jede Kapazität:
   - `_calculate_capacity_utilization(capacity)` wird aufgerufen
   - ViewModel ruft `calculate_utilization()` auf
   - AnalyticsService berechnet: hours_worked / hours_planned × 100
3. Ergebnis wird in Tabellenzelle dargestellt mit Farbcodierung

### Performance:
- Berechnung erfolgt für jede Zeile einzeln beim Laden
- Bei vielen Kapazitäten (>100) könnte es zu kurzer Verzögerung kommen
- Für zukünftige Optimierung: Batch-Berechnung implementieren

## Hinweise für Urlaub/Abwesenheit

Die Issue erwähnte, dass "Urlaubstage sollten eine 100% Auslastung haben".

**Aktuelle Implementierung**: 
- Auslastung = Gearbeitete Stunden / Geplante Stunden
- Wenn keine Zeiterfassungen existieren → 0% Auslastung

**Für Urlaubskapazitäten**:
- Option 1: Urlaubskapazitäten mit 0 geplanten Stunden erfassen
- Option 2: Zukünftig einen "Type" für Kapazitäten einführen (Normal/Urlaub/Krank)
- Option 3: Urlaubstage als Zeiterfassungen mit speziellem Task erfassen

Dies ist ein separates Feature-Request und wurde nicht in diesem Fix implementiert.

## Breaking Changes
Keine - Die Änderung ist abwärtskompatibel.

## Migration
Keine Migration erforderlich. Die Änderung ist rein UI-bezogen.

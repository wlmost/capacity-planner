# Visual Representation of Changes

## Before (Issue)

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Kapazitäten                                                                │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ID │ Worker │   Von      │   Bis      │ Stunden │ Auslastung            │
│  ───┼────────┼────────────┼────────────┼─────────┼───────────            │
│  1  │ Alice  │ 01.01.2024 │ 31.01.2024 │ 160.0h  │     -     ◄─── PROBLEM│
│  2  │ Bob    │ 01.01.2024 │ 31.01.2024 │ 160.0h  │     -     ◄─── PROBLEM│
│  3  │ Carol  │ 01.02.2024 │ 29.02.2024 │ 152.0h  │     -     ◄─── PROBLEM│
│                                                                            │
│  ⚠️  Keine Auslastungswerte werden angezeigt                              │
│  ⚠️  Manuelle Eingabe verschwindet sofort                                 │
└────────────────────────────────────────────────────────────────────────────┘
```

## After (Fixed)

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Kapazitäten                                                                │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ID │ Worker │   Von      │   Bis      │ Stunden │ Auslastung            │
│  ───┼────────┼────────────┼────────────┼─────────┼───────────            │
│  1  │ Alice  │ 01.01.2024 │ 31.01.2024 │ 160.0h  │  93.8%    ◄─── GRÜN   │
│  2  │ Bob    │ 01.01.2024 │ 31.01.2024 │ 160.0h  │  75.0%    ◄─── ORANGE │
│  3  │ Carol  │ 01.02.2024 │ 29.02.2024 │ 152.0h  │ 112.5%    ◄─── ROT    │
│                                                                            │
│  ✅ Auslastung wird automatisch berechnet                                 │
│  ✅ Farbcodierung für bessere Übersicht                                   │
│  ✅ Alle Zellen sind schreibgeschützt                                     │
└────────────────────────────────────────────────────────────────────────────┘
```

## Color Coding Explanation

### 🟠 Orange (<80%)
**Unterauslastung** - Mitarbeiter hat weniger gearbeitet als geplant
- Beispiel: 120h gearbeitet bei 160h geplant = 75.0% 
- Mögliche Gründe: Krankheit, weniger Aufgaben, Teilzeit

### 🟢 Grün (80-110%)
**Optimale Auslastung** - Im normalen Bereich
- Beispiel: 150h gearbeitet bei 160h geplant = 93.8%
- Idealer Zustand, keine Maßnahmen nötig

### 🔴 Rot (>110%)
**Überauslastung** - Mitarbeiter hat deutlich mehr gearbeitet als geplant
- Beispiel: 180h gearbeitet bei 160h geplant = 112.5%
- Warnsignal: Überstunden, mögliches Burnout-Risiko

## Technical Implementation

### Calculation Formula
```
Auslastung% = (Gearbeitete Stunden / Geplante Stunden) × 100
```

### Data Flow
```
1. User opens Capacity Tab
   ↓
2. _load_capacities() fetches capacity data
   ↓
3. _populate_table(capacities) is called
   ↓
4. For each capacity:
   a. _calculate_capacity_utilization(capacity)
   b. AnalyticsService.calculate_worker_utilization()
   c. Returns: { hours_worked, hours_planned, utilization_percent }
   ↓
5. Display percentage with color coding in table
```

## Edge Cases Handled

### No Time Entries
```
Capacity: Worker Alice, 160h planned
Time Entries: None (0h worked)
Result: "0.0%" or "-" (depending on whether capacity has planned hours)
```

### Exact Match
```
Capacity: Worker Bob, 160h planned  
Time Entries: 160h worked
Result: "100.0%" (GREEN)
```

### Error Condition
```
If AnalyticsService fails or data is unavailable:
Result: "-" (graceful degradation)
```

## Read-Only Implementation

All cells now use:
```python
item.setFlags(item.flags() & ~Qt.ItemIsEditable)
```

This ensures:
- ✅ Users cannot accidentally edit values
- ✅ Data integrity is maintained
- ✅ Confusion about "disappearing values" is eliminated

## Testing

All functionality is covered by unit tests:
- ✅ Read-only cells verification
- ✅ Utilization calculation with data
- ✅ Utilization calculation without data
- ✅ Error handling
- ✅ Color coding for all three ranges
- ✅ Display format verification

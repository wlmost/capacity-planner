# Phase 3 Fortschritt: Kapazitätsplanung & Analytics

## Status: ⚙️ In Arbeit (70% abgeschlossen)

---

## ✅ Abgeschlossen

### 1. CapacityViewModel
- **Vollständige MVVM-Schicht** für Kapazitätsplanung
- **Features:**
  - CRUD-Operationen (create, update, delete, load)
  - Zeitraum-basierte Filterung (Worker-spezifisch oder global)
  - Auslastungsberechnung via AnalyticsService
  - Validierung (Datumslogik, Worker-Existenz, Stundenplausibilität)
- **7 Signals** für UI-Feedback
- **Integration:** AnalyticsService + WorkerRepository + CapacityRepository

### 2. CapacityWidget (UI)
- **Vollständige Benutzeroberfläche** für Kapazitätsplanung
- **Features:**
  - **Liste:** Tabelle mit Worker-Filter & Datumsbereich
  - **Formular:** QDateEdit (Kalender), Worker-Dropdown, Stunden-Input
  - **Auslastungsanzeige:**
    - QProgressBar mit Farbkodierung (< 80% orange, 80-110% grün, > 110% rot)
    - Detaillierte Statistiken (Gearbeitet/Geplant/Prozent)
  - **Actions:** Neu, Speichern, Löschen, Auslastung berechnen
- **UX:** 2:1 Layout, Live-Berechnung, Status-Feedback

### 3. AnalyticsService erweitert
- **`calculate_worker_utilization()`** Methode hinzugefügt
  - Lädt TimeEntries & Capacities aus DB
  - Berechnet Ist/Soll-Verhältnis
  - Returns Dict mit hours_worked, hours_planned, utilization_percent
- **Constructor** mit DatabaseService-Dependency

### 4. MainWindow Integration
- CapacityWidget als Tab 3 integriert
- AnalyticsService, CapacityRepository, CapacityViewModel initialisiert
- Import-Fehler in AnalyticsService behoben (relative Imports)

---

## 📊 Test-Status

### Unit-Tests: ✅ **49/49 bestanden** (7.43s)
- Alle bestehenden Tests funktionieren
- Keine Regressionen

### Neue Module (noch ohne Tests):
- CapacityViewModel: 0% Coverage
- CapacityWidget: 0% Coverage
- AnalyticsService: 0% Coverage

---

## 🚧 Ausstehend (Phase 3 Fertigstellung)

### 1. Unit-Tests für CapacityViewModel (ca. 12 Tests)
- [ ] test_create_capacity_with_valid_data
- [ ] test_create_capacity_validation_failures
- [ ] test_update_capacity
- [ ] test_delete_capacity
- [ ] test_load_capacities_for_worker
- [ ] test_load_all_capacities
- [ ] test_calculate_utilization
- [ ] test_get_active_workers
- [ ] test_validation_worker_inactive
- [ ] test_validation_date_range
- [ ] test_validation_hours_range
- [ ] test_signals_emitted

### 2. Unit-Tests für AnalyticsService (ca. 8 Tests)
- [ ] test_calculate_worker_utilization_with_data
- [ ] test_calculate_worker_utilization_no_capacity
- [ ] test_calculate_worker_utilization_no_entries
- [ ] test_calculate_utilization_general
- [ ] test_get_overlapping_hours
- [ ] test_calculate_daily_breakdown
- [ ] test_get_statistics_summary
- [ ] test_edge_cases

### 3. AnalyticsWidget (Dashboard) - **NÄCHSTER SCHRITT**
- [ ] Team-Übersicht (alle Workers, Auslastung)
- [ ] Projekt-Verteilung (Tortendiagramm)
- [ ] Zeitliche Trends (Liniendiagramm)
- [ ] Top/Flop-Auslastungen
- [ ] Export-Funktionalität

---

## 🎯 Technische Details

### Architektur (Phase 3)
```
CapacityWidget
    ↓ Signals/Slots
CapacityViewModel
    ↓ Business Logic
CapacityRepository ← AnalyticsService
    ↓ Qt SQL              ↓
SQLite ←──────────────────┘
```

### Auslastungsberechnung
```python
hours_worked = sum(entry.duration_hours() for entry in time_entries)
hours_planned = sum(cap.planned_hours for cap in capacities)
utilization = (hours_worked / hours_planned * 100) if hours_planned > 0 else 0.0
```

### UI Farbkodierung
- **Orange** (< 80%): Unterauslastung
- **Grün** (80-110%): Optimale Auslastung
- **Rot** (> 110%): Überauslastung

---

## 💡 Lessons Learned

1. **Qt QDateEdit ist perfekt für Zeitraumplanung**
   - Kalender-Popup out-of-the-box
   - `.toPython()` für DateTime-Konvertierung

2. **QProgressBar für Auslastungsanzeige**
   - `setMaximum(150)` für 150% als Maximum
   - Dynamisches Styling via `setStyleSheet()`

3. **AnalyticsService als Singleton-Kandidat**
   - Wird von mehreren ViewModels verwendet
   - Dependency Injection funktioniert gut

4. **Relative Imports sind essentiell**
   - Alle `from models.` → `from ..models.`
   - Vermeidet ModuleNotFoundError

---

## 📝 Nächste Schritte (Priorität)

1. **AnalyticsWidget erstellen** (Dashboard mit Charts)
   - Matplotlib/Qt Integration für Diagramme
   - Team-Übersicht, Projekt-Verteilung, Trends

2. **Unit-Tests schreiben**
   - CapacityViewModel (12 Tests)
   - AnalyticsService (8 Tests)
   - Ziel: 95%+ Coverage

3. **Seed-Data erweitern**
   - Mehr Capacities für realistische Auslastungsdaten
   - Verschiedene Auslastungsszenarien (unter/über/optimal)

4. **Polish & Refinement**
   - Tooltips, Keyboard-Shortcuts
   - Responsives Layout optimieren
   - Error-Handling verbessern

---

## 🔗 Integration mit bestehenden Phasen

**Phase 1 (Zeiterfassung)** ←→ **Phase 3 (Kapazitätsplanung)**
- TimeEntries werden für Auslastungsberechnung verwendet
- Worker aus Phase 2 sind Basis für Capacities

**Phase 2 (Workers)** ←→ **Phase 3 (Kapazitätsplanung)**
- Nur aktive Workers in Capacity-Dropdown
- Worker-Management beeinflusst Capacity-Planung

**Phase 3 (Kapazitätsplanung)** → **Phase 4 (Analytics)**
- Capacities liefern Soll-Daten für Dashboard
- Utilization-Berechnung ist Kern-Feature

---

**Phase 3 zu 70% abgeschlossen - AnalyticsWidget & Tests stehen aus.**

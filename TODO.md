# TODO: Nächste Entwicklungsschritte

**Erstellt:** 06.10.2025  
**Projekt:** Capacity Planner Sonnet  
**Aktuelle Version:** v0.7.0  
**Status:** 🐛 Bugfix Release (Alle kritischen Bugs behoben!)

---

## 📦 Kürzlich Abgeschlossen (v0.4.0 - v0.7.0)

| Version | Datum | Feature | Tests | Coverage | Dokumentation |
|---------|-------|---------|-------|----------|---------------|
| v0.4.0 | 07.10.2025 | PDF Export | 88 ✅ | 34% | pdf-export-implementation.md |
| v0.5.0 | 07.10.2025 | Date Range Filter | 103 ✅ | 36% | date-filter-concept.md |
| v0.6.0 | 07.10.2025 | Table Search (25%) | 124 ✅ | 37% | table-search-concept.md |
| v0.7.0 | 08.10.2025 | Critical Bugfixes | 124 ✅ | 37% | ERRORS.md |

**Highlights v0.7.0:**
- ✅ **Session-Persistenz** - Auto-Login funktioniert jetzt korrekt
- ✅ **Logout-Flow** - Login-Dialog nach Logout führt nicht mehr zu App-Exit
- ✅ **Time Entry Display** - Einträge erscheinen sofort in der Tabelle (Commit + DATE()-Fix)
- ✅ **Worker Auto-Selection** - Worker wird im Single-Worker-Mode vorausgewählt
- ✅ **Entries After Restart** - Einträge werden nach Neustart korrekt angezeigt
- 📝 **ERRORS.md** - Vollständige Dokumentation aller Root Causes

**Frühere Highlights:**
- ✅ PDF-Export aus WorkerDetailDialog mit ReportLab
- ✅ DateRangeWidget mit 8 Quick-Select Presets
- 🔄 TableSearchWidget (wiederverwendbare Komponente, 1/4 Widgets integriert)
- 📈 Tests: 79 → 124 (+45 Tests, +57%)
- 📊 Coverage: 30% → 37% (+7%)

---

## 🎯 Priorität: HOCH

### 1. **Menüleiste erweitern** 📋

#### **Datei-Menü**
- [ ] **Import** - Daten aus CSV/Excel importieren
  - Zeiterfassungen importieren
  - Worker-Daten importieren
  - Kapazitäten importieren
  - Format-Validierung
  - Duplikat-Erkennung
  
- [ ] **Sichern** - Projekt speichern
  - Aktuellen Zustand speichern
  - Backup erstellen

  
- [ ] **Export** - Daten exportieren
  - Vollständiger Datenexport
  - Selektiver Export (nach Zeitraum/Worker)
  - Format-Optionen (CSV, Excel, JSON)
  
- [ ] **Beenden** - Anwendung schließen
  - Unsaved Changes Dialog
  - Cleanup-Routine
  - Graceful Shutdown

#### **Einstellungen-Menü** ⚙️
- [ ] **Anwendungseinstellungen
  - [ ] Auswahl Einzel-Worker oder Mehrfach-Worker (Default: Einzelworker)
  - [ ] Umschaltung zwischen Dark- und Ligh-Mode
  - [ ] Autosave Einstellung (Default: 5min)
- [ ] **Profil (Ausgewählter Worker)** (Dialog)
  - [ ] Worker-Auswahl Dropdown (bei Mehrfach-Worker)
  - [ ] **Regelarbeitsstunden/Tag** (Eingabefeld, Default: 8h)
  - [ ] **Jahresurlaub** (Tage pro Jahr, Default: 30)
  - [ ] **Übertrag Vorjahr** (Resturlaub aus Vorjahr)
  - [ ] **Status** (Default: aktiv)
  - [ ] **Name** (Eingabefeld)
  - [ ] **Emailadresse** (Eingabefeld)
  - [ ] **Team** (Eingabefeld)
  - [ ] Profil speichern & laden
  - [ ] Mehrere Profile verwalten
  - [ ] Die Anwendung muss sich entsprechend verhalten bei Einzel- oder Mehrfachworker (Diagramme, usw)

#### **Hilfe-Menü** ❓
- [ ] **Bedienungshilfe**
  - Anwendungs-Tutorial
  - Feature-Übersicht
  - Tastatur-Shortcuts
  - FAQ-Sektion
  - Über-Dialog (Version, Autor, Lizenz)

**Aufwand:** ~8-10 Stunden  
**Technische Hinweise:**
```python
# Menü-Struktur erweitern in main_window.py
def _setup_menu(self):
    # Datei-Menü
    file_menu = menubar.addMenu("&Datei")
    file_menu.addAction("&Import", self._on_import)
    file_menu.addAction("&Sichern", self._on_save)
    file_menu.addAction("&Export", self._on_export)
    file_menu.addSeparator()
    file_menu.addAction("&Beenden", self.close)
    
    # Einstellungen-Menü
    settings_menu = menubar.addMenu("&Einstellungen")
    settings_menu.addAction("&Profil", self._show_profile_dialog)
    
    # Hilfe-Menü
    help_menu = menubar.addMenu("&Hilfe")
    help_menu.addAction("&Bedienungshilfe", self._show_help)
```

---

## 🎯 Priorität: MITTEL

### 2. ~~**PDF-Export aus WorkerDetailDialog**~~ 📄 ✅ **ABGESCHLOSSEN (v0.4.0)**

- [x] PDF-Export Button hinzufügen
- [x] ReportLab Integration
- [x] PDF-Layout erstellen:
  - Worker-Header (Name, Team, Email)
  - Statistiken (30-Tage, 90-Tage)
  - Chart als Bild einbetten
  - Time Entries Tabelle
  - Capacities Tabelle
- [x] Dateiname-Generierung: `{worker_name}_{datum}.pdf`
- [x] Speichern-Dialog mit Vorschau

**Status:** ✅ Implementiert am 07.10.2025  
**Version:** v0.4.0  
**Aufwand:** ~4 Stunden  
**Tests:** 88 Tests passing (34% Coverage)  
**Dokumentation:** `docs/pdf-export-implementation.md`

---

### 3. ~~**Suche in Tabellen**~~ 🔍 ✅ **TEILWEISE ABGESCHLOSSEN (v0.6.0)**

- [x] Such-Widget über jeder Tabelle (Komponente erstellt)
- [x] Live-Suche (während Tippen)
- [x] Suche in mehreren Spalten
- [x] Anzahl Treffer anzeigen (mit Farb-Coding)
- [x] Clear-Button (integriert in QLineEdit)
- [ ] Treffer-Highlighting (optional)
- [ ] Navigation: Nächster/Vorheriger Treffer (optional)

**Betroffene Widgets:**
- [x] AnalyticsWidget (Team-Übersicht) - **ABGESCHLOSSEN**
- [ ] TimeEntryWidget (Zeitbuchungen-Liste) - **OFFEN**
- [ ] WorkerWidget (Worker-Liste) - **OFFEN**
- [ ] CapacityWidget (Kapazitäts-Liste) - **OFFEN**

**Status:** 🔄 25% abgeschlossen (1 von 4 Widgets integriert)  
**Version:** v0.6.0  
**Aufwand bisher:** ~3 Stunden  
**Restaufwand:** ~1.5 Stunden (3 Widget-Integrationen)  
**Tests:** 124 Tests passing (37% Coverage, TableSearchWidget: 98%)  
**Dokumentation:** `docs/table-search-concept.md`  
**Komponente:** `src/views/table_search_widget.py` (wiederverwendbar)

---

### 4. ~~**Erweiterte Datums-Filter**~~ 📅 ✅ **ABGESCHLOSSEN (v0.5.0)**

- [x] Vordefinierte Zeiträume:
  - [x] Heute
  - [x] Diese Woche
  - [x] Dieser Monat
  - [x] Dieses Quartal
  - [x] Dieses Jahr
  - [x] Letzte 7 Tage
  - [x] Letzte 30 Tage
  - [x] Letzte 90 Tage
- [x] Quick-Select Buttons
- [x] Automatische Synchronisation mit Date-Edit Feldern
- [x] Exclusive Button Group (nur ein Preset aktiv)
- [ ] Kalender-Ansicht (optional, bereits via QDateEdit)

**Betroffene Widgets:**
- [x] AnalyticsWidget (vollständig integriert)
- [ ] CapacityWidget (zukünftige Integration)
- [ ] Alle Report-Funktionen (zukünftig)

**Status:** ✅ Implementiert am 07.10.2025  
**Version:** v0.5.0  
**Aufwand:** ~3 Stunden  
**Tests:** 103 Tests passing (36% Coverage, DateRangeWidget: 100%)  
**Dokumentation:** `docs/date-filter-concept.md`  
**Komponente:** `src/views/date_range_widget.py` (wiederverwendbar)

---

## 🎯 Priorität: NIEDRIG

### 5. **Trend-Analyse über Zeit** 📈

- [ ] Neuer Tab: "Trends"
- [ ] Linien-Diagramm für Auslastung über Zeit
- [ ] Vergleich mehrerer Worker
- [ ] Trendlinien (Linear Regression)
- [ ] Prognose (nächste 30 Tage)
- [ ] Export als Bild/PDF

**Aufwand:** ~6-8 Stunden  
**Dependencies:** Verwendet bereits installiertes matplotlib  
**Technische Hinweise:**
```python
# Neues Widget: TrendAnalysisWidget
class TrendAnalysisWidget(QWidget):
    def __init__(self, analytics_service, worker_repository):
        # Zeitreihen-Daten laden
        # Matplotlib Line Chart erstellen
        # Trendlinie berechnen
        pass
```

---

### 6. **Notifications bei kritischer Auslastung** 🔔

- [ ] Notification-System implementieren
- [ ] Schwellwerte konfigurierbar:
  - Unterauslastung < X%
  - Überauslastung > Y%
  - Keine Zeiterfassung seit X Tagen
- [ ] Toast-Notifications (Desktop)
- [ ] Status-Bar Warnung
- [ ] E-Mail Benachrichtigungen (optional)
- [ ] Notification-Verlauf

**Aufwand:** ~4-5 Stunden  
**Dependencies:** 
- Qt Notifications (QSystemTrayIcon)
- Optional: Email (smtplib)

**Technische Hinweise:**
```python
# NotificationService
class NotificationService:
    def __init__(self):
        self.tray_icon = QSystemTrayIcon()
        self.thresholds = {
            'under': 60,  # < 60% Warnung
            'over': 120   # > 120% Warnung
        }
    
    def check_and_notify(self, utilization_data):
        for worker_id, data in utilization_data.items():
            util = data['utilization_percent']
            if util < self.thresholds['under']:
                self._show_notification(
                    "Unterauslastung",
                    f"Worker {worker_id}: {util:.1f}%"
                )
```

---

## 📋 Implementierungs-Reihenfolge (Empfohlen)

1. 🔜 **Menüleiste erweitern** (HOCH) - Grundfunktionen für Import/Export
2. 🔜 **Einstellungen/Profil** (HOCH) - Worker-Konfiguration
3. ✅ **Erweiterte Datums-Filter** (MITTEL) - v0.5.0 abgeschlossen
4. 🔄 **Suche in Tabellen** (MITTEL) - v0.6.0 teilweise (25%)
5. ✅ **PDF-Export WorkerDetail** (MITTEL) - v0.4.0 abgeschlossen
6. 🔜 **Hilfe/Bedienungshilfe** (HOCH) - Dokumentation
7. 🔜 **Trend-Analyse** (NIEDRIG) - Advanced Feature
8. 🔜 **Notifications** (NIEDRIG) - Optional Feature

**Legende:**
- ✅ = Abgeschlossen
- 🔄 = In Arbeit
- 🔜 = Geplant

---

## 🧪 Test-Strategie

Für jedes neue Feature:
- [ ] Unit-Tests schreiben (min. 80% Coverage)
- [ ] Integration-Tests für UI-Komponenten
- [ ] Manuelle Tests dokumentieren
- [ ] User Acceptance Testing

**Aktueller Stand:**
- ✅ 124/124 Tests bestehen
- ✅ 37% Coverage (+7% seit Start)
- 🎯 Ziel: 150+ Tests, 45%+ Coverage

**Letzte Updates:**
- v0.4.0 (07.10.2025): PDF Export - 88 Tests, 34% Coverage
- v0.5.0 (07.10.2025): Date Range Filter - 103 Tests, 36% Coverage
- v0.6.0 (07.10.2025): Table Search (partial) - 124 Tests, 37% Coverage

---

## 📊 Geschätzter Gesamt-Aufwand

| Feature | Aufwand | Status | Version |
|---------|---------|--------|---------|
| Menüleiste (komplett) | 8-10h | 🔜 Geplant | - |
| Profil-Einstellungen | 4-5h | 🔜 Geplant | - |
| PDF-Export | 4h | ✅ Abgeschlossen | v0.4.0 |
| Datums-Filter | 3h | ✅ Abgeschlossen | v0.5.0 |
| Suche in Tabellen | 4.5h (3h+1.5h) | 🔄 25% | v0.6.0 |
| Trend-Analyse | 6-8h | 🔜 Geplant | - |
| Notifications | 4-5h | 🔜 Geplant | - |

**Abgeschlossen:** ~10 Stunden  
**In Arbeit:** ~1.5 Stunden verbleibend  
**Verbleibend:** ~21-28 Stunden (ca. 3-4 Arbeitstage)

---

## 🎯 Ziel für nächste Sitzung

**Priorität 1 (Suche abschließen):**
- [ ] TableSearchWidget in TimeEntryWidget integrieren
- [ ] TableSearchWidget in WorkerWidget integrieren
- [ ] TableSearchWidget in CapacityWidget integrieren
- [ ] Tests für alle Integrationen (je ~7 Tests)
- [ ] Dokumentation aktualisieren

**Priorität 2 (Import/Export Basis):**
- [ ] Menüleiste mit Datei-Menü vollständig
- [ ] Import/Export Basis-Funktionalität
- [ ] Format-Validierung

**Optional (wenn Zeit):**
- [ ] Profil-Einstellungen Dialog
- [ ] RegEx-Suche Option

---

## 📝 Notizen

### Dark Mode Implementierung
```python
# Style-Sheets für Dark Mode
DARK_STYLE = """
    QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    QPushButton {
        background-color: #3c3c3c;
        border: 1px solid #555555;
    }
    QTableWidget {
        alternate-background-color: #3c3c3c;
    }
"""

def toggle_dark_mode(enabled):
    if enabled:
        app.setStyleSheet(DARK_STYLE)
    else:
        app.setStyleSheet("")
```

### Profil-Daten Struktur
```python
@dataclass
class WorkerProfile:
    worker_id: int
    daily_hours: float = 8.0  # Regelarbeitsstunden/Tag
    annual_vacation: int = 30  # Jahresurlaub in Tagen
    vacation_carryover: int = 0  # Übertrag Vorjahr
    dark_mode: bool = False
```

---

## ✅ Abgeschlossene Features (zur Referenz)

### Core Funktionalität (bis v0.3.0)
- ✅ Phase 0: Core Services (Crypto, Database, Analytics)
- ✅ Phase 1: TimeEntry UI mit Split View
- ✅ Phase 2: Worker Management mit Verschlüsselung
- ✅ Phase 3: Capacity Planning + Analytics Dashboard
- ✅ Phase 4 Part 1: Charts (matplotlib) + Excel Export
- ✅ Phase 4 Part 2: Worker Detail Dialog + Filters
- ✅ TimeEntry Redesign: Liste + Löschen + Autocomplete

### Neue Features (ab v0.4.0)
- ✅ **v0.4.0** (07.10.2025): PDF Export aus WorkerDetailDialog
  - ReportLab Integration
  - Vollständiger Worker-Report mit Statistiken, Charts, Tabellen
  - 88 Tests passing, 34% Coverage
  - Dokumentation: `docs/pdf-export-implementation.md`

- ✅ **v0.5.0** (07.10.2025): Erweiterte Datums-Filter
  - DateRangeWidget mit 8 Presets (Heute, Woche, Monat, Quartal, Jahr, Letzte 7/30/90 Tage)
  - Integration in AnalyticsWidget
  - 103 Tests passing, 36% Coverage
  - Dokumentation: `docs/date-filter-concept.md`

- 🔄 **v0.6.0** (07.10.2025): Table Search Functionality (25% abgeschlossen)
  - TableSearchWidget Komponente (wiederverwendbar)
  - Live-Suche mit Multi-Column Support
  - Treffer-Anzeige mit Farb-Coding
  - Integration in AnalyticsWidget ✅
  - 124 Tests passing, 37% Coverage
  - Dokumentation: `docs/table-search-concept.md`
  - Verbleibend: TimeEntryWidget, WorkerWidget, CapacityWidget

**Status:** 🎉 **3 neue Features in v0.4.0 - v0.6.0 hinzugefügt!**

---

**Letzte Aktualisierung:** 07.10.2025  
**Nächste Review:** Bei Start der nächsten Sitzung  
**Aktuelle Version:** v0.6.0 (Table Search 25%)  
**Nächstes Milestone:** v0.7.0 (Table Search 100%)

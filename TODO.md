# TODO: Nächste Entwicklungsschritte

**Erstellt:** 06.10.2025  
**Projekt:** Capacity Planner Sonnet  
**Status:** 🔜 Geplant für nächste Sitzung

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
- [ ] **Profil (Ausgewählter Worker)**
  - [ ] Worker-Auswahl Dropdown (bei Mehrfach-Worker)
  - [ ] **Regelarbeitsstunden/Tag** (Eingabefeld, Default: 8h)
  - [ ] **Jahresurlaub** (Tage pro Jahr, Default: 30)
  - [ ] **Übertrag Vorjahr** (Resturlaub aus Vorjahr)
  - [ ] Profil speichern & laden
  - [ ] Mehrere Profile verwalten

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

### 2. **PDF-Export aus WorkerDetailDialog** 📄

- [ ] PDF-Export Button hinzufügen
- [ ] ReportLab oder QPrinter Integration
- [ ] PDF-Layout erstellen:
  - Worker-Header (Name, Team, Email)
  - Statistiken (30-Tage, 90-Tage)
  - Chart als Bild einbetten
  - Time Entries Tabelle
  - Capacities Tabelle
- [ ] Dateiname-Generierung: `{worker_name}_{datum}.pdf`
- [ ] Speichern-Dialog mit Vorschau

**Aufwand:** ~4-5 Stunden  
**Dependencies:** `pip install reportlab` oder Qt's QPrinter  
**Technische Hinweise:**
```python
# In worker_detail_dialog.py
def _export_to_pdf(self):
    """Exportiert Worker-Details als PDF"""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    
    filename = f"{self._worker.name}_{datetime.now().strftime('%Y%m%d')}.pdf"
    # PDF generieren...
```

---

### 3. **Suche in Tabellen** 🔍

- [ ] Such-Widget über jeder Tabelle
- [ ] Live-Suche (während Tippen)
- [ ] Suche in mehreren Spalten
- [ ] Treffer-Highlighting
- [ ] Anzahl Treffer anzeigen
- [ ] Navigation: Nächster/Vorheriger Treffer

**Betroffene Widgets:**
- TimeEntryWidget (Zeitbuchungen-Liste)
- AnalyticsWidget (Team-Übersicht)
- WorkerWidget (Worker-Liste)
- CapacityWidget (Kapazitäts-Liste)

**Aufwand:** ~3-4 Stunden  
**Technische Hinweise:**
```python
# Such-Widget Komponente
class SearchWidget(QWidget):
    def __init__(self):
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Suchen...")
        self.search_input.textChanged.connect(self._on_search)
    
    def _on_search(self, text):
        # Filter Tabelle basierend auf Suchtext
        pass
```

---

### 4. **Erweiterte Datums-Filter** 📅

- [ ] Vordefinierte Zeiträume:
  - [ ] Heute
  - [ ] Diese Woche
  - [ ] Dieser Monat
  - [ ] Dieses Quartal
  - [ ] Dieses Jahr
  - [ ] Letzte 7 Tage
  - [ ] Letzte 30 Tage
  - [ ] Letzte 90 Tage
- [ ] Custom Range Picker
- [ ] Quick-Select Buttons
- [ ] Kalender-Ansicht

**Betroffene Widgets:**
- AnalyticsWidget
- CapacityWidget
- Alle Report-Funktionen

**Aufwand:** ~2-3 Stunden  
**Technische Hinweise:**
```python
# DateRangeWidget Komponente
class DateRangeWidget(QWidget):
    date_range_changed = Signal(QDate, QDate)
    
    def __init__(self):
        # Buttons für Presets
        self.today_btn = QPushButton("Heute")
        self.week_btn = QPushButton("Diese Woche")
        self.month_btn = QPushButton("Dieser Monat")
        # ...
```

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

1. ✅ **Menüleiste erweitern** (HOCH) - Grundfunktionen für Import/Export
2. ✅ **Einstellungen/Profil** (HOCH) - Worker-Konfiguration
3. ✅ **Erweiterte Datums-Filter** (MITTEL) - Schnell & nützlich
4. ✅ **Suche in Tabellen** (MITTEL) - UX-Verbesserung
5. ✅ **PDF-Export WorkerDetail** (MITTEL) - Reporting-Feature
6. ✅ **Hilfe/Bedienungshilfe** (HOCH) - Dokumentation
7. 🔜 **Trend-Analyse** (NIEDRIG) - Advanced Feature
8. 🔜 **Notifications** (NIEDRIG) - Optional Feature

---

## 🧪 Test-Strategie

Für jedes neue Feature:
- [ ] Unit-Tests schreiben (min. 80% Coverage)
- [ ] Integration-Tests für UI-Komponenten
- [ ] Manuelle Tests dokumentieren
- [ ] User Acceptance Testing

**Aktueller Stand:**
- ✅ 79/79 Tests bestehen
- ✅ 30% Coverage
- 🎯 Ziel: 80+ Tests, 40%+ Coverage

---

## 📊 Geschätzter Gesamt-Aufwand

| Feature | Aufwand | Priorität |
|---------|---------|-----------|
| Menüleiste (komplett) | 8-10h | HOCH |
| Profil-Einstellungen | 4-5h | HOCH |
| PDF-Export | 4-5h | MITTEL |
| Suche in Tabellen | 3-4h | MITTEL |
| Datums-Filter | 2-3h | MITTEL |
| Trend-Analyse | 6-8h | NIEDRIG |
| Notifications | 4-5h | NIEDRIG |

**Gesamt:** ~31-40 Stunden (ca. 5-7 Arbeitstage)

---

## 🎯 Ziel für nächste Sitzung

**Minimum:**
- ✅ Menüleiste mit Datei-Menü vollständig
- ✅ Profil-Einstellungen Dialog funktionsfähig
- ✅ Import/Export Basis-Funktionalität

**Optional (wenn Zeit):**
- ✅ Erweiterte Datums-Filter
- ✅ Suche in TimeEntry-Tabelle

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

- ✅ Phase 0: Core Services (Crypto, Database, Analytics)
- ✅ Phase 1: TimeEntry UI mit Split View
- ✅ Phase 2: Worker Management mit Verschlüsselung
- ✅ Phase 3: Capacity Planning + Analytics Dashboard
- ✅ Phase 4 Part 1: Charts (matplotlib) + Excel Export
- ✅ Phase 4 Part 2: Worker Detail Dialog + Filters
- ✅ TimeEntry Redesign: Liste + Löschen + Autocomplete

**Status:** 🎉 **Alle Basis-Features implementiert!**

---

**Letzte Aktualisierung:** 06.10.2025  
**Nächste Review:** Bei Start der nächsten Sitzung

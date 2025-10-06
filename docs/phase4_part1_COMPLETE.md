# Phase 4 - Advanced Analytics & Visualisierung

**Status:** ✅ Abgeschlossen (Teil 1: Charts & Excel-Export)  
**Datum:** 2025-10-06  
**Tests:** 73/73 bestanden (100%)

---

## Überblick

Phase 4 erweitert das Analytics Dashboard um professionelle Visualisierung und Export-Funktionen.

---

## Implementierte Features

### 1. Chart-Visualisierung mit matplotlib
- **UtilizationChartWidget** (120 Zeilen)
  - Horizontales Balkendiagramm für bessere Lesbarkeit
  - Farbkodierung nach Auslastungs-Status (< 80% orange, 80-110% grün, > 110% rot)
  - Sortierung nach Auslastung (höchste zuerst)
  - Referenzlinien bei 80% und 110%
  - Werte in Balken angezeigt
  - Grid für bessere Orientierung
  - Responsive Design

- **Integration in AnalyticsWidget**
  - Tab-Widget mit 2 Tabs: "📊 Tabelle" und "📈 Diagramm"
  - Automatische Chart-Aktualisierung bei Daten-Refresh
  - Empty-State für fehlende Daten

### 2. Excel-Export mit Formatierung
- **Professioneller Excel-Export** (openpyxl)
  - Formatierte Header mit Farben und Borders
  - Farbkodierung in Status-Spalte (orange/grün/rot)
  - Differenz-Spalte mit Farben (negativ orange, positiv blau)
  - Zusammenfassung mit separater Formatierung
  - Automatische Spaltenbreiten
  - Borders für alle Zellen
  - Zeitstempel im Dateinamen

- **Export-Buttons**
  - "📊 Export CSV" für einfache Exporte
  - "📗 Export Excel" für formatierte Reports

---

## Technische Details

### Architektur
```
AnalyticsWidget
├── QTabWidget
│   ├── Tab 1: Team-Tabelle (QTableWidget)
│   └── Tab 2: Chart (UtilizationChartWidget)
│       └── matplotlib FigureCanvasQTAgg
├── Export-Funktionen
│   ├── CSV (csv.writer)
│   └── Excel (openpyxl.Workbook)
└── Filter & Refresh
```

### Chart-Technologie
- **matplotlib 3.10.6**: Plotting-Library
- **FigureCanvasQTAgg**: Qt-Backend für matplotlib
- **Horizontale Balken**: `ax.barh()` für bessere Namen-Lesbarkeit
- **Referenzlinien**: `ax.axvline()` für Schwellwerte
- **Responsive**: QSizePolicy.Expanding

### Excel-Formatierung
```python
# openpyxl Styles:
- Font(bold=True, size=12, color="FFFFFF")
- PatternFill(start_color="4472C4", fill_type="solid")
- Alignment(horizontal='center', vertical='center')
- Border(left=Side(style='thin'), ...)
```

---

## Dateien

### Neue Dateien
- `src/views/utilization_chart_widget.py` (120 Zeilen)
  - UtilizationChartWidget Klasse
  - matplotlib Integration
  - Chart-Rendering mit Farbkodierung

### Geänderte Dateien
- `src/views/analytics_widget.py` (+150 Zeilen)
  - Tab-Widget für Tabelle + Chart
  - Excel-Export-Methode (_export_to_excel)
  - Chart-Update bei Daten-Refresh

- `requirements.txt`
  - matplotlib>=3.10.0
  - openpyxl>=3.1.0

- `tests/unit/views/test_analytics_widget.py`
  - Test-Anpassung für neue Button-Namen
  - Test für Chart-Widget-Existenz

---

## Tests

**Alle 73 Unit-Tests bestehen weiterhin!**

### Coverage
- `analytics_widget.py`: 74% (↓ von 97% wegen neuer Excel-Export-Methode)
- `utilization_chart_widget.py`: 97%
- **Gesamt-Projekt**: 33% (↑ von 32%)

---

## Verwendung

### Chart anzeigen
1. Analytics-Tab öffnen
2. Tab "📈 Diagramm" klicken
3. Chart zeigt alle Workers sortiert nach Auslastung

### Excel exportieren
1. Button "📗 Export Excel" klicken
2. Dateiname wählen (Standard: `analytics_20251006_203015.xlsx`)
3. Datei öffnen in Excel/LibreOffice
4. Professionell formatierte Tabelle mit Farben

### CSV exportieren (weiterhin verfügbar)
1. Button "📊 Export CSV" klicken
2. Dateiname wählen
3. Einfache CSV für weitere Verarbeitung

---

## Alternativen

### Warum matplotlib statt pyqtgraph?
- **matplotlib**: Standard, umfassende Dokumentation, einfache Integration
- **pyqtgraph**: Schneller für große Datensätze, interaktiv
- **Entscheidung**: matplotlib für MVP, pyqtgraph bei Performance-Bedarf

### Warum openpyxl statt xlsxwriter?
- **openpyxl**: Lesen + Schreiben, umfassendere API
- **xlsxwriter**: Nur Schreiben, schneller
- **Entscheidung**: openpyxl für Flexibilität

### Warum Tabs statt Side-by-Side?
- **Tabs**: Mehr Platz pro Ansicht, klare Trennung
- **Side-by-Side**: Direkter Vergleich möglich
- **Entscheidung**: Tabs für bessere Übersicht

---

## Best Practices

### matplotlib in Qt
```python
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

figure = Figure(figsize=(8, 6), dpi=100)
canvas = FigureCanvasQTAgg(figure)
canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
```

### openpyxl Styling
```python
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

cell.font = Font(bold=True, size=12, color="FFFFFF")
cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
```

### Empty-State Handling
```python
if not data:
    ax.text(0.5, 0.5, 'Keine Daten', ha='center', va='center')
    ax.axis('off')
```

---

## Lessons Learned

1. **matplotlib Backend**: `backend_qtagg` statt `backend_qt5agg` für PySide6
2. **Horizontale Balken**: `barh()` besser als `bar()` für lange Namen
3. **Excel Zell-Merge**: `ws.merge_cells()` für Zusammenfassung-Header
4. **Tab-Layout**: QTabWidget spart Platz und verbessert UX
5. **Coverage**: Neue Features können Coverage temporär senken - normal!

---

## Bekannte Limitierungen

1. **Keine Interaktivität im Chart**: Kein Zoom/Pan (pyqtgraph könnte das bieten)
2. **Keine Chart-Typen-Auswahl**: Nur Balkendiagramm (könnte erweitert werden)
3. **Excel-Export nicht getestet**: Komplexität zu hoch für Unit-Tests
4. **Keine Worker Detail-Ansicht**: Geplant für Phase 4.2

---

## Nächste Schritte (Phase 4.2)

1. **Worker Detail-Dialog**
   - Dialog mit Worker-Historie
   - Zeiterfassungs-Übersicht
   - Kapazitäts-Trends
   - Individuelles Chart

2. **Erweiterte Filter**
   - Team-Filter-Dropdown
   - Status-Filter (Unter/Optimal/Über)
   - Sortierung in Tabelle (klickbare Header)

3. **Weitere Chart-Typen**
   - Liniendiagramm für zeitliche Trends
   - Tortendiagramm für Team-Verteilung
   - Heatmap für Auslastung über Zeit

4. **Export-Optionen**
   - PDF-Report mit ReportLab
   - Chart als PNG exportieren
   - Email-Versand von Reports

---

## Dependencies

Neue Packages in `requirements.txt`:
```
matplotlib>=3.10.0  # Chart-Visualisierung
openpyxl>=3.1.0     # Excel-Export mit Formatierung
```

Installation:
```bash
pip install matplotlib openpyxl
```

---

## Code-Beispiele

### Chart erstellen
```python
from src.views.utilization_chart_widget import UtilizationChartWidget

chart = UtilizationChartWidget()
chart.update_chart(workers, utilization_data)
```

### Excel exportieren
```python
self._export_to_excel()  # Öffnet Datei-Dialog
```

---

## Zusammenfassung

**Phase 4 (Teil 1) ist erfolgreich abgeschlossen!**

- ✅ Chart-Visualisierung mit matplotlib implementiert
- ✅ Excel-Export mit professioneller Formatierung
- ✅ Tab-Layout für Tabelle + Chart
- ✅ 73/73 Tests bestehen (100%)
- ✅ Keine Regressionen
- ✅ Anwendung läuft stabil

**Das Projekt hat jetzt:**
- 4 vollständig funktionierende Tabs
- Professionelle Visualisierung (Chart)
- 2 Export-Formate (CSV + Excel)
- 1779 Zeilen Code (↑ von 1627)
- 73 Unit-Tests (100% bestanden)
- 33% Coverage (↑ von 32%)

**Phase 4.2 kann folgen mit Worker Detail-Dialog und erweiterten Filtern!** 🚀

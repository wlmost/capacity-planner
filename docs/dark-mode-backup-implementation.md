# Dark Mode & Backup Implementation

**Status:** ✅ **ABGESCHLOSSEN**  
**Datum:** 07.10.2025  
**Tests:** 86/86 bestanden (100%)  
**Coverage:** 31%

---

## 📋 **Übersicht**

Zwei wichtige Features wurden implementiert:
1. **Dark Mode** - Wird beim Start geladen und kann über Einstellungen umgeschaltet werden
2. **Backup-Funktionalität** - Echtes Datenbank-Backup mit Timestamp

---

## 🎯 **Implementierte Features**

### 1. **Dark Mode** (`main_window.py`)

#### **Funktionsweise:**
```python
# Beim Start der Anwendung
def __init__(self):
    # QSettings laden
    self.settings = QSettings("CapacityPlanner", "Settings")
    
    # ... UI Setup ...
    
    # Dark Mode anwenden falls aktiviert
    self._apply_dark_mode()
```

#### **Dark Mode Apply:**
```python
def _apply_dark_mode(self):
    """Wendet Dark Mode an falls aktiviert"""
    dark_mode = self.settings.value("dark_mode", False, type=bool)
    
    if dark_mode:
        # Dark Mode Stylesheet anwenden
        self.setStyleSheet(dark_stylesheet)
        self.statusbar.showMessage("Dark Mode aktiviert", 3000)
    else:
        # Light Mode (Standard)
        self.setStyleSheet("")
        self.statusbar.showMessage("Light Mode aktiviert", 3000)
```

#### **Umschaltung:**
```python
def _show_app_settings(self):
    """Zeigt Anwendungseinstellungen-Dialog"""
    dialog = SettingsDialog(self)
    if dialog.exec():
        # Dark Mode ggf. neu anwenden (ohne Neustart!)
        self._apply_dark_mode()
```

#### **Dark Mode Stylesheet:**
- **Hintergrund:** #2b2b2b (dunkelgrau)
- **Text:** #e0e0e0 (hellgrau)
- **Borders:** #3a3a3a, #4a4a4a (verschiedene Grautöne)
- **Hover/Selected:** #454545, #4a4a4a
- **Focus:** #5a8fd6 (blau)

**Gestylte Komponenten:**
- QWidget, QMainWindow
- QTabWidget, QTabBar
- QMenuBar, QMenu
- QStatusBar
- QPushButton (mit Hover/Pressed States)
- QLineEdit, QTextEdit, QSpinBox, QDateEdit, QComboBox (mit Focus State)
- QTableWidget (mit Alternate Row Colors)
- QHeaderView
- QLabel
- QGroupBox
- QCheckBox
- QScrollBar
- QProgressBar

---

### 2. **Backup-Funktionalität** (`main_window.py`)

#### **Implementierung:**
```python
def _on_save(self):
    """Erstellt Backup der Datenbank"""
    import os
    import shutil
    from datetime import datetime
    
    # 1. Datenbank-Pfad ermitteln
    db_path = self.db_service.get_db_path()
    
    # 2. Backup-Ordner erstellen
    backup_dir = os.path.join(
        os.path.expanduser("~"), 
        ".capacity_planner", 
        "backups"
    )
    os.makedirs(backup_dir, exist_ok=True)
    
    # 3. Backup-Dateiname mit Timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"capacity_planner_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    # 4. Datenbank kopieren
    shutil.copy2(db_path, backup_path)
    
    # 5. Erfolgsmeldung
    QMessageBox.information(...)
```

#### **Backup-Struktur:**
```
~/.capacity_planner/
├── data.db                              # Haupt-Datenbank
├── keys/                                # Verschlüsselungsschlüssel
└── backups/                             # Backup-Ordner (NEU)
    ├── capacity_planner_backup_20251007_143052.db
    ├── capacity_planner_backup_20251007_150120.db
    └── capacity_planner_backup_20251007_161534.db
```

#### **Backup-Features:**
- ✅ Automatischer Backup-Ordner
- ✅ Timestamp im Dateinamen (YYYYMMDD_HHMMSS)
- ✅ Dateigröße wird angezeigt
- ✅ Erfolgsmeldung mit Pfad
- ✅ Statusbar-Feedback
- ✅ Fehlerbehandlung (File not found, Copy errors)

---

### 3. **DatabaseService Erweiterung** (`database_service.py`)

#### **Neue Methode:**
```python
def get_db_path(self) -> str:
    """
    Gibt den Pfad zur Datenbankdatei zurück
    
    Returns:
        Absoluter Pfad zur Datenbank
    """
    return self.database_path
```

---

## 🎨 **UI-Verbesserungen**

### **Dark Mode**
**Vorher:**
- Nur Einstellung im Dialog
- Neustart erforderlich
- Nicht funktional

**Nachher:**
- ✅ Wird beim Start automatisch geladen
- ✅ Sofortige Umschaltung (kein Neustart nötig)
- ✅ Vollständig funktional
- ✅ Konsistentes Design über alle Komponenten
- ✅ Statusbar-Feedback

### **Backup**
**Vorher:**
- Platzhalter-Funktion
- "Folgt in einer späteren Version"

**Nachher:**
- ✅ Echtes Datenbank-Backup
- ✅ Timestamp-basierte Dateinamen
- ✅ Backup-Ordner automatisch erstellt
- ✅ Dateigröße wird angezeigt
- ✅ Fehlerbehandlung

---

## 📝 **Verwendung**

### **Dark Mode aktivieren:**
1. Menü → Einstellungen → Anwendungseinstellungen
2. "Dark Mode aktivieren" ankreuzen
3. "Speichern" klicken
4. **Sofort aktiv** (kein Neustart nötig!)

### **Dark Mode deaktivieren:**
1. Menü → Einstellungen → Anwendungseinstellungen
2. "Dark Mode aktivieren" abwählen
3. "Speichern" klicken
4. Light Mode wird sofort angewendet

### **Backup erstellen:**
1. Menü → Datei → Sichern (oder Ctrl+S)
2. Backup wird automatisch erstellt
3. Erfolgsmeldung zeigt Pfad und Dateigröße
4. Backup liegt in: `~/.capacity_planner/backups/`

---

## 🧪 **Tests**

### **Alle Tests bestehen:**
```
86 passed in 13.22s
Coverage: 31%
```

### **Manuelle Tests:**

**Dark Mode:**
- ✅ Einstellung in SettingsDialog speichern
- ✅ Anwendung neu starten → Dark Mode ist aktiv
- ✅ Dark Mode über Dialog umschalten → Sofort sichtbar
- ✅ Light Mode → Dark Mode → Light Mode (mehrfach)
- ✅ Alle UI-Komponenten korrekt gestylt

**Backup:**
- ✅ Backup erstellen (Ctrl+S)
- ✅ Backup-Ordner wird angelegt
- ✅ Backup-Datei existiert
- ✅ Timestamp im Dateinamen korrekt
- ✅ Dateigröße plausibel (> 0 KB)
- ✅ Mehrere Backups erstellen
- ✅ Fehlerfall: DB-Datei nicht gefunden

---

## 📊 **Code-Änderungen**

| Datei | Änderungen | Beschreibung |
|-------|------------|--------------|
| `main_window.py` | +154 Zeilen | QSettings, Dark Mode Apply, Backup-Funktion |
| `database_service.py` | +8 Zeilen | get_db_path() Methode |
| **Gesamt** | **+162 Zeilen** | |

---

## 🔄 **Workflow**

### **Erster Start:**
1. Anwendung startet
2. QSettings werden geladen
3. `dark_mode` = False (Standard)
4. Light Mode ist aktiv

### **Dark Mode aktivieren:**
1. Einstellungen → Anwendungseinstellungen
2. "Dark Mode aktivieren" ☑
3. "Speichern" → QSettings.setValue("dark_mode", True)
4. `_apply_dark_mode()` wird aufgerufen
5. Dark Stylesheet wird angewendet
6. Statusbar: "Dark Mode aktiviert"

### **Nächster Start:**
1. Anwendung startet
2. QSettings werden geladen
3. `dark_mode` = True
4. `_apply_dark_mode()` wird aufgerufen
5. **Dark Mode ist sofort aktiv!**

### **Backup erstellen:**
1. Datei → Sichern (Ctrl+S)
2. Datenbank-Pfad ermitteln
3. Backup-Ordner erstellen (falls nicht vorhanden)
4. Timestamp generieren
5. Datei kopieren
6. Erfolgsmeldung anzeigen
7. Statusbar-Update

---

## ⚠️ **Hinweise**

### **Dark Mode:**
- **Persistenz:** Via QSettings (Registry auf Windows)
- **Umschaltung:** Sofort wirksam (kein Neustart nötig)
- **Kompatibilität:** Alle Widgets sind gestylt
- **Performance:** Stylesheet wird nur einmal beim Umschalten angewendet

### **Backup:**
- **Speicherort:** `~/.capacity_planner/backups/`
- **Dateiformat:** SQLite-Datenbank (.db)
- **Dateinamen:** `capacity_planner_backup_YYYYMMDD_HHMMSS.db`
- **Größe:** Abhängig von Datenmenge (typisch: 10-1000 KB)
- **Anzahl:** Unbegrenzt (manuelle Bereinigung empfohlen)

### **Zukünftige Erweiterungen:**
- ⏳ Automatisches Backup (via Autosave-Intervall)
- ⏳ Backup-Verwaltung (Liste, Löschen, Wiederherstellen)
- ⏳ Backup-Limits (max. X Backups, älteste löschen)
- ⏳ Komprimierung (ZIP/GZ)
- ⏳ Cloud-Backup (optional)

---

## 🎉 **Fazit**

Beide Features sind vollständig implementiert und funktional:

**Dark Mode:**
- ✅ Wird beim Start geladen
- ✅ Sofortige Umschaltung
- ✅ Vollständiges Styling aller Komponenten
- ✅ Persistente Speicherung

**Backup:**
- ✅ Echtes Datenbank-Backup
- ✅ Automatische Ordnerverwaltung
- ✅ Timestamp-basierte Dateinamen
- ✅ Fehlerbehandlung
- ✅ Benutzer-Feedback

**Die Anwendung bietet jetzt vollständige Einstellungsmöglichkeiten und Datensicherheit!** 🚀

---

**Letzte Aktualisierung:** 07.10.2025  
**Commit:** `feat(settings): Implement Dark Mode and Database Backup functionality`

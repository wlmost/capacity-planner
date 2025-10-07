# Build-Anleitung für Capacity Planner

Diese Anleitung beschreibt, wie du eine standalone `.exe` Datei für Windows erstellst.

## Voraussetzungen

- **Python 3.12+** installiert
- Alle Dependencies aus `requirements.txt` installiert
- **PyInstaller** installiert (`pip install pyinstaller`)
- **Windows** Betriebssystem (für .exe Build)

## Quick Start

### 1. Kompletter Build (Empfohlen)

```powershell
# Build + Package in einem Schritt
.\build.ps1
.\package.ps1
```

Das erstellt:
- `dist\CapacityPlanner.exe` (241 MB) - Standalone Executable
- `dist\CapacityPlanner-v0.7.0-YYYY-MM-DD.zip` (229 MB) - Distribution Package

### 2. Manueller Build

Falls du den Build-Prozess manuell steuern möchtest:

```powershell
# Alte Build-Artefakte löschen
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

# PyInstaller Build
python -m PyInstaller --clean capacity-planner.spec

# Ergebnis prüfen
.\dist\CapacityPlanner.exe
```

## Build-Konfiguration

Die Datei `capacity-planner.spec` enthält die Build-Konfiguration:

### Entry Point
```python
a = Analysis(
    ['src/main.py'],  # Haupt-Python-Datei
    ...
)
```

### Hidden Imports
Alle Python-Module, die dynamisch importiert werden:
```python
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtWidgets',
    'PySide6.QtGui',
    'PySide6.QtCharts',
    'pycryptodome',
    'Crypto.Cipher.AES',
    ...
]
```

### Ausgeschlossene Module
Module, die nicht benötigt werden (reduziert Dateigröße):
```python
excludes=[
    'matplotlib',  # Nicht mehr benötigt (QtCharts)
    'numpy',
    'tkinter',
    'test',
    'pytest',
]
```

### Executable-Optionen
```python
exe = EXE(
    ...
    name='CapacityPlanner',
    console=False,  # Keine CMD-Console im Hintergrund
    upx=True,       # UPX-Kompression aktiviert
    icon=None,      # Hier kannst du ein .ico angeben
)
```

## Build-Modi

### One-File Mode (Standard)
Alles wird in eine einzige `.exe` gepackt:
- ✅ Einfache Distribution (1 Datei)
- ✅ Keine zusätzlichen DLLs
- ⚠️ Größere Dateigröße (~241 MB)
- ⚠️ Langsamerer Start (Entpacken ins Temp)

### One-Folder Mode (Optional)
Executable + DLLs in einem Ordner:
```python
# In capacity-planner.spec ändern:
exe = EXE(
    pyz,
    a.scripts,
    [],  # a.binaries NICHT hier
    exclude_binaries=True,  # HINZUFÜGEN
    ...
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name='CapacityPlanner',
)
```

Vorteile:
- ✅ Schnellerer Start
- ✅ Updates einfacher (nur EXE ersetzen)
- ⚠️ Viele Dateien zum Verteilen

## Icon hinzufügen

1. **Icon erstellen/konvertieren**:
   ```powershell
   # PNG zu ICO konvertieren (z.B. mit https://convertio.co/png-ico/)
   # Oder Icon von https://www.flaticon.com/ herunterladen
   ```

2. **Icon-Datei im Projekt ablegen**:
   ```
   capacity-planner-sonnet/
   ├── icon.ico
   └── capacity-planner.spec
   ```

3. **Spec-Datei aktualisieren**:
   ```python
   exe = EXE(
       ...
       icon='icon.ico',  # Pfad zum Icon
   )
   ```

## Troubleshooting

### Import-Fehler nach Build
**Problem**: `ModuleNotFoundError` beim Ausführen der .exe

**Lösung**: Hidden Import hinzufügen in `capacity-planner.spec`:
```python
hiddenimports = [
    'fehlendes_modul',
    'fehlendes_modul.submodul',
]
```

### DLL-Fehler
**Problem**: `DLL load failed` oder `could not resolve 'xxx.dll'`

**Lösung**: DLL manuell hinzufügen in `capacity-planner.spec`:
```python
binaries=[
    ('C:/path/to/missing.dll', '.'),
]
```

### Zu große Dateigröße
**Problem**: .exe ist zu groß (>300 MB)

**Lösungen**:
1. **Excludes erweitern**: Unnötige Module ausschließen
2. **UPX aktivieren**: `upx=True` (bereits aktiv)
3. **One-Folder Mode**: Siehe oben

### Antivirus False Positive
**Problem**: Windows Defender blockt die .exe

**Lösung**:
1. **Code-Signing**: Executable digital signieren (kostet $)
2. **SmartScreen**: Bei Microsoft submitten
3. **Temporär**: Ausnahme in Defender hinzufügen

## Dependencies

Die .exe enthält folgende Hauptkomponenten:
- **Python 3.12** Runtime
- **PySide6** (6.9.3) - Qt GUI Framework
- **PySide6_Addons** - QtCharts
- **pycryptodome** - AES Verschlüsselung
- **SQLite** - Datenbank

Gesamtgröße: ~241 MB (unkomprimiert)

## Performance-Optimierung

### Build-Zeit reduzieren
```powershell
# Inkrementeller Build (kein --clean)
python -m PyInstaller capacity-planner.spec
```

### Startup-Zeit optimieren
- One-Folder Mode verwenden (siehe oben)
- Lazy Imports im Code: `import module` erst wenn benötigt

## Automatisierung

### GitHub Actions Build (Optional)
```yaml
# .github/workflows/build.yml
name: Build Executable
on: [push]
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pip install pyinstaller
      - run: python -m PyInstaller capacity-planner.spec
      - uses: actions/upload-artifact@v3
        with:
          name: CapacityPlanner
          path: dist/CapacityPlanner.exe
```

## Distribution

Nach dem Build:
1. **Teste die .exe** gründlich
2. **Erstelle ZIP**: `.\package.ps1`
3. **Upload**: GitHub Releases, Firmen-Server, etc.
4. **Dokumentiere**: Version, Changelog, bekannte Issues

## Version Bump

Vor jedem Release:
1. **TODO.md** aktualisieren (Version + Features)
2. **DISTRIBUTION_README.md** Version aktualisieren
3. **Build erstellen**: `.\build.ps1`
4. **Package erstellen**: `.\package.ps1`
5. **Git Tag**: `git tag v0.7.0 && git push --tags`

## Support

Bei Fragen oder Problemen:
- PyInstaller Docs: https://pyinstaller.org/
- PySide6 Docs: https://doc.qt.io/qtforpython/
- GitHub Issues: https://github.com/wlmost/capacity-planner/issues

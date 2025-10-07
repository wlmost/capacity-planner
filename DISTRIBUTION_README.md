# Capacity Planner - Portable Version

## Installation

**Keine Installation erforderlich!**

Die `CapacityPlanner.exe` ist eine standalone Anwendung, die ohne Python-Installation läuft.

### Erste Schritte

1. **Kopiere** die Datei `CapacityPlanner.exe` auf deinen Rechner
2. **Doppelklick** auf die .exe - fertig!
3. Beim ersten Start wird automatisch:
   - Eine Datenbank erstellt (`~/.capacity_planner/capacity_planner.db`)
   - Verschlüsselungs-Keys generiert (`~/.capacity_planner/keys/`)

## System-Anforderungen

- **Betriebssystem**: Windows 10/11 (64-bit)
- **RAM**: Mindestens 4 GB
- **Festplatte**: ~200 MB freier Speicher
- **Keine** Python-Installation erforderlich
- **Keine** Administrator-Rechte erforderlich

## Datenbank-Speicherort

Die Anwendung speichert alle Daten in:
```
C:\Users\<Benutzername>\.capacity_planner\
├── capacity_planner.db      # SQLite Datenbank
├── keys\
│   ├── secret.key          # Verschlüsselungs-Key
│   └── salt.key            # Salt für Key-Ableitung
└── session.json            # Login-Session (optional)
```

## Backup & Migration

### Daten sichern
Kopiere den gesamten Ordner `.capacity_planner` aus deinem Benutzerverzeichnis.

### Auf anderen Rechner übertragen
1. Installiere `CapacityPlanner.exe` auf Zielrechner
2. Kopiere den `.capacity_planner`-Ordner nach `C:\Users\<Benutzername>\`
3. Starte die Anwendung - alle Daten sind verfügbar

## Features

✅ **Worker-Verwaltung** - Stammdaten mit Soll-Stunden  
✅ **Zeiterfassung** - Arbeitszeiten pro Projekt und Tag  
✅ **Projekt-Management** - Projekte mit Beschreibung  
✅ **Analytics** - Auslastungs-Übersicht mit Charts (QtCharts)  
✅ **Dark Mode** - Automatische Theme-Anpassung  
✅ **Single-Worker-Mode** - Login für einzelne Mitarbeiter  
✅ **Admin-Mode** - Übersicht aller Mitarbeiter  
✅ **Datenverschlüsselung** - AES-256 für sensible Daten  
✅ **Export** - CSV-Export für alle Tabellen  

## Troubleshooting

### Anwendung startet nicht
- Prüfe, ob Windows Defender die .exe blockiert (Rechtsklick → Eigenschaften → Freigeben)
- Versuche als Administrator auszuführen (Rechtsklick → Als Administrator ausführen)

### Daten gehen verloren
- Die Datenbank ist lokal gespeichert - kein Cloud-Sync!
- Erstelle regelmäßig Backups vom `.capacity_planner`-Ordner

### "DLL nicht gefunden" Fehler
- Installiere Microsoft Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe

## Version

**Version**: 0.7.0  
**Build-Datum**: {{ BUILD_DATE }}  
**Python**: 3.12.2  
**PySide6**: 6.9.3  

## Support

Bei Fragen oder Problemen:
- GitHub: https://github.com/wlmost/capacity-planner
- Issues: https://github.com/wlmost/capacity-planner/issues

## Lizenz

© 2025 - Siehe LICENSE im Repository

# UI-Tests Troubleshooting - Emoji-Problem in PowerShell

## Problem

Tests schlagen fehl mit:
```
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f680' in position 0
```

## Ursache

PowerShell verwendet standardmäßig Windows-1252 Encoding, das Emojis nicht unterstützt.

## Lösung

### Option 1: UTF-8 Encoding in PowerShell aktivieren

```powershell
# Setze Encoding für aktuelle Session
$OutputEncoding = [console]::InputEncoding = [console]::OutputEncoding = New-Object System.Text.UTF8Encoding

# Dann Tests ausführen
.\venv\Scripts\Activate.ps1
python tests\ui_automation\run_ui_tests.py quick
```

### Option 2: Umgebungsvariable setzen

```powershell
# Vor Test-Ausführung
$env:PYTHONIOENCODING = "utf-8"

# Dann Tests ausführen
.\venv\Scripts\Activate.ps1
python tests\ui_automation\run_ui_tests.py quick
```

### Option 3: Mit chcp (Code Page)

```powershell
# UTF-8 Code Page aktivieren
chcp 65001

# Dann Tests ausführen
.\venv\Scripts\Activate.ps1
python tests\ui_automation\run_ui_tests.py quick
```

## Schnelle Test-Ausführung (PowerShell)

```powershell
# Alles in einem Befehl
chcp 65001; .\venv\Scripts\Activate.ps1; python tests\ui_automation\run_ui_tests.py quick
```

## Alternative: CMD verwenden

Falls PowerShell Probleme macht, nutze CMD:

```cmd
REM In CMD
venv\Scripts\activate
python tests\ui_automation\run_ui_tests.py quick
```

## Permanente Lösung

Füge zu deinem PowerShell-Profil hinzu:

```powershell
# PowerShell-Profil bearbeiten
notepad $PROFILE

# Füge hinzu:
$OutputEncoding = [console]::InputEncoding = [console]::OutputEncoding = New-Object System.Text.UTF8Encoding
```

## Test: Funktioniert es jetzt?

```powershell
# 1. Encoding setzen
$env:PYTHONIOENCODING = "utf-8"

# 2. venv aktivieren
.\venv\Scripts\Activate.ps1

# 3. Quick-Test starten
python tests\ui_automation\run_ui_tests.py quick
```

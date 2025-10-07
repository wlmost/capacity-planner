# Build Script für Capacity Planner Executable
# 
# Erstellt eine standalone Windows .exe Datei
#
# Verwendung: .\build.ps1

Write-Host "=== Capacity Planner Build Script ===" -ForegroundColor Cyan
Write-Host ""

# Prüfe PyInstaller
Write-Host "Prüfe PyInstaller..." -ForegroundColor Yellow
$pyinstaller = pip list | Select-String "pyinstaller"
if (-not $pyinstaller) {
    Write-Host "PyInstaller nicht gefunden. Installiere..." -ForegroundColor Red
    pip install pyinstaller
}

# Erstelle dist-Verzeichnis
Write-Host "Bereite Build vor..." -ForegroundColor Yellow
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}

# Build mit PyInstaller
Write-Host ""
Write-Host "Starte Build-Prozess..." -ForegroundColor Green
Write-Host "Dies kann einige Minuten dauern..." -ForegroundColor Gray
Write-Host ""

python -m PyInstaller --clean capacity-planner.spec

# Prüfe Ergebnis
Write-Host ""
if (Test-Path "dist\CapacityPlanner.exe") {
    Write-Host "✅ Build erfolgreich!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable erstellt:" -ForegroundColor Cyan
    Write-Host "  📁 dist\CapacityPlanner.exe" -ForegroundColor White
    Write-Host ""
    
    $size = (Get-Item "dist\CapacityPlanner.exe").Length / 1MB
    Write-Host "  Größe: $([math]::Round($size, 2)) MB" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Du kannst die .exe jetzt auf andere Windows-Rechner kopieren." -ForegroundColor Yellow
    Write-Host "Keine Python-Installation erforderlich!" -ForegroundColor Yellow
} else {
    Write-Host "❌ Build fehlgeschlagen!" -ForegroundColor Red
    Write-Host "Prüfe die Fehlermeldungen oben." -ForegroundColor Red
    exit 1
}

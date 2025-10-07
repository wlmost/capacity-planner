# Package Script für Distribution
#
# Erstellt ein ZIP-Archiv mit der Executable und README

Write-Host "=== Capacity Planner Package Script ===" -ForegroundColor Cyan
Write-Host ""

# Prüfe ob dist existiert
if (-not (Test-Path "dist\CapacityPlanner.exe")) {
    Write-Host "❌ Executable nicht gefunden!" -ForegroundColor Red
    Write-Host "Führe zuerst .\build.ps1 aus." -ForegroundColor Yellow
    exit 1
}

# Version aus TODO.md extrahieren (oder manuell setzen)
$version = "0.7.0"
$date = Get-Date -Format "yyyy-MM-dd"
$packageName = "CapacityPlanner-v$version-$date"

Write-Host "Erstelle Package: $packageName" -ForegroundColor Green
Write-Host ""

# Erstelle Package-Verzeichnis
$packageDir = "dist\$packageName"
if (Test-Path $packageDir) {
    Remove-Item -Recurse -Force $packageDir
}
New-Item -ItemType Directory -Path $packageDir | Out-Null

# Kopiere Executable
Write-Host "Kopiere Executable..." -ForegroundColor Yellow
Copy-Item "dist\CapacityPlanner.exe" -Destination "$packageDir\CapacityPlanner.exe"

# README vorbereiten (ersetze Platzhalter)
Write-Host "Erstelle README..." -ForegroundColor Yellow
$readmeContent = Get-Content "DISTRIBUTION_README.md" -Raw
$readmeContent = $readmeContent -replace '{{ BUILD_DATE }}', $date
$readmeContent | Set-Content "$packageDir\README.md"

# Lizenz kopieren (falls vorhanden)
if (Test-Path "LICENSE") {
    Copy-Item "LICENSE" -Destination "$packageDir\LICENSE"
}

# ZIP erstellen
Write-Host "Erstelle ZIP-Archiv..." -ForegroundColor Yellow
$zipPath = "dist\$packageName.zip"
if (Test-Path $zipPath) {
    Remove-Item -Force $zipPath
}

Compress-Archive -Path "$packageDir\*" -DestinationPath $zipPath -CompressionLevel Optimal

# Aufräumen
Remove-Item -Recurse -Force $packageDir

# Ergebnis
Write-Host ""
Write-Host "✅ Package erfolgreich erstellt!" -ForegroundColor Green
Write-Host ""
Write-Host "📦 Package:" -ForegroundColor Cyan
Write-Host "   $zipPath" -ForegroundColor White
Write-Host ""

$zipSize = (Get-Item $zipPath).Length / 1MB
Write-Host "   Größe: $([math]::Round($zipSize, 2)) MB" -ForegroundColor Gray
Write-Host ""
Write-Host "Inhalt:" -ForegroundColor Cyan
Write-Host "   ✅ CapacityPlanner.exe" -ForegroundColor White
Write-Host "   ✅ README.md" -ForegroundColor White
if (Test-Path "LICENSE") {
    Write-Host "   ✅ LICENSE" -ForegroundColor White
}
Write-Host ""
Write-Host "Das ZIP-Archiv kann jetzt verteilt werden! 🚀" -ForegroundColor Green

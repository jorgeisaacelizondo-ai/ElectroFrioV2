# Script de Resguardo Automatizado para ElectroFrío
# Genera una copia con fecha y hora de todos los archivos de código del proyecto

$fecha = Get-Date -Format "yyyyMMdd_HHmmss"
$directorioRespaldos = Join-Path $PSScriptRoot "backups"
$respaldoActual = Join-Path $directorioRespaldos "backup_$fecha"

# Crear la carpeta principal de backups si no existe
if (!(Test-Path $directorioRespaldos)) {
    New-Item -ItemType Directory -Path $directorioRespaldos | Out-Null
}

# Crear la subcarpeta con la fecha y hora actuales
New-Item -ItemType Directory -Path $respaldoActual | Out-Null

# Lista de archivos clave a respaldar
$archivos = @("index.html", "styles.css", "dashboard.html", "dashboard.js", "firebase.json", "firestore.rules")

$copiados = 0
foreach ($archivo in $archivos) {
    $rutaArchivo = Join-Path $PSScriptRoot $archivo
    if (Test-Path $rutaArchivo) {
        Copy-Item -Path $rutaArchivo -Destination $respaldoActual
        $copiados++
    }
}

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   ElectroFrío - RESGUARDO COMPLETADO        " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Se respaldaron $copiados archivos en:" -ForegroundColor White
Write-Host "$respaldoActual" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan

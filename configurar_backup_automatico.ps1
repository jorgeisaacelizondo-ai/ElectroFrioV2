# Script para Programar el Backup Automático Semanal en Windows (Task Scheduler)
# ElectroFrío Refrigeración

$taskName = "ElectroFrio_Backup_Semanal"
$scriptPath = Join-Path $PSScriptRoot "hacer_backup.bat"
$workingDir = $PSScriptRoot

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host " CONFIGURACIÓN DE BACKUP AUTOMÁTICO SEMANAL     " -ForegroundColor Cyan
Write-Host " ElectroFrío Refrigeración                       " -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si la tarea ya existe y eliminarla para actualizarla
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "→ Actualizando tarea programada existente..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Crear la acción (ejecutar hacer_backup.bat)
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$scriptPath`"" -WorkingDirectory $workingDir

# Crear el disparador semanal (Todos los lunes a las 09:00 AM)
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9:00am

# Configuraciones de ejecución
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Registrar la tarea en Windows
try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Copia de seguridad semanal automática de la base de datos de ElectroFrío" | Out-Null
    Write-Host "✓ ¡Tarea programada creada exitosamente!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Detalles:" -ForegroundColor White
    Write-Host "• Nombre:        $taskName" -ForegroundColor Gray
    Write-Host "• Frecuencia:    Todos los Lunes a las 09:00 AM" -ForegroundColor Gray
    Write-Host "• Destino:       $workingDir\backups\datos_semanales\" -ForegroundColor Gray
    Write-Host "=================================================" -ForegroundColor Cyan
} catch {
    Write-Host "⚠️ Error al registrar la tarea: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Sugerencia: Ejecute este script como Administrador en PowerShell." -ForegroundColor Yellow
}

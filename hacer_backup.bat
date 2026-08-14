@echo off
chcp 65001 > nul
title ElectroFrío - Copia de Seguridad de Base de Datos
echo ===================================================
echo     ELECTROFRIO - GENERADOR DE COPIA DE SEGURIDAD
echo ===================================================
echo.
echo Ejecutando respaldo de datos Firestore...
echo.

node backup_firestore.js

echo.
echo Presione cualquier tecla para cerrar esta ventana...
pause > nul

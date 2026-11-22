@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === Crownhold - Quitar la traduccion al espanol ===
echo Cerra el juego antes de continuar.
pause
python crear_mod_es.py --desinstalar
pause

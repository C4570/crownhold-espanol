@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === Crownhold - Traduccion al espanol ===
echo.
where python >nul 2>nul
if errorlevel 1 (
  echo No se encontro Python. Instalalo desde https://www.python.org/downloads/
  echo y marca la opcion "Add Python to PATH" durante la instalacion.
  pause
  exit /b 1
)
if not exist "..\Crownhold.exe" (
  echo No se encontro Crownhold.exe en la carpeta de arriba.
  echo Esta carpeta tiene que estar DENTRO de la carpeta del juego, por ejemplo:
  echo   C:\Program Files ^(x86^)\Steam\steamapps\common\Crownhold\mod_es
  pause
  exit /b 1
)
python -m pip install --quiet --disable-pip-version-check zstandard
python crear_mod_es.py
if errorlevel 1 (
  echo.
  echo Algo salio mal. Copia el mensaje de arriba y abri un "Issue" en GitHub.
  pause
  exit /b 1
)
echo.
echo Ahora en Steam: clic derecho en Crownhold ^> Propiedades ^> General ^> Opciones de lanzamiento
echo y pega esto:
echo.
echo     --main-pack mod_es/Crownhold_ES.pck
echo.
echo Despues, en el juego, elegi "Espanol" en Ajustes ^> Idioma.
pause

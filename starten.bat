@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
echo Schritt 1/5: Python pruefen
python --version > ausgabe_setup.txt 2>&1
if errorlevel 1 (
  echo Python fehlt. Bitte von python.org installieren, Haken bei "Add python.exe to PATH".
  echo PYTHON FEHLT >> ausgabe_setup.txt
  pause
  exit /b 1
)
echo Schritt 2/5: Projekt einrichten
if not exist .venv python -m venv .venv >> ausgabe_setup.txt 2>&1
.venv\Scripts\python -m pip install -e ".[dev]" >> ausgabe_setup.txt 2>&1
echo Schritt 3/5: Daten fuer Oktober 2026 herunterladen (kann dauern)
.venv\Scripts\python scripts\download.py 2026-10 >> ausgabe_setup.txt 2>&1
echo Schritt 4/5: Auswertung
.venv\Scripts\python scripts\report.py > ausgabe_report.txt 2>&1
echo Schritt 5/5: Tests
.venv\Scripts\python -m pytest > ausgabe_tests.txt 2>&1
echo FERTIG >> ausgabe_setup.txt
echo Fertig. Du kannst das Fenster schliessen.
pause

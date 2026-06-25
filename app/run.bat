@echo off
REM Launch the IRP Tabletop prototype. Windows.
cd /d "%~dp0"
echo Starting the IRP Tabletop prototype... your browser will open shortly.
python -m streamlit run Home.py
pause

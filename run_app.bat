@echo off
:: Pindah otomatis ke direktori tempat script ini berada
cd /d "%~dp0"

echo ===================================================
echo   Menjalankan Server Web CookFit (Flask)
echo   Buka di browser: http://127.0.0.1:5000
echo ===================================================
python app.py
pause

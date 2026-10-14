@echo off
:: Pindah otomatis ke direktori tempat script ini berada
cd /d "%~dp0"

echo ===================================================
echo   Menjalankan Unit Test CookFit (Pertemuan 5)
echo ===================================================
python -m unittest discover -s tests -v
echo.
echo ===================================================
pause

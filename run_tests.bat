@echo off
:: Pindah otomatis ke direktori tempat script ini berada
cd /d "%~dp0"

echo ===================================================
echo   Menjalankan Seluruh Unit Test CookFit (Pertemuan 5 & 6)
echo ===================================================
python -m unittest discover -s tests -v
echo.
echo ===================================================
pause

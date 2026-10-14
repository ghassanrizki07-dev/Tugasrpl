@echo off
cd /d "%~dp0"
echo =========================================
echo CookFit - GitHub Push
echo Repository: https://github.com/ghassanrizki07-dev/Tugasrpl.git
echo =========================================

git add .
git commit -m "chore: sync latest project files and test scripts"
git push origin main

echo =========================================
echo Selesai! Push ke GitHub berhasil.
echo =========================================
pause

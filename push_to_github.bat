@echo off
echo =========================================
echo CookFit - GitHub Repository Setup & Push
echo Repository: https://github.com/ghassanrizki07-dev/Tugasrpl.git
echo =========================================

git init
git remote add origin https://github.com/ghassanrizki07-dev/Tugasrpl.git
git branch -M main
git add .
git commit -m "feat: initial commit for CookFit project architecture & specifications"
git push -u origin main

echo =========================================
echo Success! Push completed.
echo =========================================
pause

@echo off
title Compilation EDUPAIE
color 0A
cd /d %~dp0

echo ============================================
echo    COMPILATION EDUPAIE - PyInstaller
echo ============================================
echo.

:: Vérifier que l'environnement virtuel existe
if not exist ".venv\Scripts\python.exe" (
    echo ERREUR: Environnement virtuel non trouve!
    echo Lance d abord: python -m venv .venv
    pause
    exit /b 1
)

:: Étape 1 — Créer l'icône
echo [1/3] Creation de l icone...
.venv\Scripts\python.exe make_ico.py
if errorlevel 1 (
    echo ATTENTION: Icone non creee, compilation continue sans icone personnalisee
)
echo.

:: Étape 2 — Installer PyInstaller si besoin
echo [2/3] Verification de PyInstaller...
.venv\Scripts\pip.exe show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installation de PyInstaller...
    .venv\Scripts\pip.exe install pyinstaller==6.11.1
)
echo.

:: Étape 3 — Nettoyer les anciens builds
echo [3/3] Nettoyage des anciens builds...
if exist "dist\EduPaie" rmdir /s /q "dist\EduPaie"
if exist "build\EduPaie" rmdir /s /q "build\EduPaie"
echo.

:: Compilation
echo ============================================
echo    Compilation en cours... (patientez)
echo ============================================
.venv\Scripts\pyinstaller.exe EduPaie.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ============================================
    echo    ERREUR lors de la compilation !
    echo ============================================
    pause
    exit /b 1
)

echo.
echo ============================================
echo    COMPILATION REUSSIE !
echo ============================================
echo.
echo L executable se trouve dans :
echo    dist\EduPaie\EduPaie.exe
echo.
echo Pour distribuer : copier tout le dossier dist\EduPaie\
echo.

:: Ouvrir le dossier de sortie
explorer dist\EduPaie

pause

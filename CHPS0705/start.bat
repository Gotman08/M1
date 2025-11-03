@echo off
echo ================================================
echo    Systeme de Report Vocal - Antivan Crows
echo ================================================
echo.

REM Vérifier si l'environnement virtuel existe
if not exist "venv\" (
    echo Creation de l'environnement virtuel...
    python -m venv venv
    echo.
)

REM Activer l'environnement virtuel
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Installer les dépendances si nécessaire
if not exist "venv\Lib\site-packages\whisper\" (
    echo Installation des dependances...
    echo Cela peut prendre plusieurs minutes...
    pip install -r requirements.txt
    echo.
)

REM Vérifier Ollama (optionnel)
echo Verification d'Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo [ATTENTION] Ollama n'est pas disponible.
    echo Le systeme fonctionnera en mode degrade (analyse par mots-cles).
    echo Pour activer l'analyse IA complete :
    echo   1. Installez Ollama depuis https://ollama.ai/
    echo   2. Executez: ollama pull gemma2:2b
    echo   3. Executez: ollama serve
    echo.
)

echo Demarrage du systeme...
echo.
python main.py

pause

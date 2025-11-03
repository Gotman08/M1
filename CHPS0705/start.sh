#!/bin/bash

echo "================================================"
echo "   Systeme de Report Vocal - Antivan Crows"
echo "================================================"
echo ""

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "Creation de l'environnement virtuel..."
    python3 -m venv venv
    echo ""
fi

# Activer l'environnement virtuel
echo "Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances si nécessaire
if [ ! -d "venv/lib/python*/site-packages/whisper" ]; then
    echo "Installation des dependances..."
    echo "Cela peut prendre plusieurs minutes..."
    pip install -r requirements.txt
    echo ""
fi

# Vérifier Ollama (optionnel)
echo "Verification d'Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "[ATTENTION] Ollama n'est pas disponible."
    echo "Le systeme fonctionnera en mode degrade (analyse par mots-cles)."
    echo "Pour activer l'analyse IA complete :"
    echo "  1. Installez Ollama depuis https://ollama.ai/"
    echo "  2. Executez: ollama pull gemma2:2b"
    echo "  3. Executez: ollama serve"
    echo ""
fi

echo "Demarrage du systeme..."
echo ""
python3 main.py

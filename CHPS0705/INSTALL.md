# Guide d'Installation Rapide

## Prérequis Obligatoires

### 1. Python 3.8 ou supérieur

Vérifiez votre version :
```bash
python --version
# ou
python3 --version
```

Si Python n'est pas installé : https://www.python.org/downloads/

### 2. FFmpeg (pour Whisper)

#### Windows
Option 1 - Chocolatey (recommandé) :
```powershell
choco install ffmpeg
```

Option 2 - Manuel :
1. Télécharger depuis https://ffmpeg.org/download.html
2. Extraire dans `C:\ffmpeg`
3. Ajouter `C:\ffmpeg\bin` au PATH

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

#### macOS
```bash
brew install ffmpeg
```

Vérifier l'installation :
```bash
ffmpeg -version
```

## Prérequis Optionnels (mais Recommandés)

### Ollama + Gemma3 (pour l'analyse IA avancée)

#### 1. Installer Ollama
- Windows/Mac : https://ollama.ai/download
- Linux :
  ```bash
  curl -fsSL https://ollama.ai/install.sh | sh
  ```

#### 2. Télécharger le modèle Gemma
```bash
ollama pull gemma2:2b
```

#### 3. Démarrer le serveur Ollama
```bash
ollama serve
```

Laisser ce terminal ouvert pendant l'utilisation du système.

## Installation du Projet

### Méthode Automatique (Recommandé)

#### Windows
Double-cliquez sur `start.bat` ou dans un terminal :
```cmd
start.bat
```

#### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

Le script va automatiquement :
1. Créer un environnement virtuel Python
2. Installer toutes les dépendances
3. Vérifier Ollama
4. Démarrer le jeu

### Méthode Manuelle

#### 1. Créer un environnement virtuel
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

Cette étape peut prendre 5-10 minutes et télécharger environ 1-2 GB de données.

#### 3. Démarrer le système
```bash
python main.py
```

## Vérification de l'Installation

### Test 1 : Python et dépendances
```bash
python -c "import whisper, sounddevice, numpy; print('OK')"
```

Résultat attendu : `OK`

### Test 2 : FFmpeg
```bash
ffmpeg -version
```

Résultat attendu : Affichage de la version de FFmpeg

### Test 3 : Ollama (optionnel)
```bash
curl http://localhost:11434/api/tags
```

Résultat attendu : Liste des modèles installés (dont gemma2:2b)

### Test 4 : Audio
```python
python -c "import sounddevice as sd; print(sd.query_devices())"
```

Résultat attendu : Liste de vos périphériques audio

## Problèmes Courants

### Erreur : "No module named 'whisper'"
```bash
pip install openai-whisper
```

### Erreur : "FFmpeg not found"
- Vérifier que FFmpeg est bien dans le PATH
- Redémarrer le terminal après installation

### Erreur : "Could not find a suitable audio device"
- Vérifier qu'un microphone est branché
- Vérifier les permissions audio (Linux)
- Redémarrer le système

### Erreur : "Connection refused" (Ollama)
- Vérifier qu'Ollama est démarré : `ollama serve`
- Le système continuera à fonctionner sans Ollama (mode dégradé)

### Performances lentes
- Utiliser un modèle Whisper plus petit : `model_size="tiny"` dans main.py
- Fermer les applications gourmandes en ressources
- Sur CPU, la première transcription peut prendre 10-20 secondes

## Configuration Système Minimale

### Recommandée
- CPU : 4 cœurs ou plus
- RAM : 8 GB
- Espace disque : 5 GB libre
- Micro : N'importe quel micro fonctionnel

### Minimale
- CPU : 2 cœurs
- RAM : 4 GB
- Espace disque : 3 GB libre
- Micro : Requis

## Étapes Suivantes

Une fois l'installation terminée :

1. Lire le [README.md](README.md) pour comprendre le système
2. Consulter la section "Les 8 Bugs Intentionnels" pour savoir quoi chercher
3. Lancer le jeu avec `python main.py` ou `start.bat`/`start.sh`
4. S'amuser à trouver les bugs !

## Support

En cas de problème :
1. Vérifier ce guide d'installation
2. Consulter la section "Dépannage" du README.md
3. Vérifier les logs d'erreur affichés
4. Contacter l'équipe Antivan Crows

---

**Temps d'installation total estimé** : 15-30 minutes (selon la vitesse de connexion)

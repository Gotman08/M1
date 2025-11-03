# Système de Report Vocal de Bugs - PoC Beta-Test

## Description

Ce projet est un Proof of Concept (PoC) développé pour l'équipe Antivan Crows dans le cadre du module CHPS0705. Il implémente un système de report vocal de bugs pour des beta-tests de jeux vidéo.

Le système combine :
- Un jeu Puissance 4 avec 8 bugs intentionnels (classés par gravité)
- Un système de reconnaissance vocale utilisant Whisper (OpenAI) en local
- Une analyse intelligente des reports avec Gemma3 via Ollama
- Un dashboard terminal affichant les résultats de la chasse aux bugs

## Contexte du Projet

Dans le cadre des beta-tests de jeux vidéo, les testeurs sont placés dans des box individualisées avec casque-micro. Pour minimiser l'interruption du gameplay, le système de report de bugs se fait exclusivement par commande vocale :

1. Le joueur dit "**bug**" (wake word) pour activer l'enregistrement
2. Il décrit le bug observé pendant 8 secondes
3. Le système transcrit automatiquement avec Whisper
4. Gemma3 analyse le report et identifie le bug parmi ceux connus
5. À la fin, un rapport complet affiche tous les bugs découverts

## Architecture

```
CHPS0705/
├── game/
│   ├── puissance4.py        # Jeu avec bugs intentionnels
│   └── bugs_list.py          # Documentation des bugs
├── voice/
│   ├── voice_detector.py     # Détection du wake word
│   └── voice_transcriber.py  # Transcription Whisper
├── analysis/
│   └── bug_analyzer.py       # Analyse avec Gemma3
├── main.py                    # Point d'entrée
└── requirements.txt
```

## Les 8 Bugs Intentionnels

| ID | Niveau | Gravité | Description |
|----|--------|---------|-------------|
| 1 | 1 | Cosmétique | Symbole joueur en minuscule tous les 7 coups |
| 2 | 2 | Mineur | Message de tour mal formaté tous les 3 coups |
| 3 | 3 | Moyen | Compteur de coups +1 tous les 5 tours |
| 4 | 3 | Moyen | Colonnes numérotées 0-6 au lieu de 1-7 |
| 5 | 4 | Majeur | Détection diagonale descendante incorrecte |
| 6 | 4 | Majeur | Match nul déclaré à 41 pièces au lieu de 42 |
| 7 | 5 | Critique | Crash après 3 tentatives sur colonne pleine |
| 8 | 5 | Critique | Boucle infinie si victoire sur dernière ligne |

## Prérequis

### Logiciels requis

1. **Python 3.8+**
2. **FFmpeg** (pour Whisper)
   - Windows : `choco install ffmpeg` ou télécharger depuis https://ffmpeg.org/
   - Linux : `sudo apt install ffmpeg`
   - macOS : `brew install ffmpeg`

3. **Ollama** (optionnel mais recommandé pour l'analyse IA)
   - Télécharger depuis https://ollama.ai/
   - Installer le modèle Gemma : `ollama pull gemma2:2b`

### Dépendances Python

Voir `requirements.txt` pour la liste complète.

## Installation

### 1. Cloner ou télécharger le projet

```bash
cd c:\Users\nicol\Documents\M1\CHPS0705
```

### 2. Créer un environnement virtuel (recommandé)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

**Note** : L'installation de Whisper peut prendre plusieurs minutes et nécessite environ 1-2 GB d'espace disque pour les modèles.

### 4. Installer et configurer Ollama (optionnel)

```bash
# Après avoir installé Ollama
ollama pull gemma2:2b
ollama serve
```

Le système fonctionnera sans Ollama, mais utilisera uniquement l'analyse par mots-clés (moins précise).

### 5. Tester l'installation

```bash
python test_system.py
```

Ce script vérifie automatiquement :
- Les dépendances Python
- FFmpeg
- Les périphériques audio
- Le modèle Whisper
- Ollama (optionnel)
- Les modules du projet

## Utilisation

### Démarrage du système

```bash
python main.py
```

### Pendant le jeu

1. **Jouer normalement** : Entrez le numéro de colonne (0-6) pour placer un pion
2. **Signaler un bug** : Dites "**bug**" dans votre micro, puis décrivez le problème
3. **Quitter** : Tapez 'q' à tout moment

### Exemples de reports vocaux

- "Bug : le symbole du joueur est affiché en minuscule"
- "Bug : le compteur de tours affiche un nombre incorrect"
- "Bug : le jeu ne détecte pas ma victoire en diagonale"
- "Bug : le jeu a planté quand j'ai essayé plusieurs fois sur la même colonne"

### Rapport final

À la fin de la partie, le système affiche :
- Le nombre total de reports vocaux effectués
- Les bugs découverts vs bugs manqués
- Un score sur 100
- Le détail de chaque bug avec son niveau de gravité

## Configuration

### Modifier le wake word

Dans [main.py](main.py), ligne 18 :
```python
self.voice_detector = VoiceDetector(wake_word="bug")  # Changer ici
```

### Modifier la durée d'enregistrement

Dans [voice/voice_detector.py](voice/voice_detector.py), ligne 20 :
```python
self.recording_duration = 8  # Modifier ici (en secondes)
```

### Changer le modèle Whisper

Dans [main.py](main.py), ligne 19 :
```python
self.transcriber = VoiceTranscriber(model_size="base")  # tiny, base, small, medium, large
```

Options :
- `tiny` : Le plus rapide, moins précis (~75 MB)
- `base` : Bon compromis (recommandé) (~150 MB)
- `small` : Plus précis, plus lent (~500 MB)
- `medium` : Très précis (~1.5 GB)
- `large` : Le plus précis (~3 GB)

## Dépannage

### Whisper ne se charge pas

```bash
# Vérifier FFmpeg
ffmpeg -version

# Réinstaller Whisper
pip uninstall openai-whisper
pip install openai-whisper
```

### Le micro n'est pas détecté

```bash
# Tester la configuration audio
python -c "import sounddevice as sd; print(sd.query_devices())"
```

### Ollama n'est pas disponible

Le système continuera à fonctionner avec l'analyse par mots-clés. Pour activer Ollama :

```bash
# Dans un terminal séparé
ollama serve

# Tester
curl http://localhost:11434/api/tags
```

### Erreurs de permissions audio (Linux)

```bash
sudo usermod -a -G audio $USER
# Redémarrer la session
```

## Tests

### Tester chaque bug individuellement

Pour tester les bugs plus facilement :

1. **Bug #1 (Niveau 1)** : Jouer 7 coups et observer les symboles
2. **Bug #2 (Niveau 2)** : Observer le message tous les 3 tours
3. **Bug #3 (Niveau 3)** : Vérifier le compteur au tour 5, 10, 15...
4. **Bug #4 (Niveau 3)** : Observer la numérotation des colonnes (0-6 au lieu de 1-7)
5. **Bug #5 (Niveau 4)** : Essayer de gagner en diagonale descendante
6. **Bug #6 (Niveau 4)** : Remplir le plateau jusqu'à 41 pièces
7. **Bug #7 (Niveau 5)** : Essayer 3 fois de suite sur une colonne pleine
8. **Bug #8 (Niveau 5)** : Gagner avec un alignement sur la ligne du bas

## Technologies Utilisées

- **Python 3.8+** : Langage principal
- **OpenAI Whisper** : Reconnaissance vocale (STT) en local
- **Ollama + Gemma3** : Analyse intelligente des bugs
- **sounddevice** : Capture audio en temps réel
- **NumPy** : Traitement des données audio
- **Requests** : Communication avec l'API Ollama

## Contributeurs

Équipe **Antivan Crows** :
- Tacko : Backend d'application
- Alban : Report des bugs dans les jeux, fonctionnalité vocale
- Nicolas : Création de jeu vidéo & implémentation
- Antoine : Frontend d'application
- Sylvain : Récupération des bugs par API, communication client

## Roadmap

- [ ] Ajout de nouveaux jeux (échecs, morpion, etc.)
- [ ] Interface graphique (Electron)
- [ ] Enregistrement vidéo avec replay automatique
- [ ] Dashboard web pour visualiser les statistiques
- [ ] Support multi-langues pour la reconnaissance vocale
- [ ] Export des rapports en JSON/CSV pour analyse externe
- [ ] Intégration d'une base de données pour le stockage persistant

## Licence

Ce projet est développé dans un cadre académique pour le module CHPS0705.

## Contact

Pour toute question concernant ce PoC, contactez l'équipe Antivan Crows.

---

**Note** : Ce système est un Proof of Concept destiné à démontrer la faisabilité technique d'un système de report vocal automatisé pour les beta-tests de jeux vidéo. Les bugs sont volontairement intégrés pour les besoins de la démonstration.

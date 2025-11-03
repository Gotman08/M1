# Documentation Technique - Système de Report Vocal

## Vue d'Ensemble

Ce document détaille l'architecture technique et le fonctionnement interne du système de report vocal de bugs pour le PoC Antivan Crows.

## Architecture Globale

```
┌─────────────────────────────────────────────────────────────┐
│                         Main System                          │
│                      (GameReportSystem)                      │
└────────────┬────────────────────────┬────────────────────────┘
             │                        │
             ▼                        ▼
    ┌────────────────┐       ┌────────────────┐
    │   Game Engine  │       │  Voice System  │
    │  (Puissance4)  │       │                │
    └────────┬───────┘       └───────┬────────┘
             │                       │
             │                       ├─► VoiceDetector
             │                       │   (Wake word detection)
             │                       │
             │                       ├─► VoiceTranscriber
             │                       │   (Whisper STT)
             │                       │
             ▼                       ▼
    ┌────────────────────────────────────────┐
    │          BugAnalyzer (Gemma3)          │
    │         + bugs_list (Reference)         │
    └────────────────────────────────────────┘
                      │
                      ▼
              ┌──────────────┐
              │ Final Report │
              └──────────────┘
```

## Composants Détaillés

### 1. Game Engine (game/puissance4.py)

**Responsabilité** : Gérer la logique du jeu Puissance 4 avec bugs intentionnels

**Classe principale** : `Puissance4`

**Méthodes clés** :
- `__init__()` : Initialise le plateau 6x7, joueurs, compteurs
- `display_board()` : Affiche le plateau (contient Bug #4)
- `get_player_symbol(player)` : Retourne 'X' ou 'O' (contient Bug #1)
- `display_turn_message()` : Affiche le tour actuel (contient Bug #2)
- `get_move_count_display()` : Affiche le compteur (contient Bug #3)
- `make_move(col)` : Place un pion (contient Bug #7)
- `check_winner()` : Vérifie victoire (contient Bug #5 et #8)
- `is_board_full()` : Vérifie match nul (contient Bug #6)
- `get_game_context()` : Retourne l'état complet du jeu pour l'analyse

**Bugs implémentés** :

```python
# Bug #1 - Cosmétique (ligne 37)
if self.move_count > 0 and self.move_count % 7 == 0:
    symbol = symbol.lower()

# Bug #2 - Mineur (ligne 124)
if self.move_count % 3 == 0:
    print(f"Tour {n} -Joueur{p}")  # Espaces manquants

# Bug #3 - Moyen (ligne 111)
if self.move_count > 0 and self.move_count % 5 == 0:
    display_count += 1

# Bug #4 - Moyen (ligne 45)
print("  0   1   2   3   4   5   6")  # Devrait être 1-7

# Bug #5 - Majeur (ligne 168)
# Condition incorrecte pour diagonale descendante

# Bug #6 - Majeur (ligne 186)
if count >= 41:  # Devrait être 42
    return True

# Bug #7 - Critique (ligne 66)
if self.column_full_attempts[col] >= 3:
    raise Exception("Crash!")

# Bug #8 - Critique (ligne 144)
if row == 5:
    while True:  # Boucle infinie
        time.sleep(0.1)
```

### 2. Voice Detection System (voice/voice_detector.py)

**Responsabilité** : Écouter en continu et détecter le wake word "bug"

**Classe principale** : `VoiceDetector`

**Paramètres configurables** :
- `wake_word` : Mot de déclenchement (défaut: "bug")
- `sample_rate` : Taux d'échantillonnage audio (défaut: 16000 Hz)
- `recording_duration` : Durée d'enregistrement après détection (défaut: 8s)
- `buffer_size` : Taille du buffer circulaire (défaut: 3s)

**Workflow** :
1. `start_listening()` : Démarre le stream audio avec sounddevice
2. `audio_callback()` : Appelé en continu, remplit le buffer
3. `process_audio_stream()` : Thread qui vérifie le wake word toutes les 2s
4. `check_wake_word()` : Utilise Whisper tiny pour transcription rapide
5. `start_recording()` : Active l'enregistrement complet
6. `stop_recording_after_delay()` : Arrête après 8s et appelle le callback

**Performance** :
- Latence détection : ~2-3 secondes (compromis performance/réactivité)
- Modèle Whisper : "tiny" pour détection (rapide), "base" pour transcription (précis)
- RAM utilisée : ~500 MB (buffers audio + modèle)

### 3. Voice Transcription (voice/voice_transcriber.py)

**Responsabilité** : Convertir l'audio en texte avec Whisper

**Classe principale** : `VoiceTranscriber`

**Modèles Whisper disponibles** :

| Modèle | Taille | RAM | Vitesse | Précision |
|--------|--------|-----|---------|-----------|
| tiny   | 75 MB  | 1 GB | 32x     | ~75%      |
| base   | 150 MB | 1 GB | 16x     | ~85%      |
| small  | 500 MB | 2 GB | 6x      | ~90%      |
| medium | 1.5 GB | 5 GB | 2x      | ~95%      |
| large  | 3 GB   | 10 GB| 1x      | ~98%      |

**Recommandation** : `base` (bon compromis)

**Méthodes** :
- `load_model()` : Charge le modèle Whisper
- `transcribe(audio_data)` : Transcrit et retourne dict avec text, language, segments
- `transcribe_and_print()` : Version avec affichage formaté

**Format de sortie** :
```python
{
    'text': "bug le compteur affiche un mauvais nombre",
    'language': 'fr',
    'segments': [...],
    'error': None
}
```

### 4. Bug Analyzer (analysis/bug_analyzer.py)

**Responsabilité** : Analyser les reports et identifier les bugs

**Classe principale** : `BugAnalyzer`

**Architecture hybride** :
1. Analyse par mots-clés (fallback, toujours actif)
2. Analyse IA avec Gemma3 via Ollama (si disponible)

**Workflow** :

```
Transcription + Game Context
         │
         ▼
   Analyse par mots-clés
   (bugs_list.py)
         │
         ├──► Ollama disponible ? ──No──► Résultat final
         │                                  (mots-clés)
         Yes
         │
         ▼
   Requête à Gemma3
   (Prompt structuré)
         │
         ▼
   Parsing JSON response
         │
         ▼
   Combinaison des analyses
         │
         ▼
   Résultat final
   (IA + mots-clés)
```

**Prompt Gemma3** :
```python
{
    "bug_ids": [3, 4],
    "niveau_gravite": 3,
    "clarte_report": 8,
    "explication": "...",
    "confiance": 0.85
}
```

**Méthodes** :
- `analyze_report(transcription, game_context)` : Analyse principale
- `get_final_report()` : Génère le rapport de fin de partie
- `display_final_report()` : Affiche le dashboard terminal

**Calcul du score** :
```python
score = (nombre_bugs_trouvés / 8) * 100
```

### 5. Bugs List (game/bugs_list.py)

**Responsabilité** : Base de données des bugs pour référence

**Structure** :
```python
BUGS_INTENTIONNELS = [
    {
        "id": 1,
        "niveau": 1,
        "gravite": "Cosmétique",
        "description": "...",
        "condition": "...",
        "location": "fichier.py:fonction()",
        "mots_cles": ["mot1", "mot2", ...]
    },
    ...
]
```

**Fonctions utilitaires** :
- `get_bug_by_keywords(text)` : Recherche par mots-clés
- `get_bug_by_id(bug_id)` : Récupération par ID
- `get_all_bugs()` : Liste complète

## Flow d'Exécution Complet

### Phase 1 : Initialisation

```
1. GameReportSystem.__init__()
   ├─► Puissance4()
   ├─► VoiceDetector(wake_word="bug")
   ├─► VoiceTranscriber(model_size="base")
   └─► BugAnalyzer()

2. setup_voice_system()
   ├─► Vérifier Ollama (optionnel)
   ├─► Charger Whisper base (~150 MB)
   └─► Configurer callback vocal
```

### Phase 2 : Partie en Cours

```
Thread Principal (Jeu)          Thread Audio (Background)
       │                                │
       ▼                                ▼
   play_turn()                    audio_callback()
       │                                │
   display_board()                 buffer audio
       │                                │
   input colonne                   check_wake_word()
       │                            (toutes les 2s)
   make_move()                          │
       │                                │
   check_winner()                   "bug" détecté?
       │                                │
       │                           ┌────Yes
       │                           │
       │◄──────callback─────start_recording()
       │                           │
   continue...                record 8 secondes
                                   │
                              transcribe()
                                   │
                              analyze_report()
                                   │
                              afficher résultat
                                   │
                              continue listening...
```

### Phase 3 : Fin de Partie

```
1. game_over = True
   │
   ▼
2. stop_listening()
   │
   ▼
3. analyzer.display_final_report()
   ├─► Calcul du score
   ├─► Liste bugs trouvés
   ├─► Liste bugs manqués
   └─► Évaluation performance
```

## APIs et Intégrations

### Ollama API

**Endpoint** : `http://localhost:11434`

**Requête** :
```python
POST /api/generate
{
    "model": "gemma2:2b",
    "prompt": "...",
    "stream": false,
    "format": "json"
}
```

**Réponse** :
```python
{
    "response": "{\"bug_ids\": [1], ...}",
    "done": true
}
```

### Whisper (Local)

Pas d'API réseau, traitement local :
```python
model = whisper.load_model("base")
result = model.transcribe(audio, language="fr")
```

## Gestion des Erreurs

### Hiérarchie des exceptions

```
Exception (Python standard)
    │
    ├─► Bug intentionnel niveau 5 (crash)
    │   └─► Capturé par try/except dans main.py
    │
    ├─► Erreur Whisper (modèle non chargé)
    │   └─► Mode dégradé : pas de vocal
    │
    ├─► Erreur Ollama (non disponible)
    │   └─► Fallback : analyse mots-clés
    │
    └─► Erreur Audio (micro non détecté)
        └─► Affichage message d'erreur
```

### Stratégies de fallback

1. **Ollama indisponible** : Analyse par mots-clés uniquement
2. **Whisper échoue** : Désactiver le système vocal
3. **Micro non détecté** : Continuer sans vocal
4. **Crash du jeu (Bug #7)** : Capturer et permettre report

## Performance et Optimisation

### Bottlenecks identifiés

1. **Chargement Whisper** : 5-10 secondes (une fois au démarrage)
2. **Transcription** : 2-5 secondes par report (dépend CPU)
3. **Requête Gemma3** : 1-3 secondes (dépend du modèle et CPU)

### Optimisations possibles

1. **Modèle Whisper** :
   - Tiny pour wake word (rapide)
   - Base pour transcription complète (compromis)

2. **Cache Whisper** :
   - Garder le modèle en mémoire (déjà fait)

3. **Async Ollama** :
   - Ne pas bloquer le jeu pendant l'analyse
   - Thread séparé (déjà implémenté)

4. **Buffer audio** :
   - Circulaire de 3s (évite accumulation mémoire)

## Configuration Système

### Variables d'environnement

Aucune pour l'instant, tout est hardcodé. Évolutions possibles :

```python
# À implémenter
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
WAKE_WORD = os.getenv("WAKE_WORD", "bug")
```

### Fichiers de configuration

Actuellement aucun. Évolution possible : `config.json`

```json
{
    "voice": {
        "wake_word": "bug",
        "recording_duration": 8,
        "whisper_model": "base"
    },
    "analysis": {
        "ollama_url": "http://localhost:11434",
        "model": "gemma2:2b"
    },
    "game": {
        "enable_bugs": true,
        "bug_probability": 1.0
    }
}
```

## Tests

### Tests unitaires (à implémenter)

```python
# test_puissance4.py
def test_bug_1_minuscule_symbol():
    game = Puissance4()
    game.move_count = 7
    assert game.get_player_symbol(1) == 'x'

# test_voice_detector.py
def test_wake_word_detection():
    detector = VoiceDetector()
    # Mock audio with "bug"
    assert detector.check_wake_word(audio) == True

# test_bug_analyzer.py
def test_keyword_matching():
    bugs = get_bug_by_keywords("le compteur est faux")
    assert 3 in [b['id'] for b in bugs]
```

### Tests d'intégration

```python
# test_integration.py
def test_full_workflow():
    system = GameReportSystem()
    # Simuler une partie avec reports
    # Vérifier le rapport final
```

## Évolutions Futures

### Court terme
- [ ] Tests unitaires et d'intégration
- [ ] Configuration via fichier JSON
- [ ] Logs structurés (JSON) pour analyse
- [ ] Métriques de performance

### Moyen terme
- [ ] Interface graphique (Pygame/Tkinter)
- [ ] Enregistrement vidéo + replay
- [ ] Base de données (SQLite) pour historique
- [ ] Export rapports (JSON/CSV)

### Long terme
- [ ] Dashboard web (React/Vue)
- [ ] Support multi-jeux
- [ ] API REST pour intégration externe
- [ ] Machine Learning pour prédiction de bugs

## Références

- **Whisper** : https://github.com/openai/whisper
- **Ollama** : https://ollama.ai/
- **Gemma3** : https://ollama.ai/library/gemma2
- **sounddevice** : https://python-sounddevice.readthedocs.io/

---

Document maintenu par l'équipe Antivan Crows - CHPS0705

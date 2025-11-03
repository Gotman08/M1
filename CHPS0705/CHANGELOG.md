# Changelog - Améliorations et Corrections

## Version 1.1.0 - Améliorations et Stabilité

### Corrections Majeures

#### voice_detector.py
- **Gestion mémoire améliorée**
  - Correction de la logique du buffer circulaire (ligne 49)
  - Ajout d'une limite de taille pour la queue audio (maxsize=1000)
  - Vidage propre des buffers lors de l'arrêt

- **Gestion des exceptions**
  - Protection du callback audio avec try/except
  - Gestion des cas mono/stéréo pour l'audio
  - Queue non-bloquante pour éviter les deadlocks

- **Optimisation du modèle Whisper**
  - Chargement unique du modèle au démarrage (évite les rechargements)
  - Séparation de la fonction load_whisper_model()
  - Validation de la taille audio avant transcription
  - Normalisation du volume audio

- **Arrêt propre**
  - Attente de la terminaison des threads (join avec timeout)
  - Fermeture sécurisée du stream audio
  - Vidage des buffers et queues
  - Messages d'erreur détaillés

#### main.py
- **Gestion des ressources**
  - Vérification de l'état du système vocal avant arrêt
  - Variable voice_started pour tracker l'état
  - Gestion propre dans finally block

- **Compatibilité**
  - Suppression des emojis (problèmes d'affichage sur certains terminaux)
  - Messages ASCII pour meilleure compatibilité

- **Interruptions**
  - Support de Ctrl+C pendant l'attente après crash
  - Propagation propre des KeyboardInterrupt
  - Messages d'interruption clairs

- **Robustesse**
  - Gestion d'échec du démarrage vocal
  - Mode dégradé sans vocal si nécessaire
  - Try/except sur l'arrêt du système vocal

#### puissance4.py
- **clear_screen()**
  - Ajout d'un fallback avec lignes vides si os.system échoue
  - Gestion d'exception pour éviter les crashs

- **play_turn()**
  - Validation stricte des entrées utilisateur
  - Limite de longueur pour sécurité (max 10 caractères)
  - Compteur de tentatives invalides (max 5)
  - Protection contre les injections
  - Support de Ctrl+C pendant la saisie

- **Sécurité**
  - Validation avec isdigit()
  - Strip() des espaces
  - Limitation du nombre de tentatives

#### bug_analyzer.py
- **check_ollama_available()**
  - Exceptions spécifiques (ConnectionError, Timeout)
  - Timeout augmenté à 3 secondes
  - Messages d'erreur détaillés

- **_query_gemma()**
  - Système de retry (max 2 tentatives)
  - Délai entre tentatives (2 secondes)
  - Timeout configurable (défaut 45s)
  - Validation de la structure JSON de réponse
  - Gestion des timeouts réseau
  - Gestion des erreurs de connexion
  - Messages de progression

- **Imports**
  - Ajout de l'import time (nécessaire pour retry)

#### voice_transcriber.py
- **load_model()**
  - Retourne un booléen de succès
  - Gestion des exceptions de chargement
  - Messages d'erreur explicites

- **transcribe()**
  - Validation des données audio (None, vides)
  - Vérification du volume audio (détection audio silencieux)
  - Normalisation du volume audio
  - Validation du résultat Whisper
  - Gestion MemoryError spécifique
  - Messages d'erreur détaillés dans le dict de retour

### Ajouts

#### config.py
- **Nouveau fichier de configuration centralisée**
  - VOICE_CONFIG : Paramètres vocaux
  - ANALYSIS_CONFIG : Paramètres IA/Ollama
  - GAME_CONFIG : Paramètres du jeu
  - DISPLAY_CONFIG : Paramètres d'affichage
  - DEBUG_CONFIG : Paramètres de debug

### Améliorations de Qualité

1. **Gestion de la Mémoire**
   - Buffers avec tailles limitées
   - Queues avec maxsize
   - Vidage propre des ressources

2. **Gestion des Erreurs**
   - Exceptions spécifiques au lieu de Exception générique
   - Messages d'erreur détaillés et localisés
   - Fallbacks pour tous les composants critiques

3. **Robustesse**
   - Timeouts sur toutes les opérations réseau
   - Retry automatique sur les échecs temporaires
   - Validation de toutes les entrées utilisateur

4. **Compatibilité**
   - Support multi-plateforme (Windows/Linux/Mac)
   - Gestion mono/stéréo audio
   - Fallbacks pour terminaux limités

5. **Performance**
   - Chargement unique des modèles ML
   - Buffers circulaires optimisés
   - Threads daemon proprement gérés

6. **Sécurité**
   - Validation stricte des entrées
   - Limites de taille
   - Protection contre les injections

### Bugs Intentionnels Préservés

Tous les 8 bugs intentionnels pour le PoC sont préservés :
- Bug #1 : Symbole en minuscule
- Bug #2 : Message mal formaté
- Bug #3 : Compteur +1
- Bug #4 : Colonnes 0-6
- Bug #5 : Diagonale descendante
- Bug #6 : Match nul à 41
- Bug #7 : Crash colonne pleine
- Bug #8 : Boucle infinie dernière ligne

### Points Techniques

**Améliorations de Code**
- Meilleure séparation des responsabilités
- Constantes configurables
- Documentation améliorée
- Type hints plus complets

**Tests Recommandés**
- [ ] Tester l'arrêt propre avec Ctrl+C
- [ ] Tester sans Ollama installé
- [ ] Tester avec micro non disponible
- [ ] Tester les 8 bugs intentionnels
- [ ] Tester avec entrées invalides multiples
- [ ] Tester sur Windows/Linux/Mac

### Migration depuis v1.0.0

Aucune migration nécessaire, compatibilité totale.

Les utilisateurs peuvent optionnellement :
1. Utiliser config.py pour personnaliser les paramètres
2. Vérifier que FFmpeg est bien installé
3. Mettre à jour Ollama si nécessaire

### Notes

Cette version améliore considérablement la stabilité et la robustesse du système tout en préservant les bugs intentionnels nécessaires pour le PoC de report vocal.

---

**Équipe** : Antivan Crows
**Module** : CHPS0705
**Date** : 2025

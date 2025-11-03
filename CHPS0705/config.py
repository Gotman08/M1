"""
Configuration centralisée pour le système de report vocal
"""

# Configuration du système vocal
VOICE_CONFIG = {
    "wake_word": "bug",  # Mot de déclenchement
    "sample_rate": 16000,  # Hz
    "recording_duration": 8,  # Secondes d'enregistrement après détection
    "whisper_model": "base",  # tiny, base, small, medium, large
}

# Configuration de l'analyse IA
ANALYSIS_CONFIG = {
    "ollama_url": "http://localhost:11434",
    "model_name": "gemma2:2b",
    "timeout": 45,  # Timeout pour les requêtes Ollama (secondes)
    "max_retries": 2,  # Nombre de tentatives en cas d'échec
}

# Configuration du jeu
GAME_CONFIG = {
    "rows": 6,
    "cols": 7,
    "max_invalid_attempts": 5,  # Nombre max de tentatives invalides par tour
}

# Configuration de l'affichage
DISPLAY_CONFIG = {
    "use_emojis": False,  # Utiliser des emojis (peut causer des problèmes de compatibilité)
    "clear_screen": True,  # Effacer l'écran entre les tours
}

# Configuration du debug
DEBUG_CONFIG = {
    "verbose": False,  # Afficher des logs détaillés
    "save_reports": False,  # Sauvegarder les reports dans un fichier
    "reports_file": "reports.json",  # Nom du fichier de sauvegarde
}

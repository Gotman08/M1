"""
Module de transcription vocale utilisant Whisper d'OpenAI
Convertit l'audio en texte pour l'analyse des bugs
"""
import whisper
import numpy as np
from typing import Optional


class VoiceTranscriber:
    def __init__(self, model_size: str = "base"):
        """
        Initialise le transcripteur avec un modèle Whisper

        Args:
            model_size: Taille du modèle ('tiny', 'base', 'small', 'medium', 'large')
                       'tiny' est le plus rapide mais moins précis
                       'base' est un bon compromis
        """
        self.model_size = model_size
        self.model = None
        print(f"[Transcription] Initialisation du modèle Whisper ({model_size})...")

    def load_model(self) -> bool:
        """
        Charge le modèle Whisper

        Returns:
            True si le chargement a réussi, False sinon
        """
        if self.model is None:
            try:
                print("[Transcription] Chargement du modele en cours...")
                self.model = whisper.load_model(self.model_size)
                print("[Transcription] Modele charge avec succes!")
                return True
            except Exception as e:
                print(f"[Transcription] Erreur lors du chargement du modele: {e}")
                return False
        return True

    def transcribe(self, audio_data: np.ndarray, sample_rate: int = 16000) -> dict:
        """
        Transcrit l'audio en texte

        Args:
            audio_data: Données audio en numpy array
            sample_rate: Taux d'échantillonnage de l'audio

        Returns:
            dict avec:
                - text: Transcription complète
                - language: Langue détectée
                - segments: Segments de la transcription avec timestamps
                - error: Message d'erreur ou None
        """
        # Vérifier que le modèle est chargé
        if self.model is None:
            if not self.load_model():
                return {
                    'text': '',
                    'language': 'fr',
                    'segments': [],
                    'error': 'Modele Whisper non disponible'
                }

        try:
            # Valider les données audio
            if audio_data is None or len(audio_data) == 0:
                return {
                    'text': '',
                    'language': 'fr',
                    'segments': [],
                    'error': 'Donnees audio vides'
                }

            # S'assurer que l'audio est au bon format
            audio_normalized = audio_data.astype(np.float32)

            # Si l'audio est trop court, retourner un résultat vide
            if len(audio_normalized) < sample_rate * 0.5:  # Moins de 0.5 secondes
                return {
                    'text': '',
                    'language': 'fr',
                    'segments': [],
                    'error': 'Audio trop court (minimum 0.5 secondes)'
                }

            # Normaliser le volume si nécessaire
            max_val = np.max(np.abs(audio_normalized))
            if max_val > 0:
                audio_normalized = audio_normalized / max_val
            else:
                return {
                    'text': '',
                    'language': 'fr',
                    'segments': [],
                    'error': 'Audio silencieux'
                }

            # Transcrire avec Whisper
            result = self.model.transcribe(
                audio_normalized,
                language="fr",
                fp16=False,
                verbose=False,
                task="transcribe"
            )

            # Valider le résultat
            if not result or 'text' not in result:
                return {
                    'text': '',
                    'language': 'fr',
                    'segments': [],
                    'error': 'Resultat de transcription invalide'
                }

            # Extraire les informations pertinentes
            transcription = {
                'text': result['text'].strip(),
                'language': result.get('language', 'fr'),
                'segments': result.get('segments', []),
                'error': None
            }

            return transcription

        except MemoryError:
            print("[Transcription] Erreur: Memoire insuffisante")
            return {
                'text': '',
                'language': 'fr',
                'segments': [],
                'error': 'Memoire insuffisante'
            }
        except Exception as e:
            print(f"[Transcription] Erreur lors de la transcription: {e}")
            return {
                'text': '',
                'language': 'fr',
                'segments': [],
                'error': str(e)
            }

    def transcribe_and_print(self, audio_data: np.ndarray, sample_rate: int = 16000) -> str:
        """
        Transcrit et affiche le résultat

        Returns:
            Le texte transcrit
        """
        result = self.transcribe(audio_data, sample_rate)

        if result['error']:
            print(f"[Transcription] Erreur: {result['error']}")
            return ""

        text = result['text']
        if text:
            print(f"\n{'='*50}")
            print(f"[Transcription] Texte détecté:")
            print(f"{text}")
            print(f"{'='*50}\n")
        else:
            print("[Transcription] Aucun texte détecté dans l'audio")

        return text

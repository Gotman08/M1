"""
Détecteur de wake word vocal pour le système de report de bugs
Écoute en continu et détecte le mot "bug" pour activer l'enregistrement
"""
import sounddevice as sd
import numpy as np
import threading
import queue
import time
from typing import Callable, Optional


class VoiceDetector:
    def __init__(self, wake_word: str = "bug", sample_rate: int = 16000):
        self.wake_word = wake_word.lower()
        self.sample_rate = sample_rate
        self.is_listening = False
        self.is_recording = False
        self.audio_queue = queue.Queue(maxsize=1000)  # Limite de taille pour éviter la surcharge
        self.callback_function: Optional[Callable] = None
        self.recording_duration = 8  # Durée d'enregistrement après détection (secondes)
        self.buffer_size = int(sample_rate * 3)  # Buffer de 3 secondes
        self.audio_buffer = np.array([], dtype=np.float32)
        self.whisper_model = None  # Modèle Whisper chargé une seule fois
        self.stream = None  # Référence au stream audio
        self.processing_thread = None  # Référence au thread de traitement

    def set_callback(self, callback: Callable):
        """
        Définit la fonction de callback qui sera appelée avec l'audio enregistré
        """
        self.callback_function = callback

    def audio_callback(self, indata, frames, time_info, status):
        """
        Callback appelé par sounddevice pour chaque chunk audio
        """
        try:
            if status:
                print(f"[Audio] Statut: {status}")

            # Gérer le cas mono/stéréo
            if len(indata.shape) == 1:
                audio_data = indata.copy()
            else:
                audio_data = indata[:, 0].copy()  # Prendre un seul canal

            # Ajouter l'audio au buffer
            self.audio_buffer = np.append(self.audio_buffer, audio_data)

            # Maintenir un buffer de taille fixe (rolling buffer) - correction de la logique
            if len(self.audio_buffer) > self.buffer_size * 1.5:
                self.audio_buffer = self.audio_buffer[-self.buffer_size:]

            # Si on est en mode enregistrement actif, ajouter à la queue
            if self.is_recording:
                try:
                    self.audio_queue.put(audio_data, block=False)
                except queue.Full:
                    pass  # Ignorer si la queue est pleine
        except Exception as e:
            print(f"[Audio] Erreur dans audio_callback: {e}")

    def load_whisper_model(self):
        """
        Charge le modèle Whisper pour la détection du wake word
        """
        try:
            if self.whisper_model is None:
                import whisper
                print("[Vocal] Chargement du modèle Whisper pour détection...")
                self.whisper_model = whisper.load_model("tiny")
                print("[Vocal] Modèle Whisper chargé avec succès!")
                return True
        except Exception as e:
            print(f"[Vocal] Erreur lors du chargement de Whisper: {e}")
            return False
        return True

    def check_wake_word(self, audio_data: np.ndarray) -> bool:
        """
        Vérifie si le wake word est présent dans l'audio
        Utilise Whisper pour la transcription en temps réel
        """
        try:
            # Vérifier que le modèle est chargé
            if self.whisper_model is None:
                if not self.load_whisper_model():
                    return False

            # Vérifier la taille minimale de l'audio
            if len(audio_data) < self.sample_rate * 0.5:
                return False

            # Normaliser l'audio
            audio_normalized = audio_data.astype(np.float32)

            # Normaliser le volume si nécessaire
            max_val = np.max(np.abs(audio_normalized))
            if max_val > 0:
                audio_normalized = audio_normalized / max_val

            # Transcrire avec Whisper
            result = self.whisper_model.transcribe(
                audio_normalized,
                language="fr",
                fp16=False,
                verbose=False
            )

            text = result["text"].lower().strip()

            # Vérifier si le wake word est présent
            if self.wake_word in text:
                print(f"\n[Vocal] Wake word détecté: '{text}'")
                return True

            return False

        except Exception as e:
            print(f"[Vocal] Erreur lors de la vérification du wake word: {e}")
            return False

    def process_audio_stream(self):
        """
        Thread qui traite le stream audio en continu
        """
        check_interval = 2.0  # Vérifier toutes les 2 secondes
        last_check = time.time()

        while self.is_listening:
            current_time = time.time()

            # Vérifier périodiquement si le wake word est présent
            if not self.is_recording and (current_time - last_check) >= check_interval:
                if len(self.audio_buffer) >= self.sample_rate * 2:  # Au moins 2 secondes d'audio
                    # Prendre les 2 dernières secondes
                    audio_chunk = self.audio_buffer[-(self.sample_rate * 2):]

                    if self.check_wake_word(audio_chunk):
                        # Wake word détecté, démarrer l'enregistrement
                        self.start_recording()

                last_check = current_time

            time.sleep(0.1)

    def start_recording(self):
        """
        Démarre l'enregistrement complet du message après détection du wake word
        """
        if self.is_recording:
            return

        print(f"\n{'='*50}")
        print("[Vocal] Enregistrement du report en cours...")
        print(f"[Vocal] Parlez pendant {self.recording_duration} secondes...")
        print(f"{'='*50}\n")

        self.is_recording = True
        self.audio_queue = queue.Queue()  # Reset la queue

        # Lancer un thread pour arrêter l'enregistrement après la durée définie
        threading.Thread(target=self.stop_recording_after_delay, daemon=True).start()

    def stop_recording_after_delay(self):
        """
        Arrête l'enregistrement après le délai défini
        """
        time.sleep(self.recording_duration)

        print("[Vocal] Enregistrement terminé. Traitement en cours...")

        # Récupérer tout l'audio enregistré
        audio_chunks = []
        while not self.audio_queue.empty():
            audio_chunks.append(self.audio_queue.get())

        if audio_chunks:
            # Combiner tous les chunks
            full_audio = np.concatenate(audio_chunks)

            # Appeler le callback avec l'audio complet
            if self.callback_function:
                threading.Thread(
                    target=self.callback_function,
                    args=(full_audio,),
                    daemon=True
                ).start()

        self.is_recording = False
        print("[Vocal] Prêt pour un nouveau report (dites 'bug' pour signaler)\n")

    def start_listening(self):
        """
        Démarre l'écoute continue
        """
        if self.is_listening:
            return

        print("[Vocal] Démarrage de l'écoute continue...")

        # Précharger le modèle Whisper
        if not self.load_whisper_model():
            print("[Vocal] Impossible de démarrer sans le modèle Whisper")
            return False

        print(f"[Vocal] Dites '{self.wake_word}' pour signaler un bug")

        try:
            self.is_listening = True

            # Démarrer le stream audio
            self.stream = sd.InputStream(
                channels=1,
                samplerate=self.sample_rate,
                callback=self.audio_callback,
                blocksize=int(self.sample_rate * 0.5)  # Blocks de 0.5 secondes
            )
            self.stream.start()

            # Démarrer le thread de traitement
            self.processing_thread = threading.Thread(
                target=self.process_audio_stream,
                daemon=True
            )
            self.processing_thread.start()

            print("[Vocal] Écoute active!\n")
            return True

        except Exception as e:
            print(f"[Vocal] Erreur lors du démarrage de l'écoute: {e}")
            self.is_listening = False
            return False

    def stop_listening(self):
        """
        Arrête l'écoute et libère les ressources
        """
        if not self.is_listening:
            return

        print("\n[Vocal] Arrêt de l'écoute...")
        self.is_listening = False
        self.is_recording = False

        # Attendre un peu pour que le thread de traitement se termine
        time.sleep(0.5)

        # Fermer le stream audio
        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
                self.stream = None
            except Exception as e:
                print(f"[Vocal] Erreur lors de la fermeture du stream: {e}")

        # Attendre que le thread de traitement se termine
        if self.processing_thread is not None and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2.0)
            if self.processing_thread.is_alive():
                print("[Vocal] Attention: Le thread de traitement n'a pas terminé proprement")

        # Vider les buffers
        self.audio_buffer = np.array([], dtype=np.float32)
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

        print("[Vocal] Écoute arrêtée et ressources libérées.")

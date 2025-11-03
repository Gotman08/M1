#!/usr/bin/env python3
"""
PoC - Système de Report Vocal de Bugs pour Beta-Tests
Jeu Puissance 4 avec bugs intentionnels et report vocal

Équipe: Antivan Crows
Module: CHPS0705
"""
import sys
import time
from game.puissance4 import Puissance4
from voice.voice_detector import VoiceDetector
from voice.voice_transcriber import VoiceTranscriber
from analysis.bug_analyzer import BugAnalyzer


class GameReportSystem:
    def __init__(self):
        self.game = Puissance4()
        self.voice_detector = VoiceDetector(wake_word="bug")
        self.transcriber = VoiceTranscriber(model_size="base")
        self.analyzer = BugAnalyzer()
        self.voice_enabled = False

    def display_welcome(self):
        """
        Affiche l'écran de bienvenue
        """
        print("\n" + "="*70)
        print(" " * 15 + "BIENVENUE DANS LE SYSTÈME DE BETA-TEST")
        print(" " * 20 + "Jeu Puissance 4 - Version PoC")
        print("="*70)
        print("\nCe jeu contient des bugs intentionnels pour tester le système de report.")
        print("Votre mission: Jouer et signaler tous les bugs que vous trouvez!\n")
        print("-"*70)
        print("COMMENT SIGNALER UN BUG:")
        print("-"*70)

        if self.voice_enabled:
            print("  1. Dites 'BUG' pour activer l'enregistrement")
            print("  2. Décrivez le bug que vous avez observé")
            print("  3. Le système analysera automatiquement votre report")
        else:
            print("  Mode vocal désactivé (Ollama/Whisper non disponible)")
            print("  Les bugs seront affichés à la fin de la partie")

        print("-"*70)
        print("\nRègles du jeu:")
        print("  - Alignez 4 pions horizontalement, verticalement ou en diagonale")
        print("  - Les joueurs jouent à tour de rôle")
        print("  - Tapez 'q' pour quitter à tout moment")
        print("\n" + "="*70 + "\n")

        input("Appuyez sur Entrée pour commencer...")

    def setup_voice_system(self):
        """
        Configure le système vocal
        """
        print("\n[Setup] Configuration du système de report vocal...")

        # Vérifier si Ollama est disponible
        if not self.analyzer.check_ollama_available():
            print("[Setup] ⚠ Ollama n'est pas disponible sur http://localhost:11434")
            print("[Setup] Le système fonctionnera avec l'analyse par mots-clés uniquement")
            print("[Setup] Pour une meilleure analyse, installez Ollama et le modèle gemma2:2b")
            print("[Setup] Commande: ollama pull gemma2:2b")

        # Charger le modèle Whisper
        print("[Setup] Chargement de Whisper (cela peut prendre un moment)...")
        try:
            self.transcriber.load_model()
            self.voice_enabled = True
            print("[Setup] ✓ Système vocal prêt!")
        except Exception as e:
            print(f"[Setup] ✗ Erreur lors du chargement de Whisper: {e}")
            print("[Setup] Le jeu continuera sans le système vocal")
            self.voice_enabled = False

        return self.voice_enabled

    def handle_voice_report(self, audio_data):
        """
        Traite un report vocal
        """
        try:
            # Transcrire l'audio
            transcription = self.transcriber.transcribe_and_print(audio_data)

            if not transcription:
                print("[Report] Aucun texte détecté, veuillez réessayer.")
                return

            # Analyser le report
            game_context = self.game.get_game_context()
            self.analyzer.analyze_report(transcription, game_context)

            print("[Report] Report enregistré et analysé avec succès!")

        except Exception as e:
            print(f"[Report] Erreur lors du traitement: {e}")

    def run_game(self):
        """
        Lance la partie
        """
        voice_started = False
        try:
            # Démarrer l'écoute vocale si disponible
            if self.voice_enabled:
                self.voice_detector.set_callback(self.handle_voice_report)
                voice_started = self.voice_detector.start_listening()
                if not voice_started:
                    print("[Jeu] Le système vocal n'a pas pu démarrer, continuation sans vocal")
                    self.voice_enabled = False

            # Boucle de jeu principale
            while not self.game.game_over:
                try:
                    if not self.game.play_turn():
                        # Le joueur a quitté
                        print("\n[Jeu] Partie interrompue par le joueur.")
                        break
                except KeyboardInterrupt:
                    # Permettre l'interruption propre pendant le jeu
                    print("\n[Jeu] Interruption détectée...")
                    raise
                except Exception as e:
                    # Capturer les crashes (bugs niveau 5)
                    print(f"\n{'='*70}")
                    print("LE JEU A CRASHE!")  # Éviter les emojis pour compatibilité
                    print(f"{'='*70}")
                    print(f"Erreur: {e}")
                    print("\nC'est un bug intentionnel! Notez-le dans votre rapport.")
                    print(f"{'='*70}\n")

                    # Laisser le temps au joueur de faire un report (interruptible)
                    if self.voice_enabled and voice_started:
                        print("Vous avez 15 secondes pour signaler ce bug vocalement...")
                        print("(Appuyez sur Ctrl+C pour passer)")
                        try:
                            time.sleep(15)
                        except KeyboardInterrupt:
                            print("\nTemps d'attente interrompu.")
                    break

            # Afficher le résultat de la partie
            if self.game.game_over:
                self.game.clear_screen()
                self.game.display_board()

                if self.game.winner:
                    print(f"\nFelicitations! Le Joueur {self.game.winner} a gagne!\n")
                else:
                    print("\nMatch nul!\n")

        finally:
            # Arrêter l'écoute vocale proprement
            if self.voice_enabled and voice_started:
                try:
                    print("\nArret du systeme vocal...")
                    self.voice_detector.stop_listening()
                    time.sleep(2)  # Laisser le temps de traiter les derniers reports
                except Exception as e:
                    print(f"[Jeu] Erreur lors de l'arret du systeme vocal: {e}")

    def display_bug_hunt_results(self):
        """
        Affiche les résultats de la chasse aux bugs
        """
        print("\n\nPréparation du rapport final...")
        time.sleep(2)

        self.analyzer.display_final_report()

    def run(self):
        """
        Point d'entrée principal
        """
        voice_system_active = False
        try:
            # Afficher l'écran de bienvenue
            self.display_welcome()

            # Configuration du système vocal
            voice_system_active = self.setup_voice_system()

            # Lancer le jeu
            print("\n[Jeu] Demarrage de la partie...")
            time.sleep(1)

            self.run_game()

            # Afficher le rapport final
            self.display_bug_hunt_results()

            print("\nMerci d'avoir participe a ce beta-test!")
            print("Les donnees collectees aideront a ameliorer le systeme de report.\n")

        except KeyboardInterrupt:
            print("\n\n[Systeme] Interruption par l'utilisateur (Ctrl+C)")
            print("Arret du systeme...\n")
        except Exception as e:
            print(f"\n[Systeme] Erreur critique: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Nettoyage propre des ressources
            if voice_system_active and hasattr(self, 'voice_detector'):
                try:
                    if self.voice_detector.is_listening:
                        print("[Systeme] Nettoyage final des ressources vocales...")
                        self.voice_detector.stop_listening()
                except Exception as e:
                    print(f"[Systeme] Erreur lors du nettoyage: {e}")


def main():
    """
    Point d'entrée du programme
    """
    system = GameReportSystem()
    system.run()


if __name__ == "__main__":
    main()

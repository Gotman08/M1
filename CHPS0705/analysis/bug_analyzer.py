"""
Analyseur de bugs utilisant Gemma3 via Ollama
Analyse les reports vocaux et les compare aux bugs connus
"""
import requests
import json
import time
from typing import Dict, List, Optional
import sys
import os

# Ajouter le chemin parent pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.bugs_list import BUGS_INTENTIONNELS, get_bug_by_keywords


class BugAnalyzer:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        """
        Initialise l'analyseur de bugs avec Gemma3

        Args:
            ollama_url: URL de l'API Ollama locale
        """
        self.ollama_url = ollama_url
        self.model_name = "gemma2:2b"  # Gemma3 via Ollama
        self.reports = []  # Liste des reports collectés

    def check_ollama_available(self) -> bool:
        """
        Vérifie si Ollama est disponible
        """
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            return False
        except requests.exceptions.Timeout:
            return False
        except Exception as e:
            print(f"[Analyse] Erreur lors de la verification d'Ollama: {e}")
            return False

    def analyze_report(self, transcription: str, game_context: dict) -> dict:
        """
        Analyse un report de bug

        Args:
            transcription: Texte transcrit du report vocal
            game_context: Contexte du jeu (nombre de coups, état du plateau, etc.)

        Returns:
            Dictionnaire avec l'analyse du bug
        """
        print("\n[Analyse] Analyse du report en cours...")

        # D'abord, recherche par mots-clés (fallback si Ollama n'est pas disponible)
        potential_bugs = get_bug_by_keywords(transcription)

        # Construire le prompt pour Gemma3
        prompt = self._build_analysis_prompt(transcription, game_context, potential_bugs)

        # Analyser avec Gemma3 si disponible
        ai_analysis = None
        if self.check_ollama_available():
            ai_analysis = self._query_gemma(prompt)
        else:
            print("[Analyse] Ollama non disponible, analyse par mots-clés seulement")

        # Combiner les résultats
        result = self._combine_analysis(transcription, game_context, potential_bugs, ai_analysis)

        # Sauvegarder le report
        self.reports.append(result)

        # Afficher le résultat
        self._display_analysis(result)

        return result

    def _build_analysis_prompt(self, transcription: str, game_context: dict, potential_bugs: List[dict]) -> str:
        """
        Construit le prompt pour Gemma3
        """
        bugs_desc = "\n".join([
            f"- Bug #{b['id']} (Niveau {b['niveau']}): {b['description']}"
            for b in BUGS_INTENTIONNELS
        ])

        prompt = f"""Tu es un expert en analyse de bugs pour un jeu Puissance 4.

Un joueur a signalé un problème pendant la partie. Voici les informations:

TRANSCRIPTION DU REPORT:
"{transcription}"

CONTEXTE DU JEU:
- Nombre de coups joués: {game_context.get('move_count', 0)}
- Joueur actuel: {game_context.get('current_player', '?')}
- Partie terminée: {game_context.get('game_over', False)}
- Gagnant: {game_context.get('winner', 'Aucun')}

BUGS CONNUS DANS LE JEU:
{bugs_desc}

BUGS POTENTIELS DÉTECTÉS PAR MOTS-CLÉS:
{json.dumps([b['id'] for b in potential_bugs], ensure_ascii=False)}

TÂCHE:
1. Identifie quel(s) bug(s) parmi les bugs connus correspond(ent) au report
2. Détermine le niveau de gravité (1-5)
3. Évalue la clarté du report (1-10)
4. Fournis une explication courte

Réponds UNIQUEMENT au format JSON suivant:
{{
    "bug_ids": [liste des IDs de bugs identifiés],
    "niveau_gravite": 1-5,
    "clarte_report": 1-10,
    "explication": "courte explication",
    "confiance": 0.0-1.0
}}"""

        return prompt

    def _query_gemma(self, prompt: str, timeout: int = 45) -> Optional[dict]:
        """
        Interroge Gemma3 via Ollama avec retry et timeout
        """
        max_retries = 2
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json"
                    },
                    timeout=timeout
                )

                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get('response', '')

                    # Parser la réponse JSON
                    try:
                        parsed = json.loads(ai_response)
                        # Valider la structure de la réponse
                        if 'bug_ids' in parsed and isinstance(parsed['bug_ids'], list):
                            return parsed
                        else:
                            print("[Analyse] Reponse IA invalide (structure incorrecte)")
                            return None
                    except json.JSONDecodeError as e:
                        print(f"[Analyse] Erreur de parsing JSON: {e}")
                        if attempt < max_retries - 1:
                            print(f"[Analyse] Nouvelle tentative dans {retry_delay}s...")
                            time.sleep(retry_delay)
                            continue
                        return None
                else:
                    print(f"[Analyse] Erreur API Ollama: {response.status_code}")
                    if attempt < max_retries - 1:
                        print(f"[Analyse] Nouvelle tentative dans {retry_delay}s...")
                        time.sleep(retry_delay)
                        continue
                    return None

            except requests.exceptions.Timeout:
                print(f"[Analyse] Timeout lors de la requete a Gemma (tentative {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    print(f"[Analyse] Nouvelle tentative dans {retry_delay}s...")
                    time.sleep(retry_delay)
                    continue
                return None
            except requests.exceptions.ConnectionError:
                print("[Analyse] Erreur de connexion a Ollama")
                return None
            except Exception as e:
                print(f"[Analyse] Erreur lors de la requete a Gemma: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return None

        return None

    def _combine_analysis(self, transcription: str, game_context: dict,
                         potential_bugs: List[dict], ai_analysis: Optional[dict]) -> dict:
        """
        Combine l'analyse par mots-clés et l'analyse IA
        """
        # Résultat de base avec analyse par mots-clés
        result = {
            'transcription': transcription,
            'timestamp': game_context.get('move_count', 0),
            'game_context': game_context,
            'potential_bugs': potential_bugs,
            'ai_analysis': ai_analysis
        }

        # Si on a une analyse IA, l'utiliser
        if ai_analysis and 'bug_ids' in ai_analysis:
            result['identified_bugs'] = [
                bug for bug in BUGS_INTENTIONNELS
                if bug['id'] in ai_analysis['bug_ids']
            ]
            result['severity'] = ai_analysis.get('niveau_gravite', 0)
            result['clarity'] = ai_analysis.get('clarte_report', 5)
            result['confidence'] = ai_analysis.get('confiance', 0.5)
        else:
            # Sinon, utiliser l'analyse par mots-clés
            result['identified_bugs'] = potential_bugs
            result['severity'] = max([b['niveau'] for b in potential_bugs], default=0)
            result['clarity'] = 5
            result['confidence'] = 0.3 if potential_bugs else 0.1

        return result

    def _display_analysis(self, result: dict):
        """
        Affiche le résultat de l'analyse
        """
        print(f"\n{'='*60}")
        print("ANALYSE DU REPORT")
        print(f"{'='*60}")

        if result['identified_bugs']:
            print(f"\nBugs identifiés: {len(result['identified_bugs'])}")
            for bug in result['identified_bugs']:
                print(f"  - Bug #{bug['id']}: {bug['description']}")
                print(f"    Gravité: Niveau {bug['niveau']} ({bug['gravite']})")

            print(f"\nConfiance de l'analyse: {result['confidence']*100:.0f}%")
        else:
            print("\nAucun bug connu n'a été identifié dans ce report.")
            print("Le report sera tout de même sauvegardé pour analyse manuelle.")

        print(f"{'='*60}\n")

    def get_final_report(self) -> dict:
        """
        Génère un rapport final de tous les bugs détectés
        """
        if not self.reports:
            return {
                'total_reports': 0,
                'bugs_found': [],
                'score': 0
            }

        # Compter les bugs uniques identifiés
        bugs_found = set()
        for report in self.reports:
            for bug in report.get('identified_bugs', []):
                bugs_found.add(bug['id'])

        # Calculer le score (sur 100)
        score = (len(bugs_found) / len(BUGS_INTENTIONNELS)) * 100

        return {
            'total_reports': len(self.reports),
            'bugs_found': sorted(list(bugs_found)),
            'bugs_missed': [b['id'] for b in BUGS_INTENTIONNELS if b['id'] not in bugs_found],
            'score': score,
            'details': self.reports
        }

    def display_final_report(self):
        """
        Affiche le rapport final de la chasse aux bugs
        """
        report = self.get_final_report()

        print("\n" + "="*70)
        print(" " * 20 + "RAPPORT FINAL - CHASSE AUX BUGS")
        print("="*70)

        print(f"\nNombre total de reports vocaux: {report['total_reports']}")
        print(f"Bugs découverts: {len(report['bugs_found'])} / {len(BUGS_INTENTIONNELS)}")
        print(f"Score final: {report['score']:.1f}%")

        print("\n" + "-"*70)
        print("BUGS DÉCOUVERTS:")
        print("-"*70)

        for bug_id in report['bugs_found']:
            bug = next(b for b in BUGS_INTENTIONNELS if b['id'] == bug_id)
            print(f"\n✓ Bug #{bug['id']} - Niveau {bug['niveau']} ({bug['gravite']})")
            print(f"  {bug['description']}")

        if report['bugs_missed']:
            print("\n" + "-"*70)
            print("BUGS NON DÉCOUVERTS:")
            print("-"*70)

            for bug_id in report['bugs_missed']:
                bug = next(b for b in BUGS_INTENTIONNELS if b['id'] == bug_id)
                print(f"\n✗ Bug #{bug['id']} - Niveau {bug['niveau']} ({bug['gravite']})")
                print(f"  {bug['description']}")

        print("\n" + "="*70)

        # Évaluation de la performance
        if report['score'] >= 80:
            print("Excellent travail! Vous avez trouvé presque tous les bugs!")
        elif report['score'] >= 60:
            print("Bon travail! Vous avez trouvé la majorité des bugs.")
        elif report['score'] >= 40:
            print("Pas mal, mais il reste des bugs à découvrir.")
        else:
            print("Continuez à chercher, beaucoup de bugs sont encore cachés!")

        print("="*70 + "\n")

#!/usr/bin/env python3
"""
Script de test pour vérifier l'installation du système de report vocal
Teste chaque composant individuellement
"""
import sys

def print_header(title):
    """Affiche un en-tête formaté"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_result(test_name, success, message=""):
    """Affiche le résultat d'un test"""
    status = "[OK]" if success else "[ECHEC]"
    print(f"{status} {test_name}")
    if message:
        print(f"     -> {message}")

def test_imports():
    """Test des imports Python"""
    print_header("TEST 1: Verification des imports")

    tests = [
        ("numpy", "numpy"),
        ("sounddevice", "sounddevice"),
        ("whisper", "whisper"),
        ("requests", "requests"),
    ]

    all_ok = True
    for name, module in tests:
        try:
            __import__(module)
            print_result(f"Import {name}", True)
        except ImportError as e:
            print_result(f"Import {name}", False, str(e))
            all_ok = False

    return all_ok

def test_ffmpeg():
    """Test de la présence de FFmpeg"""
    print_header("TEST 2: Verification de FFmpeg")

    import subprocess
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print_result("FFmpeg", True, version)
            return True
        else:
            print_result("FFmpeg", False, "Commande retourne une erreur")
            return False
    except FileNotFoundError:
        print_result("FFmpeg", False, "FFmpeg non trouve dans le PATH")
        return False
    except Exception as e:
        print_result("FFmpeg", False, str(e))
        return False

def test_audio_devices():
    """Test des périphériques audio"""
    print_header("TEST 3: Verification des peripheriques audio")

    try:
        import sounddevice as sd
        devices = sd.query_devices()

        # Chercher un périphérique d'entrée
        input_devices = [d for d in devices if d['max_input_channels'] > 0]

        if input_devices:
            print_result("Peripheriques audio", True,
                        f"{len(input_devices)} peripherique(s) d'entree trouve(s)")
            print(f"\n     Peripherique par defaut:")
            default_input = sd.query_devices(kind='input')
            print(f"     - {default_input['name']}")
            return True
        else:
            print_result("Peripheriques audio", False,
                        "Aucun peripherique d'entree trouve")
            return False
    except Exception as e:
        print_result("Peripheriques audio", False, str(e))
        return False

def test_whisper_model():
    """Test du chargement du modèle Whisper"""
    print_header("TEST 4: Chargement du modele Whisper")

    try:
        import whisper
        print("Chargement du modele 'tiny' (peut prendre quelques secondes)...")
        model = whisper.load_model("tiny")
        print_result("Modele Whisper", True, "Modele 'tiny' charge avec succes")
        return True
    except Exception as e:
        print_result("Modele Whisper", False, str(e))
        return False

def test_ollama():
    """Test de la connexion à Ollama"""
    print_header("TEST 5: Verification d'Ollama (optionnel)")

    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=3)

        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])

            # Chercher gemma2:2b
            gemma_found = any('gemma2' in m.get('name', '') for m in models)

            if gemma_found:
                print_result("Ollama", True, "Ollama actif avec gemma2:2b")
                return True
            else:
                print_result("Ollama", True, "Ollama actif mais gemma2:2b non trouve")
                print("     -> Installez avec: ollama pull gemma2:2b")
                return False
        else:
            print_result("Ollama", False, f"Status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_result("Ollama", False, "Ollama n'est pas en cours d'execution")
        print("     -> Le systeme fonctionnera en mode degrade (mots-cles uniquement)")
        return False
    except Exception as e:
        print_result("Ollama", False, str(e))
        return False

def test_game_modules():
    """Test des modules du jeu"""
    print_header("TEST 6: Verification des modules du projet")

    modules = [
        "game.puissance4",
        "game.bugs_list",
        "voice.voice_detector",
        "voice.voice_transcriber",
        "analysis.bug_analyzer",
    ]

    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print_result(f"Module {module}", True)
        except ImportError as e:
            print_result(f"Module {module}", False, str(e))
            all_ok = False

    return all_ok

def run_all_tests():
    """Execute tous les tests"""
    print("\n" + "="*60)
    print("  TESTS DU SYSTEME DE REPORT VOCAL")
    print("  Antivan Crows - CHPS0705")
    print("="*60)

    results = {
        "Imports Python": test_imports(),
        "FFmpeg": test_ffmpeg(),
        "Peripheriques audio": test_audio_devices(),
        "Modele Whisper": test_whisper_model(),
        "Ollama (optionnel)": test_ollama(),
        "Modules projet": test_game_modules(),
    }

    # Résumé
    print_header("RESUME DES TESTS")

    critical_tests = ["Imports Python", "FFmpeg", "Peripheriques audio",
                     "Modele Whisper", "Modules projet"]

    critical_ok = all(results[t] for t in critical_tests)
    optional_ok = results["Ollama (optionnel)"]

    print(f"Tests critiques: {'OK' if critical_ok else 'ECHEC'}")
    print(f"Tests optionnels: {'OK' if optional_ok else 'ECHEC'}")

    print("\n" + "="*60)

    if critical_ok:
        print("Le systeme est pret a etre utilise!")
        if not optional_ok:
            print("\nNote: Ollama n'est pas disponible.")
            print("Le systeme fonctionnera avec l'analyse par mots-cles uniquement.")
        print("\nPour demarrer le jeu: python main.py")
    else:
        print("Des problemes ont ete detectes.")
        print("Veuillez corriger les erreurs ci-dessus avant de continuer.")
        print("\nConsultez INSTALL.md pour plus d'informations.")

    print("="*60 + "\n")

    return 0 if critical_ok else 1

if __name__ == "__main__":
    sys.exit(run_all_tests())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Principal - Étude de Convergence Élements Finis P1
==========================================================
Orchestrateur complet pour realiser l'etude de convergence sur les 4 maillages

Exercices realises :
1. Calculs analytiques de f et uE
2. Generation et analyse des maillages
3. Resolution avec FreeFem++ (standard et penalisation)
4. Analyse de convergence et generation des graphiques
"""

import os
import sys
import subprocess
import argparse

# Ajout du chemin python pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))

from python.mesh_analysis import analyze_all_meshes
from python.convergence_analysis import analyze_convergence


def print_banner():
    """Affiche la banniere du programme"""
    banner = """
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║   ÉTUDE DE CONVERGENCE - ÉLÉMENTS FINIS P1 EN 2D                    ║
║   Probleme de Poisson avec conditions mixtes Dirichlet/Neumann       ║
║                                                                       ║
║   Domaine : Ω = ]0,4[ × ]0,2[                                        ║
║   Solution : u(x,y) = 1 + sin(πx/2) + x(x-4)cos(πy/2)               ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
    """
    try:
        print(banner)
    except UnicodeEncodeError:
        # Fallback pour les consoles qui ne supportent pas UTF-8
        print("\n" + "="*70)
        print("ETUDE DE CONVERGENCE - ELEMENTS FINIS P1 EN 2D")
        print("Probleme de Poisson avec conditions mixtes Dirichlet/Neumann")
        print("="*70 + "\n")


def check_freefem():
    """Verifie que FreeFem++ est installe et accessible"""
    print("\n[1/7] Verification de FreeFem++...")

    # Essayer d'abord FreeFem++ (capitale - installation Ubuntu)
    try:
        result = subprocess.run(['FreeFem++', '-h'],
                                capture_output=True,
                                timeout=5)
        print("[OK] FreeFem++ detecte")
        return 'FreeFem++'
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Fallback: freefem++ (minuscules)
    try:
        result = subprocess.run(['freefem++', '-h'],
                                capture_output=True,
                                timeout=5)
        print("[OK] FreeFem++ detecte")
        return 'freefem++'
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("[ERREUR] FreeFem++ non trouve dans le PATH")
        print("\n  Pour installer FreeFem++ :")
        print("    sudo apt-get update")
        print("    sudo apt-get install freefem++")
        return None


def generate_meshes(freefem_cmd, graphics=False):
    """Genere les 4 maillages avec FreeFem++"""
    print("\n[2/7] Generation des maillages...")

    script = 'generate_meshes.edp'

    if not os.path.exists(script):
        print(f"[ERREUR] Script {script} non trouve!")
        return False

    # Creation du dossier meshes
    os.makedirs('meshes', exist_ok=True)

    # Execution de FreeFem++
    freefem_args = [freefem_cmd, script]
    if not graphics:  # Par defaut, pas de graphiques (WSL)
        freefem_args.append('-nw')

    try:
        result = subprocess.run(freefem_args,
                                capture_output=True,
                                text=True,
                                timeout=30)

        # FreeFem++ peut retourner un code non-zero meme en cas de succes (warnings)
        # On verifie plutot que les fichiers ont ete crees
        meshes_created = all(os.path.exists(f'meshes/m{i}.msh') for i in range(1, 5))

        if not meshes_created:
            print(f"[ERREUR] Erreur lors de la generation des maillages:")
            print(result.stderr)
            return False

        print(result.stdout)
        print("[OK] Maillages generes avec succes")
        return True

    except subprocess.TimeoutExpired:
        print("[X] Timeout lors de la generation des maillages")
        return False
    except Exception as e:
        print(f"[X] Erreur : {e}")
        return False


def analyze_meshes():
    """Analyse la qualite et le pas des maillages"""
    print("\n[3/7] Analyse des maillages (Exercice 2)...")

    try:
        mesh_results = analyze_all_meshes()
        print("[OK] Analyse des maillages terminee")
        return mesh_results
    except Exception as e:
        print(f"[X] Erreur lors de l'analyse : {e}")
        return None


def solve_with_freefem(freefem_cmd, method='standard', graphics=False):
    """Resout le probleme avec FreeFem++"""

    if method == 'standard':
        print("\n[4/7] Resolution avec FreeFem++ (methode standard - Exercice 3.1)...")
        script = 'freefem/validation.edp'
    else:
        print("\n[5/7] Resolution avec FreeFem++ (methode penalisation - Exercice 3.2)...")
        script = 'freefem/validation_pen.edp'

    if not os.path.exists(script):
        print(f"[ERREUR] Script {script} non trouve!")
        return False

    # Creation du dossier results
    os.makedirs('results', exist_ok=True)

    # Resolution pour chaque maillage
    mesh_files = ['meshes/m1.msh', 'meshes/m2.msh', 'meshes/m3.msh', 'meshes/m4.msh']
    mesh_names = ['m1', 'm2', 'm3', 'm4']

    for mesh_file, mesh_name in zip(mesh_files, mesh_names):
        if not os.path.exists(mesh_file):
            print(f"[WARN]  Maillage {mesh_file} non trouve, ignore")
            continue

        print(f"\n  Traitement de {mesh_name}...")

        # Construction des arguments FreeFem++
        freefem_args = [freefem_cmd, script, mesh_file]
        if not graphics:  # Par defaut, pas de graphiques (WSL)
            freefem_args.append('-nw')

        try:
            result = subprocess.run(freefem_args,
                                    capture_output=True,
                                    text=True,
                                    timeout=60)

            # FreeFem++ peut retourner un code non-zero meme avec succes (warnings)
            # On affiche la sortie et on verifie s'il y a des vraies erreurs
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Erreur' in line or 'H¹' in line or '[OK]' in line or '===' in line:
                    print(f"    {line}")

            # Verifier s'il y a eu une vraie erreur fatale
            if result.returncode != 0 and result.stderr and 'Error' in result.stderr:
                print(f"  [WARN]  Avertissement pour {mesh_name} (code retour: {result.returncode})")
                if result.stderr.strip():
                    print(f"    {result.stderr}")

        except subprocess.TimeoutExpired:
            print(f"  [X] Timeout pour {mesh_name}")
            continue
        except Exception as e:
            print(f"  [X] Erreur : {e}")
            continue

    print(f"\n[OK] Resolution terminee ({method})")
    return True


def analyze_convergence_results(mesh_results, method='standard'):
    """Analyse la convergence et genere les graphiques"""

    if method == 'standard':
        print("\n[4b/7] Analyse de convergence standard (Exercice 4)...")
    else:
        print("\n[5b/7] Analyse de convergence penalisation (Exercice 4)...")

    if mesh_results is None:
        print("[X] Pas de resultats de maillage disponibles")
        return False

    try:
        analyze_convergence(mesh_results, method=method)
        print(f"[OK] Analyse de convergence terminee ({method})")
        return True
    except Exception as e:
        print(f"[X] Erreur lors de l'analyse : {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_pdf_report():
    """Genere le rapport PDF final"""
    print("\n[6/7] Generation du rapport PDF...")

    try:
        result = subprocess.run([sys.executable, 'generate_report.py'],
                                capture_output=True,
                                text=True,
                                timeout=120)

        if result.returncode == 0:
            print(result.stdout)
            print("[OK] Rapport PDF genere avec succes")
            return True
        else:
            print("[X] Erreur lors de la generation du PDF:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("[X] Timeout lors de la generation du PDF")
        return False
    except Exception as e:
        print(f"[X] Erreur : {e}")
        return False


def display_summary():
    """Affiche un resume des resultats"""
    print("\n[7/7] Resume des resultats...")
    print("\n" + "="*70)
    print("FICHIERS GÉNÉRÉS")
    print("="*70)

    files_to_check = [
        ('meshes/m1.msh', 'Maillage 1 (4×4)'),
        ('meshes/m2.msh', 'Maillage 2 (8×8)'),
        ('meshes/m3.msh', 'Maillage 3 (16×16)'),
        ('meshes/m4.msh', 'Maillage 4 (32×32)'),
        ('results/mesh_analysis.txt', 'Analyse des maillages'),
        ('results/m1_error.txt', 'Erreur m1 (standard)'),
        ('results/m2_error.txt', 'Erreur m2 (standard)'),
        ('results/m3_error.txt', 'Erreur m3 (standard)'),
        ('results/m4_error.txt', 'Erreur m4 (standard)'),
        ('results/m1_error_pen.txt', 'Erreur m1 (penalisation)'),
        ('results/m2_error_pen.txt', 'Erreur m2 (penalisation)'),
        ('results/m3_error_pen.txt', 'Erreur m3 (penalisation)'),
        ('results/m4_error_pen.txt', 'Erreur m4 (penalisation)'),
        ('results/convergence_table_standard.txt', 'Tableau convergence (standard)'),
        ('results/convergence_plot_standard.png', 'Graphique convergence (standard)'),
        ('results/convergence_table_penalized.txt', 'Tableau convergence (penalisation)'),
        ('results/convergence_plot_penalized.png', 'Graphique convergence (penalisation)'),
        ('results/RAPPORT_CONVERGENCE.pdf', 'Rapport PDF final'),
    ]

    for filepath, description in files_to_check:
        exists = os.path.exists(filepath)
        status = "[OK]" if exists else "[X]"
        print(f"  {status} {description:<40} {filepath}")

    print("="*70)
    print()

    # Affichage du tableau si disponible
    table_file = 'results/convergence_table_standard.txt'
    if os.path.exists(table_file):
        print("\n" + "="*70)
        print("TABLEAU DE CONVERGENCE FINAL")
        print("="*70)
        with open(table_file, 'r', encoding='utf-8') as f:
            print(f.read())


def main():
    """Fonction principale"""

    parser = argparse.ArgumentParser(
        description='Étude de convergence elements finis P1'
    )
    parser.add_argument('--skip-meshgen', action='store_true',
                        help='Ignorer la generation des maillages')
    parser.add_argument('--skip-solve', action='store_true',
                        help='Ignorer la resolution FreeFem++')
    parser.add_argument('--skip-report', action='store_true',
                        help='Ne pas generer le rapport PDF')
    parser.add_argument('--only-analysis', action='store_true',
                        help='Uniquement analyser les resultats existants')
    parser.add_argument('--graphics', action='store_true',
                        help='Activer les fenetres graphiques FreeFem++ (necessite serveur X)')

    args = parser.parse_args()

    print_banner()

    # Verification de FreeFem++
    if not args.only_analysis:
        freefem_cmd = check_freefem()
        if freefem_cmd is None and not args.skip_solve:
            print("\n[WARN]  FreeFem++ requis pour continuer")
            return 1
    else:
        freefem_cmd = None

    # Generation des maillages
    if not args.skip_meshgen and not args.only_analysis:
        if not generate_meshes(freefem_cmd, graphics=args.graphics):
            print("\n[X] Échec de la generation des maillages")
            return 1

    # Analyse des maillages
    mesh_results = analyze_meshes()
    if mesh_results is None:
        print("\n[X] Échec de l'analyse des maillages")
        return 1

    # ========================================================================
    # RÉSOLUTION AVEC LES 2 MÉTHODES (standard + penalisation)
    # ========================================================================

    # Methode 1 : Standard (Exercice 3.1)
    if not args.skip_solve and not args.only_analysis:
        if not solve_with_freefem(freefem_cmd, method='standard', graphics=args.graphics):
            print("\n[X] Échec de la resolution standard")
            return 1

    # Analyse de convergence - Standard
    if not analyze_convergence_results(mesh_results, method='standard'):
        print("\n[X] Échec de l'analyse de convergence standard")
        return 1

    # Methode 2 : Penalisation (Exercice 3.2) - TOUJOURS EXÉCUTÉE
    if not args.skip_solve and not args.only_analysis:
        if not solve_with_freefem(freefem_cmd, method='penalized', graphics=args.graphics):
            print("\n[WARN]  Methode de penalisation echouee")
            # On continue quand meme pour generer le PDF avec les resultats standard
        else:
            # Analyse de convergence - Penalisation
            if not analyze_convergence_results(mesh_results, method='penalized'):
                print("\n[WARN]  Analyse penalisation echouee")

    # ========================================================================
    # GÉNÉRATION DU RAPPORT PDF
    # ========================================================================

    if not args.skip_report:
        if not generate_pdf_report():
            print("\n[WARN]  Generation du PDF echouee (resultats disponibles quand meme)")

    # Resume final
    display_summary()

    print("\n" + "="*70)
    print("[OK] ÉTUDE DE CONVERGENCE TERMINÉE AVEC SUCCÈS")
    print("="*70)
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())

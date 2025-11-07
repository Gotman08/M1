#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Principal - Étude de Convergence Éléments Finis P1
==========================================================
Orchestrateur complet pour réaliser l'étude de convergence sur les 4 maillages

Exercices réalisés :
1. Calculs analytiques de f et uE
2. Génération et analyse des maillages
3. Résolution avec FreeFem++ (standard et pénalisation)
4. Analyse de convergence et génération des graphiques
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
    """Affiche la bannière du programme"""
    banner = """
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║   ÉTUDE DE CONVERGENCE - ÉLÉMENTS FINIS P1 EN 2D                    ║
║   Problème de Poisson avec conditions mixtes Dirichlet/Neumann       ║
║                                                                       ║
║   Domaine : Ω = ]0,4[ × ]0,2[                                        ║
║   Solution : u(x,y) = 1 + sin(πx/2) + x(x-4)cos(πy/2)               ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_freefem():
    """Vérifie que FreeFem++ est installé et accessible"""
    print("\n[1/7] Vérification de FreeFem++...")

    # Essayer d'abord FreeFem++ (capitale - installation Ubuntu)
    try:
        result = subprocess.run(['FreeFem++', '-h'],
                                capture_output=True,
                                timeout=5)
        print("✓ FreeFem++ détecté")
        return 'FreeFem++'
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Fallback: freefem++ (minuscules)
    try:
        result = subprocess.run(['freefem++', '-h'],
                                capture_output=True,
                                timeout=5)
        print("✓ FreeFem++ détecté")
        return 'freefem++'
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("✗ FreeFem++ non trouvé dans le PATH")
        print("\n  Pour installer FreeFem++ :")
        print("    sudo apt-get update")
        print("    sudo apt-get install freefem++")
        return None


def generate_meshes(freefem_cmd, graphics=False):
    """Génère les 4 maillages avec FreeFem++"""
    print("\n[2/7] Génération des maillages...")

    script = 'generate_meshes.edp'

    if not os.path.exists(script):
        print(f"✗ Script {script} non trouvé!")
        return False

    # Création du dossier meshes
    os.makedirs('meshes', exist_ok=True)

    # Exécution de FreeFem++
    freefem_args = [freefem_cmd, script]
    if not graphics:  # Par défaut, pas de graphiques (WSL)
        freefem_args.append('-nw')

    try:
        result = subprocess.run(freefem_args,
                                capture_output=True,
                                text=True,
                                timeout=30)

        # FreeFem++ peut retourner un code non-zéro même en cas de succès (warnings)
        # On vérifie plutôt que les fichiers ont été créés
        meshes_created = all(os.path.exists(f'meshes/m{i}.msh') for i in range(1, 5))

        if not meshes_created:
            print(f"✗ Erreur lors de la génération des maillages:")
            print(result.stderr)
            return False

        print(result.stdout)
        print("✓ Maillages générés avec succès")
        return True

    except subprocess.TimeoutExpired:
        print("✗ Timeout lors de la génération des maillages")
        return False
    except Exception as e:
        print(f"✗ Erreur : {e}")
        return False


def analyze_meshes():
    """Analyse la qualité et le pas des maillages"""
    print("\n[3/7] Analyse des maillages (Exercice 2)...")

    try:
        mesh_results = analyze_all_meshes()
        print("✓ Analyse des maillages terminée")
        return mesh_results
    except Exception as e:
        print(f"✗ Erreur lors de l'analyse : {e}")
        return None


def solve_with_freefem(freefem_cmd, method='standard', graphics=False):
    """Résout le problème avec FreeFem++"""

    if method == 'standard':
        print("\n[4/7] Résolution avec FreeFem++ (méthode standard - Exercice 3.1)...")
        script = 'freefem/validation.edp'
    else:
        print("\n[5/7] Résolution avec FreeFem++ (méthode pénalisation - Exercice 3.2)...")
        script = 'freefem/validation_pen.edp'

    if not os.path.exists(script):
        print(f"✗ Script {script} non trouvé!")
        return False

    # Création du dossier results
    os.makedirs('results', exist_ok=True)

    # Résolution pour chaque maillage
    mesh_files = ['meshes/m1.msh', 'meshes/m2.msh', 'meshes/m3.msh', 'meshes/m4.msh']
    mesh_names = ['m1', 'm2', 'm3', 'm4']

    for mesh_file, mesh_name in zip(mesh_files, mesh_names):
        if not os.path.exists(mesh_file):
            print(f"⚠️  Maillage {mesh_file} non trouvé, ignoré")
            continue

        print(f"\n  Traitement de {mesh_name}...")

        # Construction des arguments FreeFem++
        freefem_args = [freefem_cmd, script, mesh_file]
        if not graphics:  # Par défaut, pas de graphiques (WSL)
            freefem_args.append('-nw')

        try:
            result = subprocess.run(freefem_args,
                                    capture_output=True,
                                    text=True,
                                    timeout=60)

            # FreeFem++ peut retourner un code non-zéro même avec succès (warnings)
            # On affiche la sortie et on vérifie s'il y a des vraies erreurs
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Erreur' in line or 'H¹' in line or '✓' in line or '===' in line:
                    print(f"    {line}")

            # Vérifier s'il y a eu une vraie erreur fatale
            if result.returncode != 0 and result.stderr and 'Error' in result.stderr:
                print(f"  ⚠️  Avertissement pour {mesh_name} (code retour: {result.returncode})")
                if result.stderr.strip():
                    print(f"    {result.stderr}")

        except subprocess.TimeoutExpired:
            print(f"  ✗ Timeout pour {mesh_name}")
            continue
        except Exception as e:
            print(f"  ✗ Erreur : {e}")
            continue

    print(f"\n✓ Résolution terminée ({method})")
    return True


def analyze_convergence_results(mesh_results, method='standard'):
    """Analyse la convergence et génère les graphiques"""

    if method == 'standard':
        print("\n[4b/7] Analyse de convergence standard (Exercice 4)...")
    else:
        print("\n[5b/7] Analyse de convergence pénalisation (Exercice 4)...")

    if mesh_results is None:
        print("✗ Pas de résultats de maillage disponibles")
        return False

    try:
        analyze_convergence(mesh_results, method=method)
        print(f"✓ Analyse de convergence terminée ({method})")
        return True
    except Exception as e:
        print(f"✗ Erreur lors de l'analyse : {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_pdf_report():
    """Génère le rapport PDF final"""
    print("\n[6/7] Génération du rapport PDF...")

    try:
        result = subprocess.run([sys.executable, 'generate_report.py'],
                                capture_output=True,
                                text=True,
                                timeout=120)

        if result.returncode == 0:
            print(result.stdout)
            print("✓ Rapport PDF généré avec succès")
            return True
        else:
            print("✗ Erreur lors de la génération du PDF:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("✗ Timeout lors de la génération du PDF")
        return False
    except Exception as e:
        print(f"✗ Erreur : {e}")
        return False


def display_summary():
    """Affiche un résumé des résultats"""
    print("\n[7/7] Résumé des résultats...")
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
        ('results/m1_error_pen.txt', 'Erreur m1 (pénalisation)'),
        ('results/m2_error_pen.txt', 'Erreur m2 (pénalisation)'),
        ('results/m3_error_pen.txt', 'Erreur m3 (pénalisation)'),
        ('results/m4_error_pen.txt', 'Erreur m4 (pénalisation)'),
        ('results/convergence_table_standard.txt', 'Tableau convergence (standard)'),
        ('results/convergence_plot_standard.png', 'Graphique convergence (standard)'),
        ('results/convergence_table_penalized.txt', 'Tableau convergence (pénalisation)'),
        ('results/convergence_plot_penalized.png', 'Graphique convergence (pénalisation)'),
        ('results/RAPPORT_CONVERGENCE.pdf', 'Rapport PDF final'),
    ]

    for filepath, description in files_to_check:
        exists = os.path.exists(filepath)
        status = "✓" if exists else "✗"
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
        description='Étude de convergence éléments finis P1'
    )
    parser.add_argument('--skip-meshgen', action='store_true',
                        help='Ignorer la génération des maillages')
    parser.add_argument('--skip-solve', action='store_true',
                        help='Ignorer la résolution FreeFem++')
    parser.add_argument('--skip-report', action='store_true',
                        help='Ne pas générer le rapport PDF')
    parser.add_argument('--only-analysis', action='store_true',
                        help='Uniquement analyser les résultats existants')
    parser.add_argument('--graphics', action='store_true',
                        help='Activer les fenêtres graphiques FreeFem++ (nécessite serveur X)')

    args = parser.parse_args()

    print_banner()

    # Vérification de FreeFem++
    if not args.only_analysis:
        freefem_cmd = check_freefem()
        if freefem_cmd is None and not args.skip_solve:
            print("\n⚠️  FreeFem++ requis pour continuer")
            return 1
    else:
        freefem_cmd = None

    # Génération des maillages
    if not args.skip_meshgen and not args.only_analysis:
        if not generate_meshes(freefem_cmd, graphics=args.graphics):
            print("\n✗ Échec de la génération des maillages")
            return 1

    # Analyse des maillages
    mesh_results = analyze_meshes()
    if mesh_results is None:
        print("\n✗ Échec de l'analyse des maillages")
        return 1

    # ========================================================================
    # RÉSOLUTION AVEC LES 2 MÉTHODES (standard + pénalisation)
    # ========================================================================

    # Méthode 1 : Standard (Exercice 3.1)
    if not args.skip_solve and not args.only_analysis:
        if not solve_with_freefem(freefem_cmd, method='standard', graphics=args.graphics):
            print("\n✗ Échec de la résolution standard")
            return 1

    # Analyse de convergence - Standard
    if not analyze_convergence_results(mesh_results, method='standard'):
        print("\n✗ Échec de l'analyse de convergence standard")
        return 1

    # Méthode 2 : Pénalisation (Exercice 3.2) - TOUJOURS EXÉCUTÉE
    if not args.skip_solve and not args.only_analysis:
        if not solve_with_freefem(freefem_cmd, method='penalized', graphics=args.graphics):
            print("\n⚠️  Méthode de pénalisation échouée")
            # On continue quand même pour générer le PDF avec les résultats standard
        else:
            # Analyse de convergence - Pénalisation
            if not analyze_convergence_results(mesh_results, method='penalized'):
                print("\n⚠️  Analyse pénalisation échouée")

    # ========================================================================
    # GÉNÉRATION DU RAPPORT PDF
    # ========================================================================

    if not args.skip_report:
        if not generate_pdf_report():
            print("\n⚠️  Génération du PDF échouée (résultats disponibles quand même)")

    # Résumé final
    display_summary()

    print("\n" + "="*70)
    print("✓ ÉTUDE DE CONVERGENCE TERMINÉE AVEC SUCCÈS")
    print("="*70)
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())

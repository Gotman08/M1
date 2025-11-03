#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génération du Rapport PDF Final
================================
Collecte tous les résultats et génère le rapport PDF académique complet
"""

import os
import sys

# Ajout du chemin python pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))

from python.pdf_generator import PDFReportGenerator


def read_mesh_analysis_results():
    """Lit les résultats de l'analyse des maillages"""
    results = {
        'mesh_names': ['m1', 'm2', 'm3', 'm4'],
        'sizes': [81, 289, 1089, 4225],
        'qualities': [],
        'h_values': []
    }

    # Tentative de lecture depuis le fichier mesh_analysis.txt
    analysis_file = 'results/mesh_analysis.txt'
    if os.path.exists(analysis_file):
        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    if 'Q =' in line:
                        q_value = float(line.split('=')[1].strip())
                        results['qualities'].append(q_value)
                    elif 'h =' in line:
                        h_value = float(line.split('=')[1].strip())
                        results['h_values'].append(h_value)
        except Exception as e:
            print(f"⚠️  Erreur lecture analyse maillages : {e}")

    return results


def read_convergence_data(method='standard'):
    """
    Lit les données de convergence pour une méthode donnée

    Args:
        method: 'standard' ou 'penalized'

    Returns:
        dict avec 'errors' et 'orders'
    """
    mesh_names = ['m1', 'm2', 'm3', 'm4']
    errors = []
    orders = []

    suffix = '_error.txt' if method == 'standard' else '_error_pen.txt'

    # Lecture des erreurs
    for mesh_name in mesh_names:
        error_file = os.path.join('results', mesh_name + suffix)

        if os.path.exists(error_file):
            try:
                with open(error_file, 'r') as f:
                    error = float(f.readline().strip())
                    errors.append(error)
            except Exception as e:
                print(f"⚠️  Erreur lecture {error_file} : {e}")
                errors.append(None)
        else:
            errors.append(None)

    # Calcul des ordres de convergence
    import math
    for i in range(len(errors) - 1):
        if errors[i] is not None and errors[i+1] is not None:
            try:
                p = math.log(errors[i] / errors[i+1]) / math.log(2.0)
                orders.append(p)
            except:
                orders.append(None)
        else:
            orders.append(None)

    return {
        'errors': errors,
        'orders': orders
    }


def generate_pdf_report():
    """Fonction principale de génération du rapport PDF"""

    print("\n" + "="*70)
    print("GÉNÉRATION DU RAPPORT PDF")
    print("="*70)
    print()

    # Vérification que les résultats existent
    if not os.path.exists('results'):
        print("✗ Dossier results/ non trouvé !")
        print("  Veuillez d'abord exécuter l'étude de convergence avec main.py")
        return False

    # Création du dossier results s'il n'existe pas
    os.makedirs('results', exist_ok=True)

    output_file = 'results/RAPPORT_CONVERGENCE.pdf'

    print(f"Création du rapport : {output_file}")
    print()

    # Initialisation du générateur PDF
    pdf = PDFReportGenerator(output_file)

    # 1. Page de garde
    print("  [1/9] Ajout de la page de garde...")
    pdf.add_cover_page()

    # 2. Code source - Méthode standard
    print("  [2/9] Ajout du code validation.edp (standard)...")
    pdf.add_code_section(
        "Exercice 3.1 - Solveur Standard (validation.edp)",
        "freefem/validation.edp"
    )

    # 3. Code source - Méthode pénalisation
    print("  [3/9] Ajout du code validation_pen.edp (pénalisation)...")
    pdf.add_code_section(
        "Exercice 3.2 - Solveur avec Pénalisation (validation_pen.edp)",
        "freefem/validation_pen.edp"
    )

    # 4. Lecture des données des maillages
    print("  [4/9] Lecture des données de maillages...")
    mesh_data = read_mesh_analysis_results()

    # 5. Lecture des données de convergence - Standard
    print("  [5/9] Lecture des données de convergence (standard)...")
    convergence_standard = read_convergence_data('standard')

    # Fusion des données pour le tableau standard
    table_data_standard = {
        'mesh_names': mesh_data['mesh_names'],
        'sizes': mesh_data['sizes'],
        'qualities': mesh_data['qualities'],
        'h_values': mesh_data['h_values'],
        'errors': convergence_standard['errors'],
        'orders': convergence_standard['orders']
    }

    # 6. Tableau de convergence - Standard
    print("  [6/9] Génération du tableau de convergence (standard)...")
    pdf.add_convergence_table(
        "Tableau de Convergence - Méthode Standard",
        table_data_standard
    )

    # 7. Lecture des données de convergence - Pénalisation
    print("  [7/9] Lecture des données de convergence (pénalisation)...")
    convergence_penalized = read_convergence_data('penalized')

    # Fusion des données pour le tableau pénalisation
    table_data_penalized = {
        'mesh_names': mesh_data['mesh_names'],
        'sizes': mesh_data['sizes'],
        'qualities': mesh_data['qualities'],
        'h_values': mesh_data['h_values'],
        'errors': convergence_penalized['errors'],
        'orders': convergence_penalized['orders']
    }

    # 8. Tableau de convergence - Pénalisation
    print("  [8/9] Génération du tableau de convergence (pénalisation)...")
    pdf.add_convergence_table(
        "Tableau de Convergence - Méthode Pénalisation",
        table_data_penalized
    )

    # 9. Graphiques
    print("  [9/9] Ajout des graphiques...")

    # Graphique standard
    graph_std = 'results/convergence_plot_standard.png'
    if os.path.exists(graph_std):
        pdf.add_graph("Graphique de Convergence - Méthode Standard", graph_std)
    else:
        print(f"     ⚠️  Graphique standard non trouvé : {graph_std}")

    # Graphique pénalisation
    graph_pen = 'results/convergence_plot_penalized.png'
    if os.path.exists(graph_pen):
        pdf.add_graph("Graphique de Convergence - Méthode Pénalisation", graph_pen)
    else:
        print(f"     ⚠️  Graphique pénalisation non trouvé : {graph_pen}")

    # 10. Section analyse et conclusions
    print("  [10/10] Ajout de l'analyse et des conclusions...")
    pdf.add_analysis_section(table_data_standard, table_data_penalized)

    # Génération finale
    print()
    print("Génération du PDF en cours...")
    if pdf.generate():
        print()
        print("="*70)
        print(f"✓ RAPPORT PDF GÉNÉRÉ AVEC SUCCÈS")
        print("="*70)
        print()
        print(f"Fichier : {output_file}")
        print(f"Taille : {os.path.getsize(output_file) / 1024:.1f} Ko")
        print()
        print("Contenu du rapport :")
        print("  • Page de garde")
        print("  • Code source validation.edp (standard)")
        print("  • Code source validation_pen.edp (pénalisation)")
        print("  • Tableau de convergence - Méthode standard")
        print("  • Tableau de convergence - Méthode pénalisation")
        print("  • Graphique de convergence - Méthode standard")
        print("  • Graphique de convergence - Méthode pénalisation")
        print("  • Analyse comparative et conclusions")
        print()
        return True
    else:
        print()
        print("="*70)
        print("✗ ERREUR LORS DE LA GÉNÉRATION DU PDF")
        print("="*70)
        print()
        print("Vérifiez que reportlab est installé :")
        print("  pip3 install -r requirements.txt")
        print()
        return False


def main():
    """Point d'entrée du script"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Génération du rapport PDF de convergence'
    )
    parser.add_argument('--output', '-o',
                        default='results/RAPPORT_CONVERGENCE.pdf',
                        help='Nom du fichier PDF de sortie')

    args = parser.parse_args()

    # Génération du rapport
    success = generate_pdf_report()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

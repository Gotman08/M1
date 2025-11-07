#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse de convergence - Exercice 4
Calcul des ordres de convergence et generation du graphique
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import numpy as np
import matplotlib.pyplot as plt
from utils import compute_convergence_order


def read_errors(method='standard'):
    """
    Lecture des erreurs depuis les fichiers generes par FreeFem++

    Args:
        method: 'standard' ou 'penalized'

    Returns:
        Liste des erreurs [e1, e2, e3, e4]
    """
    mesh_names = ['m1', 'm2', 'm3', 'm4']
    errors = []

    suffix = '_error.txt' if method == 'standard' else '_error_pen.txt'

    for mesh_name in mesh_names:
        error_file = os.path.join('results', mesh_name + suffix)

        if not os.path.exists(error_file):
            print(f"Attention : fichier {error_file} non trouve")
            errors.append(None)
            continue

        with open(error_file, 'r') as f:
            line = f.readline().strip()
            try:
                error = float(line)
                errors.append(error)
            except ValueError:
                print(f"Erreur de lecture dans {error_file}")
                errors.append(None)

    return errors


def compute_convergence_orders(errors):
    """Calcul des ordres p_i = ln(e_i / e_{i+1}) / ln(2)"""
    orders = []

    for i in range(len(errors) - 1):
        if errors[i] is not None and errors[i+1] is not None:
            p = compute_convergence_order(errors[i], errors[i+1])
            orders.append(p)
        else:
            orders.append(None)

    return orders


def plot_convergence(h_values, errors, method='standard'):
    """
    Generation du graphique de convergence en log-log
    La pente donne l'ordre de convergence p
    """
    # Filtrer les valeurs None
    valid_indices = [i for i in range(len(errors)) if errors[i] is not None and h_values[i] is not None]
    h_valid = [h_values[i] for i in valid_indices]
    e_valid = [errors[i] for i in valid_indices]

    if len(h_valid) < 2:
        print("Pas assez de donnees pour le graphique")
        return

    # Conversion en log
    log_h = np.log(h_valid)
    log_e = np.log(e_valid)

    # Regression lineaire pour la pente
    coeffs = np.polyfit(log_h, log_e, 1)
    slope = coeffs[0]
    intercept = coeffs[1]

    # Creation du graphique
    plt.figure(figsize=(10, 7))

    # Points de donnees
    plt.loglog(h_valid, e_valid, 'o-', linewidth=2, markersize=10,
               label=f'Erreur eh ({method})')

    # Droite de regression
    h_fit = np.array([min(h_valid), max(h_valid)])
    e_fit = np.exp(intercept) * h_fit**slope
    plt.loglog(h_fit, e_fit, '--', linewidth=1.5,
               label=f'Regression : eh ~ C h^{slope:.4f}')

    # Droites de reference
    h_ref = np.array([min(h_valid), max(h_valid)])

    # Ordre 1 (theorique)
    C1 = e_valid[0] / h_valid[0]
    e_order1 = C1 * h_ref
    plt.loglog(h_ref, e_order1, ':', color='gray', linewidth=1,
               label='Ordre 1 (theorique)')

    # Ordre 2 (super-convergence)
    C2 = e_valid[0] / (h_valid[0]**2)
    e_order2 = C2 * h_ref**2
    plt.loglog(h_ref, e_order2, ':', color='green', linewidth=1,
               label='Ordre 2 (super-convergence)')

    plt.xlabel('Pas du maillage h', fontsize=12)
    plt.ylabel('Erreur H1 semi-norme', fontsize=12)
    plt.title(f'Courbe de Convergence - Methode {method}\n' +
              f'Pente observee : p = {slope:.4f}',
              fontsize=14)
    plt.grid(True, which='both', linestyle='--', alpha=0.6)
    plt.legend(fontsize=10)
    plt.tight_layout()

    # Sauvegarde
    output_file = f'results/convergence_plot_{method}.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Graphique sauvegarde : {output_file}")

    plt.close()


def generate_convergence_table(h_values, Q_values, errors, orders, method='standard'):
    """Generation du tableau de convergence formate"""
    mesh_names = ['m1.msh', 'm2.msh', 'm3.msh', 'm4.msh']
    sizes = [25, 81, 289, 1089]  # tailles : 5x5, 9x9, 17x17, 33x33

    print("\n" + "="*90)
    print(f"TABLEAU DE CONVERGENCE - Methode {method.upper()}")
    print("="*90)
    print()

    # En-tete
    print(f"{'Maillage':<12} {'Taille N':<12} {'Qualite Q':<20} {'Pas h':<20} {'eh (16 dec.)':<22} {'Ordre p':<12}")
    print("-"*90)

    # Lignes de donnees
    for i, mesh_name in enumerate(mesh_names):
        N = sizes[i]
        Q = Q_values[i] if Q_values[i] is not None else float('nan')
        h = h_values[i] if h_values[i] is not None else float('nan')
        e = errors[i] if errors[i] is not None else float('nan')

        Q_str = f"{Q:.16f}" if not np.isnan(Q) else "N/A"
        h_str = f"{h:.16f}" if not np.isnan(h) else "N/A"
        e_str = f"{e:.16e}" if not np.isnan(e) else "N/A"

        print(f"{mesh_name:<12} {N:<12} {Q_str:<20} {h_str:<20} {e_str:<22}", end='')

        # Ordre de convergence (sauf pour le dernier)
        if i < len(orders) and orders[i] is not None:
            print(f" {orders[i]:.16f}")
        else:
            print()

    print("-"*90)

    # Calcul des rapports
    print("\nOrdres de convergence (4 decimales) :")
    print("-"*50)

    for i in range(len(orders)):
        if orders[i] is not None:
            print(f"ln(e{i+1}/e{i+2})/ln(2) = {orders[i]:.4f}")
        else:
            print(f"ln(e{i+1}/e{i+2})/ln(2) = N/A")

    print("="*90)
    print()

    # Sauvegarde du tableau
    output_file = f'results/convergence_table_{method}.txt'

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*90 + "\n")
        f.write(f"TABLEAU DE CONVERGENCE - Methode {method.upper()}\n")
        f.write("="*90 + "\n\n")

        f.write(f"{'Maillage':<12} {'Taille N':<12} {'Qualite Q':<20} {'Pas h':<20} {'eh (16 dec.)':<22} {'Ordre p':<12}\n")
        f.write("-"*90 + "\n")

        for i, mesh_name in enumerate(mesh_names):
            N = sizes[i]
            Q = Q_values[i] if Q_values[i] is not None else float('nan')
            h = h_values[i] if h_values[i] is not None else float('nan')
            e = errors[i] if errors[i] is not None else float('nan')

            Q_str = f"{Q:.16f}" if not np.isnan(Q) else "N/A"
            h_str = f"{h:.16f}" if not np.isnan(h) else "N/A"
            e_str = f"{e:.16e}" if not np.isnan(e) else "N/A"

            f.write(f"{mesh_name:<12} {N:<12} {Q_str:<20} {h_str:<20} {e_str:<22}")

            if i < len(orders) and orders[i] is not None:
                f.write(f" {orders[i]:.16f}\n")
            else:
                f.write("\n")

        f.write("-"*90 + "\n\n")

        f.write("Ordres de convergence (4 decimales) :\n")
        f.write("-"*50 + "\n")

        for i in range(len(orders)):
            if orders[i] is not None:
                f.write(f"ln(e{i+1}/e{i+2})/ln(2) = {orders[i]:.4f}\n")
            else:
                f.write(f"ln(e{i+1}/e{i+2})/ln(2) = N/A\n")

        f.write("="*90 + "\n")

    print(f"Tableau sauvegarde : {output_file}\n")


def analyze_convergence(mesh_analysis_results, method='standard'):
    """
    Analyse complete de convergence

    Args:
        mesh_analysis_results: Resultats de l'analyse des maillages
        method: 'standard' ou 'penalized'
    """
    print("\n" + "="*70)
    print(f"ANALYSE DE CONVERGENCE - Exercice 4 ({method.upper()})")
    print("="*70)
    print()

    # Extraction h et Q
    h_values = [res['h'] for res in mesh_analysis_results]
    Q_values = [res['Q'] for res in mesh_analysis_results]

    # Lecture des erreurs
    print("Lecture des erreurs...")
    errors = read_errors(method)
    print(f"Erreurs lues : {errors}\n")

    # Calcul des ordres
    print("Calcul des ordres de convergence...")
    orders = compute_convergence_orders(errors)
    print(f"Ordres calcules : {orders}\n")

    # Generation du tableau
    generate_convergence_table(h_values, Q_values, errors, orders, method)

    # Generation du graphique
    print("Generation du graphique de convergence...")
    plot_convergence(h_values, errors, method)

    print("\nAnalyse de convergence terminee\n")

    # Commentaire sur la super-convergence
    valid_orders = [o for o in orders if o is not None]
    if valid_orders:
        avg_order = np.mean(valid_orders)
        print("="*70)
        print("COMMENTAIRE SUR LA CONVERGENCE")
        print("="*70)
        print(f"Ordre moyen observe : p ~ {avg_order:.4f}")
        print()

        if avg_order > 1.5:
            print("SUPER-CONVERGENCE OBSERVEE")
            print("  L'ordre de convergence est superieur a 1 (ordre theorique).")
            print("  Ce phenomene est typique pour les elements finis P1 sur")
            print("  maillages structures avec solutions regulieres.")
        elif avg_order > 0.9:
            print("Convergence conforme a la theorie (p ~ 1)")
            print("  L'erreur en semi-norme H1 decroit comme O(h).")
        else:
            print("Attention : ordre de convergence sous-optimal (p < 1)")
            print("  Verifier l'implementation et les conditions aux limites.")

        print("="*70)
        print()


if __name__ == "__main__":
    # Exemple d'utilisation
    from mesh_analysis import analyze_all_meshes

    mesh_results = analyze_all_meshes()
    analyze_convergence(mesh_results, method='standard')

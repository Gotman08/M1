#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXERCICE 6 : Analyse de convergence numerique
==============================================
Calcul des erreurs e_h et des ordres de convergence p sur les 4 maillages

Recalcule les colonnes "e_h" et "ordre p" dans un nouveau tableau issu
du programme validation_pen.py ecrit en Python.

Usage:
    python exercice6_convergence.py
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Ajout du chemin pour importer validation_pen
sys.path.insert(0, os.path.dirname(__file__))

from validation_pen import main as solve_fem


def analyze_convergence(mesh_files):
    """
    Analyse de convergence sur plusieurs maillages

    Args:
        mesh_files: Liste des fichiers maillages (m1.msh, m2.msh, m3.msh, m4.msh)

    Returns:
        dict avec les resultats de convergence
    """
    results = []

    print("\n" + "="*80)
    print("EXERCICE 6 : ANALYSE DE CONVERGENCE NUMERIQUE")
    print("="*80)

    # Resolution sur chaque maillage
    for i, mesh_file in enumerate(mesh_files, 1):
        print(f"\n[{i}/{len(mesh_files)}] Resolution sur {mesh_file}...")

        if not os.path.exists(mesh_file):
            print(f"   ERREUR: Maillage {mesh_file} non trouve!")
            continue

        # Resolution EF-P1
        result = solve_fem(mesh_file, verbose=False)

        results.append({
            'mesh': mesh_file,
            'nv': result['nv'],
            'nt': result['nt'],
            'h': result['h'],
            'Q': result['Q'],
            'error_H1': result['error_H1']
        })

        print(f"   N = {result['nv']}, h = {result['h']:.6f}, e_h = {result['error_H1']:.6e}")

    return results


def compute_convergence_orders(results):
    """
    Calcul des ordres de convergence : p = ln(e_h / e_{h/2}) / ln(2)

    Args:
        results: Liste des resultats de convergence

    Returns:
        Liste des ordres de convergence
    """
    orders = []

    for i in range(len(results) - 1):
        e_h = results[i]['error_H1']
        e_h2 = results[i+1]['error_H1']
        h1 = results[i]['h']
        h2 = results[i+1]['h']

        # Ordre de convergence
        p = np.log(e_h / e_h2) / np.log(h1 / h2)
        orders.append(p)

    return orders


def generate_convergence_table(results, orders, output_file=None):
    """
    Generate tableau de convergence formate

    Args:
        results: Liste des resultats de convergence
        orders: Liste des ordres de convergence
        output_file: Fichier de sortie (optionnel)

    Returns:
        str: Tableau formate
    """
    table = []
    table.append("="*100)
    table.append("TABLEAU DE CONVERGENCE - EXERCICE 6 (Python validation_pen.py)")
    table.append("="*100)
    table.append("")

    # En-tete
    header = f"{'Maillage':<15} {'N sommets':<12} {'Q':<20} {'h':<20} {'e_h (H1)':<20} {'Ordre p':<15}"
    table.append(header)
    table.append("-"*100)

    # Lignes de donnees
    for i, res in enumerate(results):
        mesh_name = os.path.basename(res['mesh'])
        nv = res['nv']
        Q = res['Q']
        h = res['h']
        error = res['error_H1']

        if i < len(orders):
            order = orders[i]
            line = f"{mesh_name:<15} {nv:<12} {Q:<20.16f} {h:<20.16f} {error:<20.16e} {order:<15.10f}"
        else:
            line = f"{mesh_name:<15} {nv:<12} {Q:<20.16f} {h:<20.16f} {error:<20.16e} {'-':<15}"

        table.append(line)

    table.append("-"*100)
    table.append("")

    # Ordres de convergence
    table.append("Ordres de convergence (10 decimales) :")
    table.append("-"*50)
    for i, p in enumerate(orders):
        table.append(f"ln(e{i+1}/e{i+2})/ln(h{i+1}/h{i+2}) = {p:.10f}")

    # Ordre moyen
    if orders:
        p_mean = np.mean(orders)
        table.append("")
        table.append(f"Ordre moyen : p ~ {p_mean:.4f}")

        # Commentaire
        table.append("")
        if 0.9 <= p_mean <= 1.1:
            table.append("Convergence conforme a la theorie (p ~ 1)")
            table.append("  L'erreur en semi-norme H1 decroit comme O(h).")
        elif 1.9 <= p_mean <= 2.1:
            table.append("Super-convergence observee (p ~ 2)")
            table.append("  Possible sur maillages structures uniformes.")
        else:
            table.append(f"Ordre de convergence inattendu : p ~ {p_mean:.2f}")

    table.append("="*100)

    table_str = "\n".join(table)

    # Sauvegarde dans fichier
    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(table_str)
        print(f"\nTableau sauvegarde : {output_file}")

    return table_str


def plot_convergence(results, orders, output_file=None):
    """
    Graphique de convergence log-log

    Args:
        results: Liste des resultats de convergence
        orders: Liste des ordres de convergence
        output_file: Fichier de sortie (optionnel)
    """
    # Extraction des donnees
    h_values = np.array([res['h'] for res in results])
    error_values = np.array([res['error_H1'] for res in results])

    # Creation du graphique
    plt.figure(figsize=(10, 7))

    # Points de convergence
    plt.loglog(h_values, error_values, 'o-', linewidth=2, markersize=10,
               label='Erreur mesuree $e_h$', color='blue')

    # Droite theorique O(h)
    h_ref = h_values[0]
    e_ref = error_values[0]
    h_theory = np.array([h_ref, h_values[-1]])
    e_theory_h1 = e_ref * (h_theory / h_ref)**1.0
    plt.loglog(h_theory, e_theory_h1, '--', linewidth=2,
               label='Theorie O(h) - P1', color='red', alpha=0.7)

    # Droite theorique O(h²)
    e_theory_h2 = e_ref * (h_theory / h_ref)**2.0
    plt.loglog(h_theory, e_theory_h2, ':', linewidth=2,
               label='Super-convergence O(h²)', color='green', alpha=0.7)

    # Labels et titre
    plt.xlabel('Pas de maillage h', fontsize=12)
    plt.ylabel('Erreur $|u_h - r_h(u)|_{H^1}$', fontsize=12)
    plt.title('Convergence numerique - Exercice 6 (Python validation_pen.py)', fontsize=14, fontweight='bold')
    plt.grid(True, which='both', alpha=0.3)
    plt.legend(fontsize=11)

    # Annotation de l'ordre moyen
    if orders:
        p_mean = np.mean(orders)
        plt.text(0.05, 0.95, f'Ordre moyen: p $\\approx$ {p_mean:.2f}',
                transform=plt.gca().transAxes,
                fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()

    # Sauvegarde
    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"Graphique sauvegarde : {output_file}")

    plt.close()


def main():
    """Fonction principale"""

    # Liste des maillages
    mesh_files = [
        'meshes/m1.msh',
        'meshes/m2.msh',
        'meshes/m3.msh',
        'meshes/m4.msh'
    ]

    # Analyse de convergence
    results = analyze_convergence(mesh_files)

    if not results:
        print("\nERREUR: Aucun resultat obtenu!")
        return 1

    # Calcul des ordres de convergence
    print("\n" + "="*80)
    print("CALCUL DES ORDRES DE CONVERGENCE")
    print("="*80)

    orders = compute_convergence_orders(results)

    for i, p in enumerate(orders):
        print(f"  p_{i+1} = ln(e_{i+1}/e_{i+2})/ln(h_{i+1}/h_{i+2}) = {p:.10f}")

    if orders:
        p_mean = np.mean(orders)
        print(f"\n  Ordre moyen : p ~ {p_mean:.4f}")

    # Generation du tableau
    print("\n" + "="*80)
    print("GENERATION DU TABLEAU")
    print("="*80)

    output_table = 'results/exercice6_table.txt'
    table_str = generate_convergence_table(results, orders, output_table)
    print("\n" + table_str)

    # Generation du graphique
    print("\n" + "="*80)
    print("GENERATION DU GRAPHIQUE")
    print("="*80)

    output_plot = 'results/exercice6_plot.png'
    plot_convergence(results, orders, output_plot)

    # Resume final
    print("\n" + "="*80)
    print("EXERCICE 6 TERMINE")
    print("="*80)
    print(f"\nFichiers generes :")
    print(f"  - Tableau  : {output_table}")
    print(f"  - Graphique: {output_plot}")

    if orders:
        p_mean = np.mean(orders)
        if 0.9 <= p_mean <= 1.1:
            print(f"\n[OK] Resultats convenables : ordre de convergence p ~ {p_mean:.2f} ~ 1")
            print("  Conforme a la theorie pour des elements P1.")
        elif 1.8 <= p_mean <= 2.2:
            print(f"\n[OK] Super-convergence observee : p ~ {p_mean:.2f} ~ 2")
            print("  Possible sur maillages structures uniformes.")
        else:
            print(f"\n[WARN] Ordre de convergence inattendu : p ~ {p_mean:.2f}")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())

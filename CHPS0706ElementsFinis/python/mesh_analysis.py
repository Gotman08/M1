#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse des maillages - Exercice 2
Calcul de la qualite Q et du pas h pour les 4 maillages
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from utils import read_freefem_mesh, compute_mesh_characteristics


def analyze_all_meshes():
    """Analyse les 4 maillages et affiche les resultats"""
    mesh_files = ['m1.msh', 'm2.msh', 'm3.msh', 'm4.msh']
    mesh_names = ['m1', 'm2', 'm3', 'm4']
    expected_sizes = [25, 81, 289, 1089]  # tailles selon l'enonce du TP

    results = []

    print("="*70)
    print("ANALYSE DES MAILLAGES - Exercice 2")
    print("="*70)
    print()

    for i, (mesh_file, mesh_name, expected_nv) in enumerate(zip(mesh_files, mesh_names, expected_sizes)):
        mesh_path = os.path.join('meshes', mesh_file)

        if not os.path.exists(mesh_path):
            print(f"Attention : fichier {mesh_file} non trouve!")
            results.append({
                'name': mesh_name,
                'N': expected_nv,
                'Q': None,
                'h': None
            })
            continue

        # Lecture du maillage
        mesh_data = read_freefem_mesh(mesh_path)

        # Calcul Q et h
        Q_max, h = compute_mesh_characteristics(mesh_data)

        results.append({
            'name': mesh_name,
            'N': mesh_data['nv'],
            'Q': Q_max,
            'h': h
        })

        print(f"Maillage {mesh_name}.msh:")
        print(f"  - Taille N        : {mesh_data['nv']} sommets")
        print(f"  - Triangles       : {mesh_data['nt']}")
        print(f"  - Qualite Q       : {Q_max:.16f}")
        print(f"  - Pas h           : {h:.16f}")
        print()

    # Sauvegarde
    output_file = os.path.join('results', 'mesh_analysis.txt')
    os.makedirs('results', exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("ANALYSE DES MAILLAGES\n")
        f.write("="*70 + "\n\n")

        for res in results:
            if res['Q'] is not None:
                f.write(f"{res['name']}.msh:\n")
                f.write(f"  N = {res['N']}\n")
                f.write(f"  Q = {res['Q']:.16f}\n")
                f.write(f"  h = {res['h']:.16f}\n\n")

    print(f"Resultats sauvegardes dans {output_file}")

    return results


if __name__ == "__main__":
    analyze_all_meshes()

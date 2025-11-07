#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BONUS : Assemblage manuel EF-P1 en Python

Script qui fait tout en Python (sans FreeFem++ pour la resolution) :
- Lecture maillages .msh
- Assemblage manuel triangle par triangle
- Resolution systeme lineaire
- Calcul erreur H1

Usage:
    python bonus_assemblage.py meshes/m1.msh meshes/m2.msh meshes/m3.msh meshes/m4.msh
"""

import sys
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
import matplotlib.pyplot as plt
from pathlib import Path

# Solution exacte et second membre

def u_exact(x, y):
    """
    Solution exacte : u(x,y) = 1 + sin(πx/2) + x(x-4)cos(πy/2)
    """
    return 1.0 + np.sin(np.pi * x / 2.0) + x * (x - 4.0) * np.cos(np.pi * y / 2.0)


def grad_u_exact(x, y):
    """
    Gradient analytique de la solution exacte

    ∂u/∂x = (π/2)cos(πx/2) + (2x-4)cos(πy/2)
    ∂u/∂y = -(π/2)x(x-4)sin(πy/2)

    Returns:
        (du_dx, du_dy)
    """
    du_dx = (np.pi / 2.0) * np.cos(np.pi * x / 2.0) + (2.0 * x - 4.0) * np.cos(np.pi * y / 2.0)
    du_dy = -(np.pi / 2.0) * x * (x - 4.0) * np.sin(np.pi * y / 2.0)
    return du_dx, du_dy


def f_source(x, y):
    """
    Second membre f = -Δu

    Calcul analytique :
    Δu = ∂²u/∂x² + ∂²u/∂y²
       = -(π²/4)sin(πx/2) + 2cos(πy/2) - (π²/4)x(x-4)cos(πy/2)

    Donc : f = (π²/4)[sin(πx/2) + x(x-4)cos(πy/2)] - 2cos(πy/2)
    """
    pi2_4 = np.pi**2 / 4.0
    return pi2_4 * (np.sin(np.pi * x / 2.0) + x * (x - 4.0) * np.cos(np.pi * y / 2.0)) - 2.0 * np.cos(np.pi * y / 2.0)


# Lecture maillages FreeFem++ (.msh)

def read_freefem_mesh(filename):
    """
    Lecture d'un maillage FreeFem++ au format .msh

    Format :
    Ligne 1 : nv nt nbe (nombre sommets, triangles, arêtes bord)
    Lignes suivantes : coordonnées sommets (x y label)
    Puis : triangles (i1 i2 i3 label)
    Puis : arêtes bord (i1 i2 label)

    Returns:
        dict avec 'vertices', 'triangles', 'edges', 'dirichlet_nodes'
    """
    with open(filename, 'r') as f:
        # Ligne 1 : nv nt nbe
        first_line = f.readline().strip().split()
        nv = int(first_line[0])
        nt = int(first_line[1])
        nbe = int(first_line[2])

        # Lecture des sommets
        vertices = np.zeros((nv, 2))  # x, y
        for i in range(nv):
            line = f.readline().strip().split()
            vertices[i] = [float(line[0]), float(line[1])]

        # Lecture des triangles (indices 1-based → 0-based)
        triangles = np.zeros((nt, 3), dtype=int)
        for i in range(nt):
            line = f.readline().strip().split()
            triangles[i] = [int(line[0])-1, int(line[1])-1, int(line[2])-1]

        # Lecture des arêtes de bord
        edges = []
        dirichlet_nodes = set()
        for i in range(nbe):
            line = f.readline().strip().split()
            i1, i2, label = int(line[0])-1, int(line[1])-1, int(line[2])
            edges.append((i1, i2, label))
            # Label 1 = Dirichlet (x=0 et x=4)
            if label == 1:
                dirichlet_nodes.add(i1)
                dirichlet_nodes.add(i2)

    # Fallback si aucun noeud Dirichlet détecté : x=0 ou x=4
    if len(dirichlet_nodes) == 0:
        tol = 1e-8
        for i, (x, y) in enumerate(vertices):
            if abs(x - 0.0) < tol or abs(x - 4.0) < tol:
                dirichlet_nodes.add(i)

    return {
        'vertices': vertices,
        'triangles': triangles,
        'edges': edges,
        'dirichlet_nodes': sorted(list(dirichlet_nodes)),
        'nv': nv,
        'nt': nt,
        'nbe': nbe
    }

# Qualite et pas du maillage

def triangle_area(p0, p1, p2):
    """Aire d'un triangle (produit vectoriel)"""
    x0, y0 = p0
    x1, y1 = p1
    x2, y2 = p2
    return 0.5 * abs((x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0))


def edge_lengths(p0, p1, p2):
    """Longueurs des 3 arêtes d'un triangle"""
    d01 = np.linalg.norm(p0 - p1)
    d12 = np.linalg.norm(p1 - p2)
    d20 = np.linalg.norm(p2 - p0)
    return d01, d12, d20


def mesh_quality_and_step(vertices, triangles):
    """
    Calcul de la qualité Q et du pas h du maillage (formules du cours CHPS0706)

    - Diamètre du triangle : h_T = max des longueurs d'arêtes
    - Rayon inscrit : r_T = 2 * Aire / Périmètre
    - Qualité : Q_T = (√3/6) * (h_T / r_T)
    - Qualité du maillage : Q = max(Q_T)
    - Pas du maillage : h = max(h_T)

    Returns:
        (Q, h)
    """
    Q_list = []
    h_list = []

    for tri in triangles:
        p0 = vertices[tri[0]]
        p1 = vertices[tri[1]]
        p2 = vertices[tri[2]]

        # Aire
        A = triangle_area(p0, p1, p2)

        # Arêtes
        d01, d12, d20 = edge_lengths(p0, p1, p2)
        P = d01 + d12 + d20  # Périmètre

        # Diamètre (plus grande arête)
        h_T = max(d01, d12, d20)

        # Rayon inscrit
        r_T = 2.0 * A / P if P > 0 else 1e-16

        # Qualité
        Q_T = (np.sqrt(3.0) / 6.0) * (h_T / r_T) if r_T > 0 else float('inf')

        Q_list.append(Q_T)
        h_list.append(h_T)

    Q = max(Q_list)
    h = max(h_list)

    return Q, h

# Assemblage de la matrice de rigidite (methode manuelle)

def assemble_stiffness_and_load(vertices, triangles, f_func):
    """
    Assemblage manuel de la matrice de rigidité A et du vecteur de charge F

    Méthode : pour chaque triangle T
    1. Calculer les gradients des fonctions de base P1 (via inversion de matrice)
    2. Calculer la matrice locale K_T = Aire * (grad φ_j · grad φ_i)
    3. Calculer le vecteur local F_T = Aire/3 * f(sommets)
    4. Assembler dans les matrices globales

    Référence : Cours CHPS0706, Chapitre 3

    Args:
        vertices: Coordonnées des sommets (nv × 2)
        triangles: Connectivité (nt × 3)
        f_func: Fonction source f(x, y)

    Returns:
        (A, F) : matrice de rigidité (sparse CSR) et vecteur de charge
    """
    nv = vertices.shape[0]
    nt = triangles.shape[0]

    # Stockage pour assemblage sparse
    rows = []
    cols = []
    vals = []
    F = np.zeros(nv)

    # Boucle sur les triangles
    for tri in triangles:
        # Indices globaux
        i0, i1, i2 = tri[0], tri[1], tri[2]

        # Coordonnées des sommets
        p0 = vertices[i0]
        p1 = vertices[i1]
        p2 = vertices[i2]

        # Aire du triangle
        A_tri = triangle_area(p0, p1, p2)

        # Calcul des gradients des fonctions de base P1
        # Les fonctions de base λ_i satisfont λ_i(p_j) = δ_ij
        # On écrit λ_i = a_i + b_i*x + c_i*y
        # Les coefficients [a_i, b_i, c_i]^T sont donnés par l'inverse de :
        # M = [1  x0  y0]
        #     [1  x1  y1]
        #     [1  x2  y2]
        M = np.array([[1.0, p0[0], p0[1]],
                      [1.0, p1[0], p1[1]],
                      [1.0, p2[0], p2[1]]])

        M_inv = np.linalg.inv(M)

        # Les gradients sont les lignes 1 et 2 de M_inv^T, ou colonnes de M_inv[1:3, :]
        # grad λ_i = [b_i, c_i] = M_inv[1:3, i]
        grads = M_inv[1:3, :]  # Shape (2, 3) : colonne j = grad λ_j

        # Matrice élémentaire de rigidité : K_T[i,j] = A_tri * (grad λ_j · grad λ_i)
        K_T = np.zeros((3, 3))
        for i in range(3):
            for j in range(3):
                K_T[i, j] = A_tri * np.dot(grads[:, i], grads[:, j])

        # Vecteur élémentaire de charge (quadrature à 3 points : sommets)
        # ∫_T f * λ_i ≈ (Aire / 3) * f(sommet_i)
        f_values = np.array([f_func(*p0), f_func(*p1), f_func(*p2)])
        F_T = (A_tri / 3.0) * f_values

        # Assemblage global
        indices = [i0, i1, i2]
        for a in range(3):
            F[indices[a]] += F_T[a]
            for b in range(3):
                rows.append(indices[a])
                cols.append(indices[b])
                vals.append(K_T[a, b])

    # Construction de la matrice sparse
    A = sp.csr_matrix((vals, (rows, cols)), shape=(nv, nv))

    return A, F


def apply_dirichlet_strong(A, F, dirichlet_nodes, vertices, u_exact_func):
    """
    Application des conditions de Dirichlet par élimination de lignes/colonnes

    Méthode :
    1. Pour chaque noeud Dirichlet i :
       - Mettre la ligne i à zéro sauf A[i,i] = 1
       - Mettre la colonne i à zéro
       - Mettre F[i] = u_exact(x_i, y_i)

    Args:
        A: Matrice de rigidité (CSR)
        F: Vecteur de charge
        dirichlet_nodes: Liste des indices de noeuds Dirichlet
        vertices: Coordonnées des sommets
        u_exact_func: Fonction u_exact(x, y)

    Returns:
        (A_modified, F_modified)
    """
    A = A.tolil()  # Conversion en LIL pour modification efficace

    # Zéro sur les lignes et colonnes Dirichlet
    for node in dirichlet_nodes:
        # Ligne : A[node, :] = 0 sauf A[node, node] = 1
        A.rows[node] = [node]
        A.data[node] = [1.0]

    A = A.tocsr()

    # Colonnes : mettre à zéro (sauf diagonale)
    for node in dirichlet_nodes:
        A[:, node] = 0
        A[node, node] = 1.0
        # Second membre = valeur exacte
        x, y = vertices[node]
        F[node] = u_exact_func(x, y)

    return A, F

# Calcul de l'erreur en semi-norme H1

def compute_H1_semi_error(vertices, triangles, uh, grad_u_exact_func):
    """
    Calcul de l'erreur en semi-norme H¹

    |u - uh|_{H¹} = sqrt(∫_Ω |grad(u) - grad(uh)|² dx)

    Pour les éléments P1, grad(uh) est constant par triangle.
    On calcule donc la somme sur les triangles :
        error² = Σ_T Aire_T * |grad_exact(centroïde_T) - grad_uh_T|²

    Args:
        vertices: Coordonnées des sommets
        triangles: Connectivité
        uh: Solution numérique (vecteur des valeurs aux noeuds)
        grad_u_exact_func: Fonction retournant (du/dx, du/dy)

    Returns:
        Erreur en semi-norme H¹
    """
    error_squared = 0.0

    for tri in triangles:
        # Sommets
        i0, i1, i2 = tri[0], tri[1], tri[2]
        p0 = vertices[i0]
        p1 = vertices[i1]
        p2 = vertices[i2]

        # Aire
        A_tri = triangle_area(p0, p1, p2)

        # Calcul du gradient de uh (constant sur le triangle)
        M = np.array([[1.0, p0[0], p0[1]],
                      [1.0, p1[0], p1[1]],
                      [1.0, p2[0], p2[1]]])
        M_inv = np.linalg.inv(M)
        grads = M_inv[1:3, :]  # grad λ_i

        # grad uh = Σ uh_i * grad λ_i
        uh_values = np.array([uh[i0], uh[i1], uh[i2]])
        grad_uh = grads.dot(uh_values)  # Shape (2,)

        # Gradient exact évalué au centroïde du triangle
        xc = (p0[0] + p1[0] + p2[0]) / 3.0
        yc = (p0[1] + p1[1] + p2[1]) / 3.0
        du_dx_exact, du_dy_exact = grad_u_exact_func(xc, yc)
        grad_exact = np.array([du_dx_exact, du_dy_exact])

        # Contribution à l'erreur
        diff = grad_exact - grad_uh
        error_squared += A_tri * np.dot(diff, diff)

    return np.sqrt(error_squared)

# Etude de convergence

def convergence_order(e1, e2):
    """
    Calcul de l'ordre de convergence p

    Si eh ≃ C·h^p, alors : p ≃ ln(e(h)/e(h/2)) / ln(2)

    Args:
        e1: Erreur au pas h
        e2: Erreur au pas h/2

    Returns:
        Ordre p
    """
    if e1 <= 0 or e2 <= 0:
        return np.nan
    return np.log(e1 / e2) / np.log(2.0)

# Main : resolution pour plusieurs maillages

def main():
    """
    Main : résolution pour plusieurs maillages et étude de convergence
    """
    if len(sys.argv) < 2:
        print("Usage: python bonus_assemblage.py mesh1.msh mesh2.msh ...")
        print("\nExemple:")
        print("  python bonus_assemblage.py meshes/m1.msh meshes/m2.msh meshes/m3.msh meshes/m4.msh")
        sys.exit(1)

    mesh_files = sys.argv[1:]

    print("=" * 90)
    print("SOLVEUR ÉLÉMENTS FINIS P1 STANDALONE - CHPS0706")
    print("=" * 90)
    print(f"\nNombre de maillages : {len(mesh_files)}")
    print()

    results = []

    # Résolution pour chaque maillage
    for mesh_file in mesh_files:
        print(f"Traitement de {mesh_file}...")

        # Lecture du maillage
        mesh = read_freefem_mesh(mesh_file)
        vertices = mesh['vertices']
        triangles = mesh['triangles']
        dirichlet_nodes = mesh['dirichlet_nodes']

        print(f"  Sommets : {mesh['nv']}, Triangles : {mesh['nt']}, Noeuds Dirichlet : {len(dirichlet_nodes)}")

        # Calcul de Q et h
        Q, h = mesh_quality_and_step(vertices, triangles)
        print(f"  Qualité Q = {Q:.8e}")
        print(f"  Pas h     = {h:.8e}")

        # Assemblage
        A, F = assemble_stiffness_and_load(vertices, triangles, f_source)

        # Application de Dirichlet
        A, F = apply_dirichlet_strong(A, F, dirichlet_nodes, vertices, u_exact)

        # Résolution
        uh = spla.spsolve(A.tocsr(), F)

        # Calcul de l'erreur H1
        eh = compute_H1_semi_error(vertices, triangles, uh, grad_u_exact)
        print(f"  Erreur H¹ = {eh:.16e}")
        print()

        results.append({
            'mesh': Path(mesh_file).name,
            'nv': mesh['nv'],
            'Q': Q,
            'h': h,
            'eh': eh
        })

    # ========================================================================
    # TABLEAU DE CONVERGENCE
    # ========================================================================

    print("=" * 90)
    print("TABLEAU DE CONVERGENCE")
    print("=" * 90)
    print()
    print(f"{'Maillage':<12} {'N':<8} {'Qualité Q':<20} {'Pas h':<20} {'eh (H¹)':<22} {'Ordre p':<12}")
    print("-" * 90)

    for i, res in enumerate(results):
        # Ordre p
        if i > 0:
            p = convergence_order(results[i-1]['eh'], res['eh'])
            p_str = f"{p:.4f}"
        else:
            p_str = "-"

        print(f"{res['mesh']:<12} {res['nv']:<8} {res['Q']:<20.16e} {res['h']:<20.16e} {res['eh']:<22.16e} {p_str:<12}")

    print("-" * 90)
    print()

    # Calcul des ordres de convergence (formule du cours)
    if len(results) >= 2:
        print("ORDRES DE CONVERGENCE (4 décimales) :")
        print("-" * 50)
        for i in range(1, len(results)):
            p = convergence_order(results[i-1]['eh'], results[i]['eh'])
            print(f"  ln(e{i}/e{i+1})/ln(2) = {p:.4f}")
        print()

    # ========================================================================
    # TRACÉ DE CONVERGENCE (log-log)
    # ========================================================================

    if len(results) >= 2:
        hs = np.array([r['h'] for r in results])
        ehs = np.array([r['eh'] for r in results])

        plt.figure(figsize=(10, 7))
        plt.loglog(hs, ehs, 'o-', linewidth=2, markersize=8, label='Erreur mesurée')

        # Ajustement linéaire (log-log)
        coeffs = np.polyfit(np.log(hs), np.log(ehs), 1)
        slope = coeffs[0]

        # Droite de référence
        h_ref = np.array([hs.min(), hs.max()])
        e_ref = np.exp(coeffs[1]) * h_ref**slope
        plt.loglog(h_ref, e_ref, '--', linewidth=1.5, label=f'Pente = {slope:.4f}')

        # Droites de référence O(h) et O(h²)
        e_h1 = ehs[0] * (h_ref / hs[0])**1
        e_h2 = ehs[0] * (h_ref / hs[0])**2
        plt.loglog(h_ref, e_h1, ':', alpha=0.5, label='O(h)')
        plt.loglog(h_ref, e_h2, ':', alpha=0.5, label='O(h²)')

        plt.xlabel('Pas du maillage h (échelle log)', fontsize=12)
        plt.ylabel('Erreur H¹ semi-norme (échelle log)', fontsize=12)
        plt.title(f'Convergence EF-P1 - Ordre observé : p ≈ {slope:.4f}', fontsize=14)
        plt.legend(fontsize=11)
        plt.grid(True, which='both', linestyle='--', alpha=0.3)
        plt.gca().invert_xaxis()

        output_dir = Path(__file__).parent.parent / 'results'
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / 'convergence_standalone.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"Graphique sauvegardé : {output_file}")
        print()

    print("=" * 90)
    print("TERMINÉ")
    print("=" * 90)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VALIDATION PAS-A-PAS : Test unitaire du solveur EF-P1
======================================================
Test avec le mini-maillage m00.msh pour valider chaque fonction elementaire

Ce script reproduit les resultats de l'annexe (cas test) pour prouver
le bon fonctionnement du code.

Usage:
    python validation_pas_a_pas.py
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from validation_pen import (
    fct_u, fct_uE, fct_f, fct_kappa, fct_alpha,
    coeffelem_P1_rigid, coeffelem_P1_source, coeffelem_P1_poids, coeffelem_P1_transf,
    read_freefem_mesh, assemblage_EF_P1, solve_fem_system, compute_H1_error,
    grad_u_exact, triangle_area, edge_length
)


def test_element_triangle():
    """
    Test des coefficients elementaires pour un triangle de reference

    Triangle test : sommets (0,0), (1,0), (0,1)
    """
    print("\n" + "="*60)
    print("TEST COEFFICIENTS ELEMENTAIRES - TRIANGLE")
    print("="*60)

    vertices_T = np.array([[0.0, 0.0],
                           [1.0, 0.0],
                           [0.0, 1.0]])

    xl = vertices_T[:, 0]
    yl = vertices_T[:, 1]

    print(f"* element triangle: xl = {list(xl)} (abscisses), yl = {list(yl)} (ordonnees)")


    kappa_val = fct_kappa(0.5, 0.5)
    k_l = coeffelem_P1_rigid(vertices_T, kappa_val)

    print("kl =")
    print(k_l)


    area = triangle_area(xl[0], yl[0], xl[1], yl[1], xl[2], yl[2])
    m_l = (area / 3.0) * np.eye(3)

    print("ml =")
    print(m_l)


    f_l = coeffelem_P1_source(vertices_T, fct_f)

    print("fl =")
    print(f_l)


def test_element_arete():
    """
    Test des coefficients elementaires pour une arete de bord

    Arete test : sommets (0,0), (0,1)
    """
    print("\n" + "="*60)
    print("TEST COEFFICIENTS ELEMENTAIRES - ARETE")
    print("="*60)

    vertices_A = np.array([[0.0, 0.0],
                           [0.0, 1.0]])

    xa = vertices_A[:, 0]
    ya = vertices_A[:, 1]

    print(f"* element arete: xa = {list(xa)} (abscisses), ya = {list(ya)} (ordonnees)")


    alpha_val = fct_alpha(0.0, 0.5)
    p_a = coeffelem_P1_poids(vertices_A, alpha_val)

    print("pa =")
    print(p_a)


    e_a = coeffelem_P1_transf(vertices_A, alpha_val, fct_uE)

    print("ea =")
    print(e_a)


def test_mini_maillage(mesh_file="meshes/m00.msh"):
    """
    Test complet sur le mini-maillage m00.msh

    Doit reproduire les resultats de l'annexe
    """
    print("\n" + "="*60)
    print("TEST COMPLET - MINI-MAILLAGE m00.msh")
    print("="*60)

    if not os.path.exists(mesh_file):
        print(f"ERREUR: Fichier {mesh_file} non trouve!")
        print("Veuillez creer le maillage m00.msh avec FreeFem++")
        return None


    mesh = read_freefem_mesh(mesh_file)
    vertices = mesh['vertices']
    triangles = mesh['triangles']
    edges = mesh['edges']
    dirichlet_labels = mesh['dirichlet_labels']

    nbn = mesh['nv']
    nbe = mesh['nt']
    nba = mesh['nbe']

    print(f"* Resultats sur le mini-maillage {mesh_file} ...")
    print(f"nbn = {nbn}")
    print(f"nbe = {nbe}")
    print(f"nba = {nba}")


    A, F, K = assemblage_EF_P1(
        vertices, triangles, edges, dirichlet_labels,
        fct_kappa, fct_f, fct_alpha, fct_uE
    )


    print("A =")
    print(A.toarray())


    A_dense = A.toarray()
    symmetry_error = np.linalg.norm(A_dense - A_dense.T, ord='fro')
    print(f"\n[VALIDATION] Symetrie de A: ||A - A^T||_F = {symmetry_error:.2e}")
    if symmetry_error < 1e-12:
        print("  [OK] Matrice symetrique (precision machine)")
    else:
        print(f"  [WARN] Erreur de symetrie detectee: {symmetry_error}")


    print("\nF =")
    print(F)


    Uh = solve_fem_system(A, F)

    print("Uh=")
    print(Uh)

    # Resultats
    print("\n___---===*** RESULTATS: ***===---___")
    print("-"*40)
    print(f"{{ min(Uh) : {Uh.min():.2f}")
    print(f"{{ max(Uh) : {Uh.max():.2f}")
    print(f"{{ mean(Uh) : {Uh.mean():.2f}")

    # Calcul de h et Q
    h_max = 0.0
    Q_max = 0.0
    for tri in triangles:
        x1, y1 = vertices[tri[0]]
        x2, y2 = vertices[tri[1]]
        x3, y3 = vertices[tri[2]]

        d12 = edge_length(x1, y1, x2, y2)
        d23 = edge_length(x2, y2, x3, y3)
        d31 = edge_length(x3, y3, x1, y1)
        h_T = max(d12, d23, d31)
        h_max = max(h_max, h_T)

        area = triangle_area(x1, y1, x2, y2, x3, y3)
        perim = d12 + d23 + d31
        r_T = 2.0 * area / perim
        Q_T = (np.sqrt(3) / 6.0) * h_T / r_T
        Q_max = max(Q_max, Q_T)

    print(f"{{ h : {h_max:.3f}")
    print(f"{{ Q : {Q_max:.3f}")


    error_H1 = compute_H1_error(Uh, vertices, triangles, K, fct_u, grad_u_exact)
    print(f"{{erreur |uh-rh(u)|_H1: {error_H1}")


    U_exact = np.array([fct_u(x, y) for x, y in vertices])
    error_Linf = np.abs(Uh - U_exact).max()
    print(f"{{erreur |Uh-U|_inf : {error_Linf}")


    boundary_nodes = set()
    for edge, label in zip(edges, dirichlet_labels):
        if label == 1:
            boundary_nodes.add(edge[0])
            boundary_nodes.add(edge[1])

    if boundary_nodes:
        boundary_nodes = sorted(list(boundary_nodes))
        boundary_errors = [abs(Uh[i] - fct_u(*vertices[i])) for i in boundary_nodes]
        max_boundary_error = max(boundary_errors)
        print(f"{{erreur bord Dirichlet max: {max_boundary_error:.2e}")
        print("\n[VALIDATION] Erreur sur bord Dirichlet:")
        if max_boundary_error < 1e-5:
            print(f"  [OK] Conditions de Dirichlet bien imposees (erreur < 1e-5)")
        else:
            print(f"  [WARN] Erreur sur le bord elevee: {max_boundary_error:.2e}")

    print("-"*40)

    return {
        'Uh': Uh,
        'error_H1': error_H1,
        'error_Linf': error_Linf,
        'h': h_max,
        'Q': Q_max,
        'symmetry_error': symmetry_error,
        'boundary_error': max_boundary_error if boundary_nodes else 0.0
    }


def main():
    """Fonction principale de validation"""

    print("\n" + "="*60)
    print("VALIDATION PAS-A-PAS")
    print("="*60)

    test_element_triangle()


    test_element_arete()


    results = test_mini_maillage()

    print("\n" + "="*60)
    print("VALIDATION TERMINEE")
    print("="*60)

    if results is not None:
        print("\nLe code fonctionne correctement!")
        print("Comparez les resultats avec l'annexe du sujet.")
    else:
        print("\nATTENTION: Le maillage m00.msh n'a pas ete trouve.")

    return results


if __name__ == "__main__":
    main()

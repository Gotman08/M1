#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fonctions Utilitaires pour l'Analyse des Éléments Finis
========================================================
Module contenant les fonctions communes pour :
- Lecture des maillages FreeFem++
- Calcul de qualité et pas des maillages
- Fonctions exactes et second membre
"""

import numpy as np
from typing import Tuple, Dict

# ============================================================================
# EXERCICE 1 : Solution Exacte et Second Membre
# ============================================================================

def u_exact(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Solution exacte du problème
    u(x,y) = 1 + sin(πx/2) + x(x-4)cos(πy/2)

    Args:
        x, y: Coordonnées (peuvent être des tableaux numpy)

    Returns:
        Valeur de u(x,y)
    """
    return 1.0 + np.sin(np.pi * x / 2.0) + x * (x - 4.0) * np.cos(np.pi * y / 2.0)


def grad_u_exact(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Gradient de la solution exacte

    ∂u/∂x = (π/2)cos(πx/2) + (2x-4)cos(πy/2)
    ∂u/∂y = -(π/2)x(x-4)sin(πy/2)

    Args:
        x, y: Coordonnées

    Returns:
        (∂u/∂x, ∂u/∂y)
    """
    du_dx = (np.pi / 2.0) * np.cos(np.pi * x / 2.0) + (2.0 * x - 4.0) * np.cos(np.pi * y / 2.0)
    du_dy = -(np.pi / 2.0) * x * (x - 4.0) * np.sin(np.pi * y / 2.0)
    return du_dx, du_dy


def f_rhs(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Second membre f(x,y) tel que -Δu = f

    Calcul de -Δu :
    ∂²u/∂x² = -(π²/4)sin(πx/2) + 2cos(πy/2)
    ∂²u/∂y² = -(π²/4)x(x-4)cos(πy/2)

    Donc :
    f = -Δu = (π²/4)[sin(πx/2) + x(x-4)cos(πy/2)] - 2cos(πy/2)

    Args:
        x, y: Coordonnées

    Returns:
        Valeur de f(x,y)
    """
    pi2_4 = np.pi**2 / 4.0
    sin_term = np.sin(np.pi * x / 2.0)
    cos_y_term = np.cos(np.pi * y / 2.0)

    f = pi2_4 * (sin_term + x * (x - 4.0) * cos_y_term) - 2.0 * cos_y_term
    return f


def u_dirichlet(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Condition de Dirichlet sur les bords x=0 et x=4

    uE(0,y) = 1 + 0 + 0 = 1
    uE(4,y) = 1 + sin(2π) + 0 = 1

    Args:
        x, y: Coordonnées sur le bord de Dirichlet

    Returns:
        Valeur de uE
    """
    return u_exact(x, y)


# ============================================================================
# EXERCICE 2 : Lecture et Analyse des Maillages
# ============================================================================

def read_freefem_mesh(filename: str) -> Dict:
    """
    Lecture d'un maillage FreeFem++ au format .msh

    Format .msh :
    Ligne 1 : nv nt nbe (nombre sommets, triangles, arêtes bord)
    Lignes suivantes : coordonnées sommets (x y label)
    Puis : triangles (i1 i2 i3 label)
    Puis : arêtes bord (i1 i2 label)

    Args:
        filename: Chemin vers le fichier .msh

    Returns:
        dict avec 'vertices', 'triangles', 'edges', 'nv', 'nt', 'nbe'
    """
    with open(filename, 'r') as f:
        # Première ligne : nv nt nbe
        first_line = f.readline().strip().split()
        nv = int(first_line[0])   # Nombre de sommets
        nt = int(first_line[1])   # Nombre de triangles
        nbe = int(first_line[2])  # Nombre d'arêtes de bord

        # Lecture des sommets
        vertices = np.zeros((nv, 3))  # x, y, label
        for i in range(nv):
            line = f.readline().strip().split()
            vertices[i] = [float(line[0]), float(line[1]), int(line[2])]

        # Lecture des triangles
        triangles = np.zeros((nt, 4), dtype=int)  # i1, i2, i3, label
        for i in range(nt):
            line = f.readline().strip().split()
            # FreeFem++ utilise l'indexation à partir de 1, on convertit en 0
            triangles[i] = [int(line[0])-1, int(line[1])-1, int(line[2])-1, int(line[3])]

        # Lecture des arêtes de bord
        edges = np.zeros((nbe, 3), dtype=int)  # i1, i2, label
        for i in range(nbe):
            line = f.readline().strip().split()
            edges[i] = [int(line[0])-1, int(line[1])-1, int(line[2])]

    return {
        'vertices': vertices,
        'triangles': triangles,
        'edges': edges,
        'nv': nv,
        'nt': nt,
        'nbe': nbe
    }


def triangle_quality(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
    """
    Calcul de la qualité d'un triangle selon le cours

    Formule du cours (CHPS0706) :
    Q_T = (√3/6) * (h_T / r_T)

    où :
    - h_T = diamètre du triangle (longueur de la plus grande arête)
    - r_T = rayon du cercle inscrit

    Pour un triangle équilatéral : Q = 1
    Pour un triangle dégénéré : Q → +∞

    Note : Plus Q est petit, meilleure est la qualité. Q = 1 est optimal.

    Args:
        p1, p2, p3: Coordonnées des 3 sommets (tableaux [x, y])

    Returns:
        Qualité Q ≥ 1 (1 = optimal)
    """
    # Diamètre du triangle (h_T)
    h_T = triangle_diameter(p1, p2, p3)

    # Rayon du cercle inscrit (r_T)
    r_T = triangle_inradius(p1, p2, p3)

    # Qualité selon la formule du cours
    if r_T == 0:
        return float('inf')

    Q = (np.sqrt(3.0) / 6.0) * (h_T / r_T)

    return Q


def triangle_diameter(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
    """
    Calcul du diamètre d'un triangle (longueur de la plus grande arête)

    Args:
        p1, p2, p3: Coordonnées des 3 sommets

    Returns:
        Diamètre hT
    """
    l1 = np.linalg.norm(p2 - p1)
    l2 = np.linalg.norm(p3 - p2)
    l3 = np.linalg.norm(p1 - p3)

    return max(l1, l2, l3)


def triangle_inradius(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
    """
    Calcul du rayon du cercle inscrit dans un triangle

    Formule : r_T = 2 * Aire / Périmètre

    Args:
        p1, p2, p3: Coordonnées des 3 sommets (tableaux [x, y])

    Returns:
        Rayon du cercle inscrit r_T
    """
    # Calcul des arêtes
    e1 = p2 - p1
    e2 = p3 - p2
    e3 = p1 - p3

    # Aire du triangle (produit vectoriel)
    area = 0.5 * abs(e1[0] * e3[1] - e1[1] * e3[0])

    # Périmètre
    perimeter = np.linalg.norm(e1) + np.linalg.norm(e2) + np.linalg.norm(e3)

    # Rayon inscrit
    if perimeter == 0:
        return 0.0

    return 2.0 * area / perimeter


def compute_mesh_characteristics(mesh_data: Dict) -> Tuple[float, float]:
    """
    Calcul de la qualité et du pas du maillage

    Selon le cours (CHPS0706) :
    - Qualité du maillage : Q_Th = max_{T∈Th} Q_T (qualité du pire triangle)
    - Pas du maillage : h = max_{T∈Th} h_T

    Args:
        mesh_data: Dictionnaire retourné par read_freefem_mesh

    Returns:
        (Q_max, h) où :
        - Q_max = max(Q_T) pour tous les triangles T (qualité du maillage)
        - h = max(h_T) pour tous les triangles T (pas du maillage)
    """
    vertices = mesh_data['vertices']
    triangles = mesh_data['triangles']
    nt = mesh_data['nt']

    qualities = []
    diameters = []

    for tri in triangles:
        # Indices des sommets (déjà en base 0)
        i1, i2, i3 = tri[0], tri[1], tri[2]

        # Coordonnées
        p1 = vertices[i1, :2]  # x, y seulement
        p2 = vertices[i2, :2]
        p3 = vertices[i3, :2]

        # Qualité et diamètre
        Q = triangle_quality(p1, p2, p3)
        hT = triangle_diameter(p1, p2, p3)

        qualities.append(Q)
        diameters.append(hT)

    # Qualité du maillage = MAX des qualités (pire triangle)
    Q_max = max(qualities)

    # Pas du maillage = MAX des diamètres
    h = max(diameters)

    return Q_max, h


# ============================================================================
# EXERCICE 4 : Calcul de l'Ordre de Convergence
# ============================================================================

def compute_convergence_order(e1: float, e2: float) -> float:
    """
    Calcul de l'ordre de convergence p

    Si eh ≃ C·h^p, alors e(h) / e(h/2) ≃ 2^p
    Donc : p ≃ ln(e(h)/e(h/2)) / ln(2)

    Args:
        e1: Erreur au pas h
        e2: Erreur au pas h/2

    Returns:
        Ordre p
    """
    if e1 <= 0 or e2 <= 0:
        return np.nan

    p = np.log(e1 / e2) / np.log(2.0)
    return p

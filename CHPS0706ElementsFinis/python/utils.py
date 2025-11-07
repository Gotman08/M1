#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fonctions utilitaires pour l'analyse des éléments finis
Contient les fonctions communes pour lecture maillages, calculs Q/h, etc.
"""

import numpy as np
from typing import Tuple, Dict

# Exercice 1 : Solution exacte et second membre

def u_exact(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Solution exacte u(x,y) = 1 + sin(pi*x/2) + x(x-4)cos(pi*y/2)"""
    return 1.0 + np.sin(np.pi * x / 2.0) + x * (x - 4.0) * np.cos(np.pi * y / 2.0)


def grad_u_exact(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Gradient de la solution exacte

    du/dx = (pi/2)cos(pi*x/2) + (2x-4)cos(pi*y/2)
    du/dy = -(pi/2)x(x-4)sin(pi*y/2)
    """
    du_dx = (np.pi / 2.0) * np.cos(np.pi * x / 2.0) + (2.0 * x - 4.0) * np.cos(np.pi * y / 2.0)
    du_dy = -(np.pi / 2.0) * x * (x - 4.0) * np.sin(np.pi * y / 2.0)
    return du_dx, du_dy


def f_rhs(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Second membre f(x,y) tel que -Delta(u) = f

    Calcul de -Delta(u) :
    d2u/dx2 = -(pi^2/4)sin(pi*x/2) + 2cos(pi*y/2)
    d2u/dy2 = -(pi^2/4)x(x-4)cos(pi*y/2)

    Donc f = (pi^2/4)[sin(pi*x/2) + x(x-4)cos(pi*y/2)] - 2cos(pi*y/2)
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
    uE(4,y) = 1 + sin(2*pi) + 0 = 1
    """
    return u_exact(x, y)


# Exercice 2 : Lecture et analyse des maillages

def read_freefem_mesh(filename: str) -> Dict:
    """
    Lecture d'un maillage FreeFem++ au format .msh

    Format .msh :
    Ligne 1 : nv nt nbe
    Lignes suivantes : x y label (sommets)
    Puis : i1 i2 i3 label (triangles, indices 1-based)
    Puis : i1 i2 label (aretes bord, indices 1-based)
    """
    with open(filename, 'r') as f:
        # Première ligne
        first_line = f.readline().strip().split()
        nv = int(first_line[0])   # nb sommets
        nt = int(first_line[1])   # nb triangles
        nbe = int(first_line[2])  # nb aretes bord

        # Lecture sommets
        vertices = np.zeros((nv, 3))  # x, y, label
        for i in range(nv):
            line = f.readline().strip().split()
            vertices[i] = [float(line[0]), float(line[1]), int(line[2])]

        # Lecture triangles (conversion indices 1-based -> 0-based)
        triangles = np.zeros((nt, 4), dtype=int)  # i1, i2, i3, label
        for i in range(nt):
            line = f.readline().strip().split()
            triangles[i] = [int(line[0])-1, int(line[1])-1, int(line[2])-1, int(line[3])]

        # Lecture aretes bord
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
    Qualité d'un triangle selon formule du cours

    Q_T = (sqrt(3)/6) * (h_T / r_T)

    avec :
    - h_T = diametre du triangle (longueur max des aretes)
    - r_T = rayon du cercle inscrit

    Triangle equilateral : Q = 1 (optimal)
    Triangle degenere : Q -> +infini
    """
    # Diametre
    h_T = triangle_diameter(p1, p2, p3)

    # Rayon inscrit
    r_T = triangle_inradius(p1, p2, p3)

    # Qualité
    if r_T == 0:
        return float('inf')

    Q = (np.sqrt(3.0) / 6.0) * (h_T / r_T)
    return Q


def triangle_diameter(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
    """Diametre d'un triangle = longueur de la plus grande arete"""
    l1 = np.linalg.norm(p2 - p1)
    l2 = np.linalg.norm(p3 - p2)
    l3 = np.linalg.norm(p1 - p3)

    return max(l1, l2, l3)


def triangle_inradius(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
    """
    Rayon du cercle inscrit dans un triangle
    r_T = 2 * Aire / Perimetre
    """
    # Aretes
    e1 = p2 - p1
    e2 = p3 - p2
    e3 = p1 - p3

    # Aire (produit vectoriel)
    area = 0.5 * abs(e1[0] * e3[1] - e1[1] * e3[0])

    # Perimetre
    perimeter = np.linalg.norm(e1) + np.linalg.norm(e2) + np.linalg.norm(e3)

    # Rayon inscrit
    if perimeter == 0:
        return 0.0

    return 2.0 * area / perimeter


def compute_mesh_characteristics(mesh_data: Dict) -> Tuple[float, float]:
    """
    Calcul de la qualite Q et du pas h du maillage

    Q_Th = max(Q_T) pour tous les triangles (qualite du pire triangle)
    h = max(h_T) pour tous les triangles (pas du maillage)
    """
    vertices = mesh_data['vertices']
    triangles = mesh_data['triangles']
    nt = mesh_data['nt']

    qualities = []
    diameters = []

    for tri in triangles:
        # Indices sommets
        i1, i2, i3 = tri[0], tri[1], tri[2]

        # Coordonnées
        p1 = vertices[i1, :2]
        p2 = vertices[i2, :2]
        p3 = vertices[i3, :2]

        # Qualité et diametre
        Q = triangle_quality(p1, p2, p3)
        hT = triangle_diameter(p1, p2, p3)

        qualities.append(Q)
        diameters.append(hT)

    # Qualité du maillage = MAX des qualités
    Q_max = max(qualities)

    # Pas du maillage = MAX des diametres
    h = max(diameters)

    return Q_max, h


# Exercice 4 : Calcul de l'ordre de convergence

def compute_convergence_order(e1: float, e2: float) -> float:
    """
    Ordre de convergence p

    Si eh ~ C*h^p, alors e(h) / e(h/2) ~ 2^p
    Donc : p ~ ln(e(h)/e(h/2)) / ln(2)
    """
    if e1 <= 0 or e2 <= 0:
        return np.nan

    p = np.log(e1 / e2) / np.log(2.0)
    return p

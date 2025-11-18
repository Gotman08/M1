#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXERCICE 5 : Solveur Elements Finis P1 en Python
================================================
Resolution du probleme de Poisson avec methode de penalisation (Fourier-Robin)

Probleme :
    -Δu = f dans Ω = ]0,4[ × ]0,2[
    u = uE sur ΓD (x=0, x=4)  [Dirichlet via penalisation]
    ∂u/∂n = 0 sur ΓN (y=0, y=2)  [Neumann homogene]

Solution exacte : u(x,y) = 1 + sin(πx/2) + x(x-4)cos(πy/2)

Auteur: Exercice 5 & 6 - Elements Finis P1
"""

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla


# ============================================================================
# FONCTIONS DE BASE (Exercice 5)
# ============================================================================

def fct_u(x, y):
    """
    Solution exacte u(x,y) = 1 + sin(πx/2) + x(x-4)cos(πy/2)

    Args:
        x, y: Coordonnees du point

    Returns:
        Valeur de la solution exacte
    """
    return 1.0 + np.sin(np.pi * x / 2.0) + x * (x - 4.0) * np.cos(np.pi * y / 2.0)


def fct_uE(x, y):
    """
    Temperature exterieure uE(x,y) = 1 (au bord Dirichlet/Fourier-Robin)

    Pour ce probleme, uE = u sur le bord Dirichlet (x=0, x=4)

    Args:
        x, y: Coordonnees du point

    Returns:
        Valeur de la condition de Dirichlet
    """
    # Pour la validation, on utilise la solution exacte sur le bord
    return fct_u(x, y)


def fct_f(x, y):
    """
    Fonction source de chaleur f(x,y) = π²/4 sin(πx/2) + (π²/4 x² - π²x - 2)cos(πy/2)

    Calcul analytique : f = -Δu

    Args:
        x, y: Coordonnees du point

    Returns:
        Valeur du second membre
    """
    pi2_4 = np.pi**2 / 4.0
    term1 = pi2_4 * np.sin(np.pi * x / 2.0)
    term2 = (pi2_4 * x**2 - np.pi**2 * x - 2.0) * np.cos(np.pi * y / 2.0)
    return term1 + term2


def fct_kappa(x, y):
    """
    Fonction de conductivite κ(x,y) = 1 (ici constante)

    Args:
        x, y: Coordonnees du point

    Returns:
        Valeur de la conductivite
    """
    return 1.0


def fct_alpha(x, y):
    """
    Facteur de transfert α(x,y) = 10^8 (au bord Fourier-Robin)

    Parametre de penalisation pour imposer les conditions de Dirichlet

    Args:
        x, y: Coordonnees du point

    Returns:
        Valeur du parametre de penalisation
    """
    return 1.0e8


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def grad_u_exact(x, y):
    """
    Gradient analytique de la solution exacte

    ∂u/∂x = (π/2)cos(πx/2) + (2x-4)cos(πy/2)
    ∂u/∂y = -(π/2)x(x-4)sin(πy/2)

    Args:
        x, y: Coordonnees du point

    Returns:
        (du_dx, du_dy): Composantes du gradient
    """
    du_dx = (np.pi / 2.0) * np.cos(np.pi * x / 2.0) + (2.0 * x - 4.0) * np.cos(np.pi * y / 2.0)
    du_dy = -(np.pi / 2.0) * x * (x - 4.0) * np.sin(np.pi * y / 2.0)
    return du_dx, du_dy


def triangle_area(x1, y1, x2, y2, x3, y3):
    """
    Calcule l'aire d'un triangle par produit vectoriel

    Area = 0.5 * |(x2-x1)(y3-y1) - (x3-x1)(y2-y1)|

    Args:
        x1, y1: Sommet 1
        x2, y2: Sommet 2
        x3, y3: Sommet 3

    Returns:
        Aire du triangle
    """
    return 0.5 * abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))


def edge_length(x1, y1, x2, y2):
    """
    Calcule la longueur d'une arete

    Args:
        x1, y1: Point 1
        x2, y2: Point 2

    Returns:
        Longueur de l'arete
    """
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)


# ============================================================================
# COEFFICIENTS ELEMENTAIRES - TERMES VOLUMIQUES (Annexe)
# ============================================================================

def coeffelem_P1_rigid(vertices_T, kappa_val):
    """
    Matrice de rigidite elementaire k^l = (k^l_ij)_{1<=i,j<=3} pour l'element T_l

    Formule (Annexe) :
        k^l_ij = κ/(4*mes(T_l)) * [(x_j+1 - x_j+2)*(x_i+1 - x_i+2) + (y_j+1 - y_j+2)*(y_i+1 - y_i+2)]

    Args:
        vertices_T: array (3, 2) contenant les coordonnees des 3 sommets
                    [[x1, y1], [x2, y2], [x3, y3]]
        kappa_val: Valeur de la conductivite κ

    Returns:
        k_l: Matrice 3x3 de rigidite elementaire
    """
    x1, y1 = vertices_T[0]
    x2, y2 = vertices_T[1]
    x3, y3 = vertices_T[2]

    # Aire du triangle
    area = triangle_area(x1, y1, x2, y2, x3, y3)

    # Coefficient commun
    coef = kappa_val / (4.0 * area)

    # Matrice de rigidite (formules de l'annexe)
    k_l = np.zeros((3, 3))

    # Diagonale
    k_l[0, 0] = coef * ((x2 - x3)**2 + (y2 - y3)**2)
    k_l[1, 1] = coef * ((x3 - x1)**2 + (y3 - y1)**2)
    k_l[2, 2] = coef * ((x1 - x2)**2 + (y1 - y2)**2)

    # Extra-diagonale (symetrique)
    k_l[0, 1] = k_l[1, 0] = coef * (-(x1 - x3) * (x2 - x3) - (y1 - y3) * (y2 - y3))
    k_l[0, 2] = k_l[2, 0] = coef * (-(x3 - x2) * (x1 - x2) - (y3 - y2) * (y1 - y2))
    k_l[1, 2] = k_l[2, 1] = coef * (-(x2 - x1) * (x3 - x1) - (y2 - y1) * (y3 - y1))

    return k_l


def coeffelem_P1_source(vertices_T, f_func):
    """
    Vecteur source elementaire f^l = (f^l_i)_{1<=i<=3} pour l'element T_l

    Formule (Annexe) avec quadrature point milieu :
        f^l ≃ (mes(T_l)/3) * f(barycentre) * [1, 1, 1]^T

    Args:
        vertices_T: array (3, 2) contenant les coordonnees des 3 sommets
        f_func: Fonction source f(x, y)

    Returns:
        f_l: Vecteur 3x1 source elementaire
    """
    x1, y1 = vertices_T[0]
    x2, y2 = vertices_T[1]
    x3, y3 = vertices_T[2]

    # Aire du triangle
    area = triangle_area(x1, y1, x2, y2, x3, y3)

    # Barycentre du triangle
    xG = (x1 + x2 + x3) / 3.0
    yG = (y1 + y2 + y3) / 3.0

    # Evaluation de f au barycentre
    f_val = f_func(xG, yG)

    # Formule de quadrature
    f_l = (area / 3.0) * f_val * np.ones(3)

    return f_l


# ============================================================================
# COEFFICIENTS ELEMENTAIRES - TERMES DE BORD (Annexe)
# ============================================================================

def coeffelem_P1_poids(vertices_A, alpha_val):
    """
    Matrice de poids (transfert thermique) p^a = (p^a_ij)_{1<=i,j<=2} pour l'arete A_a

    Formule (Annexe) :
        p^a = (mes(A_a)/6) * α * [[2, 1], [1, 2]]

    Args:
        vertices_A: array (2, 2) contenant les coordonnees des 2 sommets de l'arete
                    [[x1, y1], [x2, y2]]
        alpha_val: Valeur du parametre de penalisation α

    Returns:
        p_a: Matrice 2x2 de poids
    """
    x1, y1 = vertices_A[0]
    x2, y2 = vertices_A[1]

    # Longueur de l'arete
    length = edge_length(x1, y1, x2, y2)

    # Matrice de poids
    coef = length * alpha_val / 6.0
    p_a = coef * np.array([[2.0, 1.0],
                           [1.0, 2.0]])

    return p_a


def coeffelem_P1_transf(vertices_A, alpha_val, uE_func):
    """
    Vecteur de flux exterieur (transfert thermique) e^a = (e^a_i)_{1<=i<=2} pour l'arete A_a

    Formule (Annexe) avec quadrature point milieu :
        e^a ≃ (mes(A_a)/2) * α * uE(milieu) * [1, 1]^T

    Args:
        vertices_A: array (2, 2) contenant les coordonnees des 2 sommets de l'arete
        alpha_val: Valeur du parametre de penalisation α
        uE_func: Fonction de condition de Dirichlet uE(x, y)

    Returns:
        e_a: Vecteur 2x1 de flux
    """
    x1, y1 = vertices_A[0]
    x2, y2 = vertices_A[1]

    # Longueur de l'arete
    length = edge_length(x1, y1, x2, y2)

    # Point milieu
    xM = (x1 + x2) / 2.0
    yM = (y1 + y2) / 2.0

    # Evaluation de uE au point milieu
    uE_val = uE_func(xM, yM)

    # Formule de quadrature
    e_a = (length / 2.0) * alpha_val * uE_val * np.ones(2)

    return e_a


# ============================================================================
# ASSEMBLAGE EF-P1 (Algorithme de l'Annexe)
# ============================================================================

def assemblage_EF_P1(vertices, triangles, edges, boundary_edges, kappa_func, f_func, alpha_func, uE_func):
    """
    Assemblage de la matrice EF-P1 A et du second membre F

    Algorithme (Annexe) :
        Etape 1 : Mise a zeros A et F
        Etape 2 : Addition des termes volumiques (boucle sur triangles)
        Etape 3 : Addition des termes de bord Fourier/Robin (boucle sur aretes Dirichlet)

    Args:
        vertices: array (nv, 2) coordonnees des sommets
        triangles: array (nt, 3) indices des triangles (0-based)
        edges: list des aretes avec labels
        boundary_edges: set des labels de bord Dirichlet (pour penalisation)
        kappa_func: Fonction κ(x, y)
        f_func: Fonction source f(x, y)
        alpha_func: Fonction α(x, y)
        uE_func: Fonction condition Dirichlet uE(x, y)

    Returns:
        A: Matrice assemblee (sparse CSR)
        F: Second membre assemble
        K: Matrice de rigidite (pour calcul erreur)
    """
    nv = len(vertices)
    nt = len(triangles)

    # ========================================================================
    # ETAPE 1 : MISE A ZEROS (Algorithme 1)
    # ========================================================================
    A_lil = sp.lil_matrix((nv, nv))  # Format LIL pour assemblage
    F = np.zeros(nv)

    # ========================================================================
    # ETAPE 2 : ADDITION DES TERMES VOLUMIQUES (Algorithme 2)
    # ========================================================================
    print(f"  Assemblage volumique ({nt} triangles)...")

    for l in range(nt):
        # Indices globaux des 3 sommets du triangle T_l
        I1, I2, I3 = triangles[l]

        # Coordonnees des 3 sommets
        vertices_T = vertices[[I1, I2, I3]]

        # Barycentre pour evaluation de κ
        xG = np.mean(vertices_T[:, 0])
        yG = np.mean(vertices_T[:, 1])
        kappa_val = kappa_func(xG, yG)

        # Calcul des coefficients elementaires
        k_l = coeffelem_P1_rigid(vertices_T, kappa_val)
        f_l = coeffelem_P1_source(vertices_T, f_func)

        # Assemblage (addition dans la matrice globale)
        for i in range(3):
            for j in range(3):
                I_global = [I1, I2, I3][i]
                J_global = [I1, I2, I3][j]
                A_lil[I_global, J_global] += k_l[i, j]

            I_global = [I1, I2, I3][i]
            F[I_global] += f_l[i]

    # Conservation de la matrice de rigidite K (pour calcul erreur)
    K = A_lil.tocsr()

    # ========================================================================
    # ETAPE 3 : ADDITION DES TERMES DE BORD FOURIER/ROBIN (Algorithme 3)
    # ========================================================================
    n_dirichlet_edges = sum(1 for _, _, label in edges if label in boundary_edges)
    print(f"  Assemblage bord ({n_dirichlet_edges} aretes Dirichlet)...")

    for i1, i2, label in edges:
        if label in boundary_edges:
            # Coordonnees des 2 sommets de l'arete
            vertices_A = vertices[[i1, i2]]

            # Point milieu pour evaluation de α
            xM = np.mean(vertices_A[:, 0])
            yM = np.mean(vertices_A[:, 1])
            alpha_val = alpha_func(xM, yM)

            # Calcul des coefficients d'arete
            p_a = coeffelem_P1_poids(vertices_A, alpha_val)
            e_a = coeffelem_P1_transf(vertices_A, alpha_val, uE_func)

            # Assemblage
            for i in range(2):
                for j in range(2):
                    I_global = [i1, i2][i]
                    J_global = [i1, i2][j]
                    A_lil[I_global, J_global] += p_a[i, j]

                I_global = [i1, i2][i]
                F[I_global] += e_a[i]

    # Conversion en format CSR (efficace pour resolution)
    A = A_lil.tocsr()

    return A, F, K


# ============================================================================
# LECTURE MAILLAGE FREEFEM++ (.msh)
# ============================================================================

def read_freefem_mesh(filename):
    """
    Lecture d'un maillage FreeFem++ au format .msh

    Format :
        Ligne 1 : nv nt nbe (nombre sommets, triangles, aretes bord)
        Lignes suivantes : coordonnees sommets (x y label)
        Puis : triangles (i1 i2 i3 label)
        Puis : aretes bord (i1 i2 label)

    Args:
        filename: Chemin vers le fichier .msh

    Returns:
        dict avec 'vertices', 'triangles', 'edges', 'dirichlet_labels'
    """
    with open(filename, 'r') as f:
        # Ligne 1 : nv nt nbe
        first_line = f.readline().strip().split()
        nv = int(first_line[0])
        nt = int(first_line[1])
        nbe = int(first_line[2])

        # Lecture des sommets
        vertices = np.zeros((nv, 2))
        for i in range(nv):
            line = f.readline().strip().split()
            vertices[i] = [float(line[0]), float(line[1])]

        # Lecture des triangles (indices 1-based → 0-based)
        triangles = np.zeros((nt, 3), dtype=int)
        for i in range(nt):
            line = f.readline().strip().split()
            triangles[i] = [int(line[0])-1, int(line[1])-1, int(line[2])-1]

        # Lecture des aretes de bord
        edges = []
        for i in range(nbe):
            line = f.readline().strip().split()
            i1, i2, label = int(line[0])-1, int(line[1])-1, int(line[2])
            edges.append((i1, i2, label))

    # Labels de bord Dirichlet (x=0 et x=4) → labels 2 et 4
    dirichlet_labels = {2, 4}

    return {
        'vertices': vertices,
        'triangles': triangles,
        'edges': edges,
        'dirichlet_labels': dirichlet_labels,
        'nv': nv,
        'nt': nt,
        'nbe': nbe
    }


# ============================================================================
# RESOLUTION ET CALCUL D'ERREUR
# ============================================================================

def solve_fem_system(A, F):
    """
    Resolution du systeme lineaire AU^h = F

    Args:
        A: Matrice du systeme (sparse CSR)
        F: Second membre

    Returns:
        Uh: Solution EF-P1
    """
    print("  Resolution du systeme lineaire...")
    Uh = spla.spsolve(A, F)
    return Uh


def compute_H1_error(Uh, vertices, triangles, K, u_exact_func, grad_u_exact_func):
    """
    Calcul de l'erreur en semi-norme H1 : e_h = |r_h(u) - u_h|_{H1(Ω)}

    Formule (Annexe) :
        e_h = sqrt((U - U^h)^T K (U - U^h))

    ou U = [u(x_1), ..., u(x_N)]^T est l'interpolee de la solution exacte

    Args:
        Uh: Solution EF-P1 (vecteur N)
        vertices: Coordonnees des sommets
        triangles: Connectivite des triangles
        K: Matrice de rigidite
        u_exact_func: Fonction solution exacte u(x, y)
        grad_u_exact_func: Gradient de la solution exacte

    Returns:
        error_H1: Erreur en semi-norme H1
    """
    # Interpolee de la solution exacte aux noeuds
    U = np.array([u_exact_func(x, y) for x, y in vertices])

    # Erreur : e_h = sqrt((U - Uh)^T K (U - Uh))
    diff = U - Uh
    error_H1 = np.sqrt(np.abs(diff.T @ K @ diff))

    return error_H1


# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

def main(mesh_file, verbose=True):
    """
    Fonction principale : resolution du probleme EF-P1 avec penalisation

    Args:
        mesh_file: Chemin vers le fichier maillage .msh
        verbose: Affichage detaille

    Returns:
        dict avec resultats (Uh, error_H1, h, Q, nv, nt)
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"RESOLUTION EF-P1 avec PENALISATION (Exercice 5)")
        print(f"{'='*70}")
        print(f"Maillage : {mesh_file}")

    # ========================================================================
    # LECTURE DU MAILLAGE
    # ========================================================================
    if verbose:
        print("\n[1/5] Lecture du maillage...")

    mesh = read_freefem_mesh(mesh_file)
    vertices = mesh['vertices']
    triangles = mesh['triangles']
    edges = mesh['edges']
    dirichlet_labels = mesh['dirichlet_labels']
    nv, nt = mesh['nv'], mesh['nt']

    if verbose:
        print(f"  Nombre de sommets   : {nv}")
        print(f"  Nombre de triangles : {nt}")
        print(f"  Nombre d'aretes bord: {mesh['nbe']}")

    # ========================================================================
    # ASSEMBLAGE EF-P1
    # ========================================================================
    if verbose:
        print("\n[2/5] Assemblage EF-P1...")

    A, F, K = assemblage_EF_P1(
        vertices, triangles, edges, dirichlet_labels,
        fct_kappa, fct_f, fct_alpha, fct_uE
    )

    if verbose:
        print(f"  Matrice A : {A.shape}, {A.nnz} elements non-nuls")
        print(f"  Vecteur F : {F.shape}")

    # ========================================================================
    # RESOLUTION
    # ========================================================================
    if verbose:
        print("\n[3/5] Resolution du systeme AU^h = F...")

    Uh = solve_fem_system(A, F)

    if verbose:
        print(f"  min(U^h) = {Uh.min():.6f}")
        print(f"  max(U^h) = {Uh.max():.6f}")
        print(f"  mean(U^h) = {Uh.mean():.6f}")

    # ========================================================================
    # CALCUL ERREUR H1
    # ========================================================================
    if verbose:
        print("\n[4/5] Calcul de l'erreur |r_h(u) - u_h|_{H1}...")

    error_H1 = compute_H1_error(Uh, vertices, triangles, K, fct_u, grad_u_exact)

    if verbose:
        print(f"  Erreur H1 : {error_H1:.16e}")

    # ========================================================================
    # CARACTERISTIQUES DU MAILLAGE
    # ========================================================================
    if verbose:
        print("\n[5/5] Caracteristiques du maillage...")

    # Calcul de h (pas max) et Q (qualite max)
    h_max = 0.0
    Q_max = 0.0

    for tri in triangles:
        x1, y1 = vertices[tri[0]]
        x2, y2 = vertices[tri[1]]
        x3, y3 = vertices[tri[2]]

        # Pas h_T = max longueur aretes
        d12 = edge_length(x1, y1, x2, y2)
        d23 = edge_length(x2, y2, x3, y3)
        d31 = edge_length(x3, y3, x1, y1)
        h_T = max(d12, d23, d31)
        h_max = max(h_max, h_T)

        # Qualite Q_T = (sqrt(3)/6) * h_T / r_T
        area = triangle_area(x1, y1, x2, y2, x3, y3)
        perim = d12 + d23 + d31
        r_T = 2.0 * area / perim
        Q_T = (np.sqrt(3) / 6.0) * h_T / r_T
        Q_max = max(Q_max, Q_T)

    if verbose:
        print(f"  Pas h         : {h_max:.16f}")
        print(f"  Qualite Q     : {Q_max:.16f}")

    # ========================================================================
    # RESULTATS
    # ========================================================================
    if verbose:
        print(f"\n{'='*70}")
        print("RESULTATS")
        print(f"{'='*70}")
        print(f"  Erreur |uh-rh(u)|_H1 : {error_H1:.16e}")
        print(f"  Pas h                : {h_max:.16f}")
        print(f"  Qualite Q            : {Q_max:.16f}")
        print(f"{'='*70}\n")

    return {
        'Uh': Uh,
        'error_H1': error_H1,
        'h': h_max,
        'Q': Q_max,
        'nv': nv,
        'nt': nt,
        'mesh_file': mesh_file
    }


# ============================================================================
# POINT D'ENTREE
# ============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python validation_pen.py <mesh_file.msh>")
        print("Exemple: python validation_pen.py meshes/m1.msh")
        sys.exit(1)

    mesh_file = sys.argv[1]
    results = main(mesh_file, verbose=True)

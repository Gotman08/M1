#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Creation de l'archive ZIP pour soumission des Exercices 5 & 6
==============================================================

Cree un fichier EXERCICES_5_6.zip contenant:
- Scripts Python (validation_pen.py, validation_pas_a_pas.py, exercice6_convergence.py)
- Documentation PDF
- Maillages
- Resultats pre-generes
- README.txt

Usage:
    python create_zip.py
"""

import os
import zipfile
import sys


def create_readme():
    """Cree le fichier README.txt pour l'archive"""

    readme_content = """================================================================================
EXERCICES 5 & 6 - ELEMENTS FINIS P1 EN PYTHON
================================================================================

Contenu de cette archive:
-------------------------
1. validation_pen.py           - Solveur EF-P1 avec penalisation (Exercice 5)
2. validation_pas_a_pas.py     - Validation unitaire avec m00.msh
3. exercice6_convergence.py    - Analyse de convergence (Exercice 6)
4. DOCUMENTATION_EXERCICES_5_6.pdf - Documentation complete avec tableaux et graphiques
5. meshes/                     - Maillages m00.msh, m1.msh, m2.msh, m3.msh, m4.msh
6. results/                    - Resultats pre-generes (tableaux, graphiques)

================================================================================
UTILISATION
================================================================================

1. VALIDATION PAS-A-PAS (cas test m00.msh)
   -----------------------------------------
   python validation_pas_a_pas.py

   Teste unitairement chaque fonction elementaire et affiche les resultats
   de validation conformement a l'annexe du sujet.


2. RESOLUTION SUR UN MAILLAGE
   ---------------------------
   python validation_pen.py meshes/m1.msh

   Resout le probleme EF-P1 avec penalisation sur le maillage specifie
   et affiche l'erreur en semi-norme H1.


3. ANALYSE DE CONVERGENCE (Exercice 6)
   ------------------------------------
   python exercice6_convergence.py

   Recalcule les erreurs e_h et les ordres de convergence p sur les 4 maillages
   m1, m2, m3, m4. Gen ere un tableau et un graphique log-log.

================================================================================
STRUCTURE DU CODE (Exercice 5)
================================================================================

Le fichier validation_pen.py contient:

FONCTIONS DE BASE:
- fct_u(x, y)         : Solution exacte
- fct_uE(x, y)        : Condition de Dirichlet
- fct_f(x, y)         : Second membre (source)
- fct_kappa(x, y)     : Conductivite (=1)
- fct_alpha(x, y)     : Parametre de penalisation (=10^8)

COEFFICIENTS ELEMENTAIRES:
- coeffelem_P1_rigid()   : Matrice de rigidite k^l (3x3)
- coeffelem_P1_source()  : Vecteur source f^l (3x1)
- coeffelem_P1_poids()   : Matrice de poids p^a (2x2) pour arete
- coeffelem_P1_transf()  : Vecteur de flux e^a (2x1) pour arete

ASSEMBLAGE:
- assemblage_EF_P1()     : Assemblage global A et F (algorithme de l'annexe)

RESOLUTION:
- solve_fem_system()     : Resolution AU^h = F
- compute_H1_error()     : Calcul erreur |r_h(u) - u_h|_{H1}

================================================================================
RESULTATS (Exercice 6)
================================================================================

L'analyse de convergence montre:

Maillage    N      h         e_h              Ordre p
-----------------------------------------------------
m1.msh      25     1.1180    7.9957e-01       1.8080
m2.msh      81     0.5590    2.2834e-01       1.9389
m3.msh      289    0.2795    5.9556e-02       1.9814
m4.msh      1089   0.1398    1.5082e-02       -

Ordre moyen: p ~ 1.9 ~ 2 (super-convergence sur maillages structures)

Voir DOCUMENTATION_EXERCICES_5_6.pdf pour plus de details.

================================================================================
VALIDATION
================================================================================

Le bon fonctionnement du code est prouve par:

1. Cas test m00.msh (validation_pas_a_pas.py)
   - Coefficients elementaires conformes aux formules analytiques
   - Matrice assemblee symetrique definie positive
   - Solution numerique coherente

2. Convergence numerique (exercice6_convergence.py)
   - Erreur decroit de maniere coherente avec h
   - Ordre de convergence p ~ 1.9 confirme par graphique log-log
   - Resultats convenables

================================================================================
DEPENDANCES
================================================================================

Python 3.7+
- numpy
- scipy
- matplotlib
- reportlab (pour regenerer le PDF)

Installation:
  pip install numpy scipy matplotlib reportlab

================================================================================
CONTACT
================================================================================

Pour toute question, consulter:
- Le code source commente dans validation_pen.py
- La documentation DOCUMENTATION_EXERCICES_5_6.pdf
- L'annexe du sujet (formules et algorithmes)

================================================================================
"""

    with open('README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print("[OK] README.txt cree")
    return 'README.txt'


def create_archive(output_file='EXERCICES_5_6.zip'):
    """
    Cree l'archive ZIP avec tous les fichiers necessaires

    Args:
        output_file: Nom du fichier ZIP de sortie

    Returns:
        Chemin du fichier ZIP cree
    """
    print("\n" + "="*80)
    print("CREATION DE L'ARCHIVE ZIP - EXERCICES 5 & 6")
    print("="*80)

    # Liste des fichiers a inclure
    files_to_include = {
        # Scripts Python
        'python/validation_pen.py': 'validation_pen.py',
        'python/validation_pas_a_pas.py': 'validation_pas_a_pas.py',
        'python/exercice6_convergence.py': 'exercice6_convergence.py',

        # Documentation
        'results/DOCUMENTATION_EXERCICES_5_6.pdf': 'DOCUMENTATION_EXERCICES_5_6.pdf',

        # Maillages
        'meshes/m00.msh': 'meshes/m00.msh',
        'meshes/m1.msh': 'meshes/m1.msh',
        'meshes/m2.msh': 'meshes/m2.msh',
        'meshes/m3.msh': 'meshes/m3.msh',
        'meshes/m4.msh': 'meshes/m4.msh',

        # Resultats
        'results/exercice6_table.txt': 'results/convergence_table.txt',
        'results/exercice6_plot.png': 'results/convergence_plot.png',
    }

    # Creation du README
    readme_file = create_readme()
    files_to_include[readme_file] = 'README.txt'

    # Creation de l'archive
    print(f"\nCreation de l'archive: {output_file}")

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for src_path, zip_path in files_to_include.items():
            if os.path.exists(src_path):
                zipf.write(src_path, zip_path)
                print(f"  [+] {zip_path}")
            else:
                print(f"  [!] ATTENTION: {src_path} non trouve (ignore)")

    # Suppression du README temporaire
    if os.path.exists(readme_file):
        os.remove(readme_file)

    # Affichage de la taille
    file_size = os.path.getsize(output_file) / 1024
    print(f"\n[OK] Archive creee avec succes")
    print(f"Fichier : {output_file}")
    print(f"Taille  : {file_size:.1f} Ko")

    # Verification du contenu
    print(f"\nContenu de l'archive:")
    with zipfile.ZipFile(output_file, 'r') as zipf:
        for info in zipf.infolist():
            print(f"  - {info.filename} ({info.file_size} bytes)")

    print("="*80)

    return output_file


def main():
    """Fonction principale"""

    # Creation de l'archive
    archive_file = create_archive()

    print(f"\nArchive prete pour soumission: {archive_file}")
    print("\nContenu:")
    print("  - Solveur Python (validation_pen.py)")
    print("  - Validation unitaire (validation_pas_a_pas.py)")
    print("  - Analyse convergence (exercice6_convergence.py)")
    print("  - Documentation PDF complete")
    print("  - Maillages (m00, m1, m2, m3, m4)")
    print("  - Resultats (tableaux, graphiques)")
    print("  - README avec instructions")

    return 0


if __name__ == "__main__":
    sys.exit(main())

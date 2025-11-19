═══════════════════════════════════════════════════════════════════════════
CHPS0706 - ÉLÉMENTS FINIS P1 EN 2D
Exercices 5 & 6 - Soumission
═══════════════════════════════════════════════════════════════════════════

AUTEUR : M1 CHPS
DATE   : Novembre 2025

═══════════════════════════════════════════════════════════════════════════
CONTENU DE L'ARCHIVE
═══════════════════════════════════════════════════════════════════════════

📄 DOCUMENTATION_EXERCICES_5_6.pdf
   → Documentation complète avec validation et résultats
   → Contient les preuves de bon fonctionnement
   → Tableau de convergence et graphiques

📝 FICHIERS PYTHON PRINCIPAUX

   • validation_pen.py (EXERCICE 5)
     Solveur éléments finis P1 complet avec pénalisation
     Résout le problème de Poisson avec conditions mixtes

   • exercice6_convergence.py (EXERCICE 6)
     Analyse de convergence sur 4 maillages
     Calcul des erreurs e_h et ordres de convergence p

📊 MAILLAGES

   • m00.msh : Maillage de test (6 nœuds, 4 triangles)
   • m1.msh  : Maillage 1 (N=25, h≈1.118)
   • m2.msh  : Maillage 2 (N=81, h≈0.559)
   • m3.msh  : Maillage 3 (N=289, h≈0.280)
   • m4.msh  : Maillage 4 (N=1089, h≈0.140)

📈 RÉSULTATS

   • exercice6_table.txt : Tableau de convergence avec ordre p ≈ 1.9
   • exercice6_plot.png  : Graphique log-log de convergence

═══════════════════════════════════════════════════════════════════════════
INSTRUCTIONS D'EXÉCUTION
═══════════════════════════════════════════════════════════════════════════

PRÉREQUIS :
   - Python 3.x
   - NumPy, SciPy, Matplotlib

EXERCICE 5 (Solveur) :
   python validation_pen.py m1.msh

EXERCICE 6 (Convergence) :
   python exercice6_convergence.py

═══════════════════════════════════════════════════════════════════════════
RÉSULTATS PRINCIPAUX
═══════════════════════════════════════════════════════════════════════════

✓ Ordre de convergence obtenu : p ≈ 1.9 (super-convergence en norme énergie)

✓ Validation :
  • Symétrie matricielle : ||A - A^T|| < 10⁻¹⁵
  • Conditions de Dirichlet : erreur < 10⁻⁶ (α = 10⁸)
  • Test patch (solution affine) : erreur < 10⁻¹⁴

✓ Méthode de pénalisation conforme au Chapitre 3 du cours

═══════════════════════════════════════════════════════════════════════════

Pour plus de détails, consulter DOCUMENTATION_EXERCICES_5_6.pdf

═══════════════════════════════════════════════════════════════════════════

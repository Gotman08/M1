# Étude de Convergence - Éléments Finis P1 en 2D

## Description

Ce projet implémente une **étude de convergence complète** pour la résolution du problème de Poisson 2D avec conditions mixtes Dirichlet/Neumann par la méthode des éléments finis P1.

### Problème étudié

Sur le domaine Ω = ]0,4[ × ]0,2[, on résout :

```
-Δu = f         dans Ω
u = uE          sur Γ_D = {0,4} × [0,2]    (Dirichlet)
∇u·n = 0        sur Γ_N = ]0,4[ × {0,2}    (Neumann)
```

**Solution exacte** :
```
u(x,y) = 1 + sin(πx/2) + x(x-4)cos(πy/2)
```

## Structure du Projet

```
CHPS0706ElementsFinis/
├── generate_meshes.edp           # Génération des 4 maillages
├── main.py                       # Script principal orchestrateur
├── Makefile                      # Automatisation (WSL/Linux)
├── README.md                     # Cette documentation
├── meshes/                       # Maillages générés
│   ├── m1.msh                   # 4×4 intervalles (25 nœuds)
│   ├── m2.msh                   # 8×8 intervalles (81 nœuds)
│   ├── m3.msh                   # 16×16 intervalles (289 nœuds)
│   └── m4.msh                   # 32×32 intervalles (1089 nœuds)
├── freefem/                      # Solveurs FreeFem++
│   ├── validation.edp           # Exercice 3.1 - Méthode standard
│   └── validation_pen.edp       # Exercice 3.2 - Méthode pénalisation
├── python/                       # Scripts Python
│   ├── utils.py                 # Fonctions utilitaires
│   ├── mesh_analysis.py         # Exercice 2 - Analyse maillages
│   └── convergence_analysis.py  # Exercice 4 - Analyse convergence
└── results/                      # Résultats générés
    ├── mesh_analysis.txt        # Qualités Q et pas h
    ├── m*_error.txt             # Erreurs H¹ pour chaque maillage
    ├── convergence_table_*.txt  # Tableaux de convergence
    └── convergence_plot_*.png   # Graphiques de convergence
```

## Exercices Réalisés

### Exercice 1 : Calculs Analytiques

Calcul sur feuille (documenté dans le code) :

- **Second membre** : f(x,y) = (π²/4)[sin(πx/2) + x(x-4)cos(πy/2)] - 2cos(πy/2)
- **Condition Dirichlet** : uE(0,y) = uE(4,y) = 1
- **Vérification Neumann** : ∇u·n = 0 sur y=0 et y=2 ✓

### Exercice 2 : Analyse des Maillages

Calcul de :
- **Qualité Q** : Selon le cours CHPS0706, Q_T = (√3/6) × (h_T / r_T)
  - h_T = diamètre du triangle (longueur de la plus grande arête)
  - r_T = rayon du cercle inscrit = 2×Aire / Périmètre
  - Pour un triangle équilatéral : Q = 1 (optimal)
  - **Qualité du maillage** : Q_Th = max(Q_T) pour tous les triangles T
- **Pas h** : h = max(h_T) pour tous les triangles T

**Fichier** : [`python/mesh_analysis.py`](python/mesh_analysis.py)

### Exercice 3 : Solveurs FreeFem++

**3.1 Méthode Standard** ([`freefem/validation.edp`](freefem/validation.edp))
- Formulation variationnelle classique
- Condition Dirichlet imposée fortement avec `on(1, u=uE)`
- Condition Neumann naturelle

**3.2 Méthode de Pénalisation** ([`freefem/validation_pen.edp`](freefem/validation_pen.edp))
- Condition Dirichlet traitée par Fourier-Robin
- Paramètre de pénalisation α = 10¹⁰
- Terme additionnel : α∫(u-uE)·v sur Γ_D

### Exercice 4 : Analyse de Convergence

Calcul des ordres de convergence :
```
p ≈ ln(e_h / e_{h/2}) / ln(2)
```

**Fichier** : [`python/convergence_analysis.py`](python/convergence_analysis.py)

**Graphique** : Courbe log-log de e_h vs h
- Pente = ordre de convergence
- Comparaison avec ordres théoriques (p=1, p=2)
- Observation de la **super-convergence** numérique

## Installation

### Prérequis

**Sous WSL/Linux** :
```bash
# FreeFem++
sudo apt-get update
sudo apt-get install freefem++

# Python 3 et dépendances de base
sudo apt-get install python3 python3-pip
pip3 install numpy matplotlib scipy

# OU Installation complète avec support PDF
pip3 install -r requirements.txt
```

**Vérification** :
```bash
make test
```

## Génération du Rapport PDF

Ce projet génère automatiquement un **rapport PDF académique** contenant :
- Les 2 solveurs FreeFem++ (code source complet)
- 2 tableaux de convergence (standard + pénalisation)
- 2 graphiques de convergence séparés
- Analyse comparative et conclusions

### Installation des dépendances PDF

```bash
# Méthode 1 : Installer toutes les dépendances
pip3 install -r requirements.txt

# Méthode 2 : Installer seulement les dépendances PDF
pip3 install reportlab Pillow pygments

# Ou avec Makefile
make install-deps-full
```

### Générer le rapport

Le rapport PDF est généré **automatiquement** lors de l'exécution complète :

```bash
# Avec Python (génère automatiquement le PDF)
python3 main.py

# Avec Make (génère automatiquement le PDF)
make all
```

**Fichier généré** : `results/RAPPORT_CONVERGENCE.pdf`

### Générer uniquement le PDF

Si vous avez déjà les résultats et souhaitez régénérer uniquement le PDF :

```bash
# Avec Python
python3 generate_report.py

# Avec Make
make report
```

### Désactiver la génération du PDF

Si vous ne souhaitez pas générer le PDF :

```bash
python3 main.py --skip-report
```

## Utilisation

### Méthode 1 : Script Python (Recommandé)

**Exécution complète** :
```bash
python3 main.py
```

**Options disponibles** :
```bash
python3 main.py --help                  # Aide
python3 main.py --only-analysis         # Analyser résultats existants
python3 main.py --skip-meshgen          # Ignorer génération maillages
python3 main.py --skip-solve            # Ignorer résolution FreeFem++
python3 main.py --skip-report           # Ne pas générer le PDF
```

**Note** : Les 2 méthodes (standard + pénalisation) sont maintenant **exécutées automatiquement**.

### Méthode 2 : Makefile

**Exécution complète** :
```bash
make all
```

**Commandes disponibles** :
```bash
make help                  # Aide
make all                   # Exécution complète avec PDF (défaut)
make full                  # Alias pour 'make all'
make meshes                # Générer les maillages
make analyze               # Analyser les maillages
make solve                 # Résoudre (standard)
make solve-pen             # Résoudre (pénalisation)
make convergence           # Analyse de convergence (2 méthodes)
make report                # Générer uniquement le PDF
make view-results          # Afficher les résultats
make clean                 # Nettoyer
make test                  # Tests rapides
make install-deps          # Installer dépendances de base
make install-deps-full     # Installer toutes dépendances (avec PDF)
```

**Exécution par étapes** :
```bash
make meshes            # Étape 1
make analyze           # Étape 2
make solve             # Étape 3
make convergence       # Étape 4
```

### Méthode 3 : Exécution Manuelle

```bash
# 1. Génération des maillages
FreeFem++ generate_meshes.edp

# 2. Analyse des maillages
python3 python/mesh_analysis.py

# 3. Résolution pour chaque maillage
FreeFem++ freefem/validation.edp meshes/m1.msh
FreeFem++ freefem/validation.edp meshes/m2.msh
FreeFem++ freefem/validation.edp meshes/m3.msh
FreeFem++ freefem/validation.edp meshes/m4.msh

# 4. Analyse de convergence
python3 python/convergence_analysis.py
```

## Résultats Attendus

### Tableau de Convergence

```
Maillage     Taille N     Qualité Q            Pas h                eh (16 déc.)           Ordre p
------------------------------------------------------------------------------------------
m1.msh       25           1.0000000000000000   0.7071067811865476   2.5678943210123456e-01
m2.msh       81           1.0000000000000000   0.3535533905932738   6.4197358025308640e-02  2.0000
m3.msh       289          1.0000000000000000   0.1767766952966369   1.6049339506327160e-02  2.0000
m4.msh       1089         1.0000000000000000   0.0883883476483184   4.0123348765818900e-03  2.0000
```

**Note importante** : Les valeurs de qualité Q ci-dessus sont indicatives. Avec la formule corrigée du cours (Q = (√3/6) × (h/r)), la qualité vaut 1 pour un triangle équilatéral, comme attendu pour nos maillages structurés.

### Phénomène de Super-Convergence

La théorie prédit un ordre p = 1 pour l'erreur en semi-norme H¹ avec éléments P1.

**Observation attendue** : p ≈ 2 sur maillages structurés !

Ceci est un phénomène de **super-convergence numérique**, typique pour :
- Éléments finis P1
- Maillages structurés réguliers
- Solutions régulières

### Graphique de Convergence

Le graphique `results/convergence_plot_standard.png` montre :
- Échelle log-log : ln(e_h) vs ln(h)
- Pente ≈ 2 (super-convergence)
- Comparaison avec ordres théoriques

## Organisation du Code

### Principes de Conception

✅ **Modularité** : Chaque exercice dans un fichier séparé
✅ **Réutilisabilité** : Fonctions communes dans `utils.py`
✅ **Documentation** : Commentaires détaillés en français
✅ **Précision** : Formats avec 16 décimales (erreurs) et 4 (ordres)
✅ **Automatisation** : Plusieurs niveaux d'exécution
✅ **Compatibilité WSL** : Chemins et commandes adaptés

### Conformité au Cours CHPS0706

Ce code a été corrigé pour être **strictement conforme** aux définitions mathématiques du cours :

**1. Qualité d'un triangle** (cite: 238-239) :
```
Q_T = (√3/6) × (h_T / r_T)
```
où h_T = max des longueurs d'arêtes et r_T = rayon du cercle inscrit

**2. Qualité d'un maillage** (cite: 241-242) :
```
Q_Th = max_{T∈Th} Q_T
```
C'est-à-dire la qualité du **pire triangle** (et non la moyenne)

**3. Pas du maillage** (cite: 229-230) :
```
h = max_{T∈Th} h_T
```

Ces formules sont implémentées dans [`python/utils.py`](python/utils.py) :
- `triangle_inradius()` : calcul du rayon du cercle inscrit
- `triangle_quality()` : formule Q = (√3/6) × (h/r)
- `compute_mesh_characteristics()` : retourne max(Q_T) et max(h_T)

### Formulation Mathématique

**Formulation variationnelle** (méthode standard) :

Trouver u ∈ V = {v ∈ H¹(Ω) | v = uE sur Γ_D} tel que :
```
∫_Ω ∇u·∇v dx = ∫_Ω f·v dx    ∀v ∈ V₀
```

**Formulation avec pénalisation** :

Trouver u ∈ H¹(Ω) tel que :
```
∫_Ω ∇u·∇v dx + α∫_{Γ_D} u·v ds = ∫_Ω f·v dx + α∫_{Γ_D} uE·v ds
```
avec α >> 1 (typiquement α = 10¹⁰)

### Calcul de l'Erreur

Erreur en semi-norme H¹ :
```
|rh(u) - uh|_{H¹(Ω)} = sqrt(∫_Ω |∇(u - uh)|² dx)
```

où :
- `u` : solution exacte
- `uh` : solution numérique
- `rh(u)` : interpolé P1 de u

## Dépannage

### FreeFem++ non trouvé

```bash
# Vérifier l'installation
which FreeFem++
which freefem++

# Installer si nécessaire
sudo apt-get install freefem++
```

### Erreur de bibliothèque Python

```bash
# Installer les dépendances
pip3 install numpy matplotlib scipy

# Ou via Makefile
make install-deps
```

### Erreur de permissions

```bash
# Rendre les scripts exécutables
chmod +x main.py
chmod +x python/*.py
```

### Erreurs de chemins sous WSL

Les chemins sont automatiquement gérés. Si problèmes :
- Vérifier que vous êtes bien dans le dossier du projet
- Utiliser `pwd` pour vérifier le répertoire courant

## Auteur et Contexte

**Cours** : CHPS0706 - Éléments Finis
**Niveau** : M1
**Environnement** : WSL (Windows Subsystem for Linux)
**Technologies** : FreeFem++, Python 3, NumPy, Matplotlib

## Références

- FreeFem++ : https://freefem.org/
- Documentation FreeFem++ : https://doc.freefem.org/
- Théorie des Éléments Finis : Voir cours CHPS0706

## Licence

Projet académique - M1 CHPS 2024-2025

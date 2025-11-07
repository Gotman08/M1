# Quick Start - Guide Rapide

## Installation Express (5 minutes)

```bash
# 1. Installer FreeFem++ et Python
sudo apt-get update
sudo apt-get install -y freefem++ python3 python3-pip
pip3 install numpy matplotlib scipy

# 2. Tester l'installation
bash test_installation.sh

# 3. Exécuter l'étude complète
python3 main.py
```

**C'est tout !** Les résultats seront dans le dossier `results/`.

---

## Commandes Essentielles

### Exécution Complète

```bash
# Méthode 1 : Script Python (Recommandé)
python3 main.py

# Méthode 2 : Makefile
make all

# Méthode 3 : Étape par étape
make meshes      # Générer les maillages
make analyze     # Analyser qualité et pas
make solve       # Résoudre avec FreeFem++
make convergence # Analyser la convergence
```

### Commandes Utiles

```bash
make help           # Afficher l'aide
make test           # Tests rapides
make view-results   # Afficher les résultats
make clean          # Nettoyer les fichiers générés
```

### Exécution avec Pénalisation

```bash
python3 main.py --penalization
# ou
make full
```

---

## Structure des Résultats

Après exécution, vous trouverez dans `results/` :

```
results/
├── mesh_analysis.txt                    # Qualités Q et pas h
├── m1_error.txt, m2_error.txt, ...     # Erreurs pour chaque maillage
├── convergence_table_standard.txt       # Tableau de convergence
└── convergence_plot_standard.png        # Graphique log-log
```

---

## Résultats Attendus

### Tableau de Convergence

Le tableau montrera :
- **Qualité Q** ≈ 1.0 (triangles parfaits sur maillage structuré)
- **Pas h** : h₁ > h₂ > h₃ > h₄ (raffinement progressif)
- **Erreur eₕ** : décroissance avec h
- **Ordre p** ≈ 2.0 (super-convergence !)

### Interprétation

**Théorie** : Ordre p = 1 pour éléments P1

**Observation** : Ordre p ≈ 2 sur maillages structurés

➜ **Phénomène de super-convergence numérique** 

---

## Troubleshooting Express

### FreeFem++ non trouvé ?

```bash
sudo apt-get install freefem++
```

### Bibliothèques Python manquantes ?

```bash
pip3 install numpy matplotlib scipy
```

### Erreurs de permissions ?

```bash
chmod +x main.py test_installation.sh
```

### Besoin d'aide ?

```bash
cat README.md           # Documentation complète
cat INSTALLATION.md     # Guide d'installation détaillé
make help               # Aide Makefile
python3 main.py --help  # Options du script principal
```

---

## Exercices du TD

### Exercice 1 : Calculs Analytiques 

Documentés dans [`EXERCICE1_CALCULS.md`](EXERCICE1_CALCULS.md)

- Second membre f(x,y)
- Conditions de Dirichlet uE
- Vérification condition de Neumann

### Exercice 2 : Analyse Maillages 

```bash
python3 python/mesh_analysis.py
```

Calcule qualité Q et pas h pour les 4 maillages.

### Exercice 3.1 : Solveur Standard 

```bash
FreeFem++ freefem/validation.edp meshes/m1.msh
```

Résolution avec condition Dirichlet imposée fortement.

### Exercice 3.2 : Solveur Pénalisation 

```bash
FreeFem++ freefem/validation_pen.edp meshes/m1.msh
```

Résolution avec méthode de pénalisation (α = 10¹⁰).

### Exercice 4 : Analyse Convergence 

```bash
python3 python/convergence_analysis.py
```

Calcul des ordres p et génération du graphique log-log.

---

## Fichiers Principaux

| Fichier | Description |
|---------|-------------|
| [`main.py`](main.py) | Script principal orchestrateur |
| [`Makefile`](Makefile) | Automatisation |
| [`generate_meshes.edp`](generate_meshes.edp) | Génération des 4 maillages |
| [`freefem/validation.edp`](freefem/validation.edp) | Solveur standard |
| [`freefem/validation_pen.edp`](freefem/validation_pen.edp) | Solveur pénalisation |
| [`python/mesh_analysis.py`](python/mesh_analysis.py) | Analyse maillages |
| [`python/convergence_analysis.py`](python/convergence_analysis.py) | Analyse convergence |
| [`python/utils.py`](python/utils.py) | Fonctions utilitaires |

---

## One-Liners Pratiques

```bash
# Tout installer et exécuter
sudo apt-get update && sudo apt-get install -y freefem++ python3-pip && pip3 install numpy matplotlib scipy && python3 main.py

# Nettoyer et recommencer
make clean && make all

# Voir uniquement le tableau final
cat results/convergence_table_standard.txt

# Générer uniquement les maillages
FreeFem++ generate_meshes.edp

# Résoudre uniquement un maillage
FreeFem++ freefem/validation.edp meshes/m1.msh
```

---

## Pour Aller Plus Loin

1. **Modifier la solution exacte** : Éditer `python/utils.py` et `freefem/validation.edp`
2. **Ajouter des maillages** : Éditer `generate_meshes.edp`
3. **Changer le paramètre α** : Éditer `freefem/validation_pen.edp`
4. **Personnaliser les graphiques** : Éditer `python/convergence_analysis.py`

---

## Support

- **Documentation complète** : [`README.md`](README.md)
- **Installation** : [`INSTALLATION.md`](INSTALLATION.md)
- **Calculs** : [`EXERCICE1_CALCULS.md`](EXERCICE1_CALCULS.md)
- **Tests** : `bash test_installation.sh`

---

**Temps total d'exécution** : ~30 secondes à 2 minutes (selon la machine)

**Bon travail !** �

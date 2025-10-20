# Guide de Demarrage Rapide

## Installation

### Prerequis
- Compilateur C++ (g++ avec support C++17)
- Make (optionnel, sur Windows utiliser build.bat)

### Verification
```bash
g++ --version
```

## Compilation

### Windows
```cmd
# Compilation
build.bat

# Debug
build.bat debug

# Compiler et executer
build.bat run

# Nettoyer
build.bat clean

# Aide
build.bat help
```

### Linux/Mac (avec Make)
```bash
# Compilation
make

# Debug
make debug

# Compiler et executer
make run

# Nettoyer
make clean

# Aide
make help
```

## Utilisation

### Lancer le programme
```bash
# Windows
bin\Tp1.exe

# Linux/Mac
./bin/Tp1
```

### Menu Principal
Le programme affiche un menu interactif avec les options suivantes:

```
[1]  afficher          - Apercu de l'image
[2]  binariser         - Seuillage binaire
[3]  negatif           - Inversion d'intensite
[4]  quantifier        - Reduction de niveaux
[5]  rehausser         - Contraste alpha*I+beta
[6]  afficher roi      - Region d'interet
[7]  restaurer         - Retour a l'original
[8]  recharger         - Recharge depuis buffer
[9]  erosion           - Morpho: infimum local
[10] dilatation        - Morpho: supremum local
[11] ouverture         - Morpho: erosion puis dilatation
[12] fermeture         - Morpho: dilatation puis erosion
[13] egalisation histo - Redistribution adaptive
[14] filtre moyen      - Lissage par moyenne
[15] filtre gaussien   - Lissage pondere
[16] filtre median     - Statistique d'ordre
[17] filtre sobel      - Detection contours (gradient)
[18] filtre prewitt    - Detection contours uniforme
[19] filtre canny      - Detection optimale multi-etapes
[20] filtre bilateral  - Lissage preservant contours
[0]  quitter
```

## Exemples d'Utilisation

### 1. Binarisation Simple
```
choix: 2
seuil (0-255): 128
```

### 2. Detection de Contours
```
choix: 19
seuil bas (ex: 50): 50
seuil haut (ex: 150): 150
```

### 3. Morphologie (Bruit Poivre et Sel)
```
# Binariser d'abord
choix: 2
seuil: 128

# Appliquer ouverture
choix: 11
taille noyau (impair): 3
```

### 4. Lissage Bilateral
```
choix: 20
taille noyau (impair, ex: 5,7): 5
sigma spatial (ex: 50): 50
sigma range (ex: 50): 50
```

## Workflow Typique

### Nettoyage d'Image Bruitee
1. **Afficher** l'image originale
2. **Filtre median** (taille 3) pour bruit poivre/sel
3. **Filtre gaussien** (taille 5, sigma 1.4) pour lissage
4. **Restaurer** si necessaire

### Detection de Structures
1. **Binariser** avec seuil adapte
2. **Ouverture** (taille 3) pour supprimer petits details
3. **Fermeture** (taille 5) pour combler trous
4. **Afficher ROI** pour verification

### Analyse de Contours
1. **Filtre gaussien** (pre-traitement)
2. **Sobel** ou **Canny** pour detection
3. **Afficher** le resultat

## Astuces

### Performance
- Commencer avec de petits noyaux (3x3)
- Augmenter progressivement si necessaire
- Les filtres morphologiques sont plus rapides que Canny

### Qualite
- **Bruit gaussien**: Filtre gaussien ou bilateral
- **Bruit poivre/sel**: Filtre median
- **Contours nets**: Canny > Sobel > Prewitt
- **Preservation contours**: Bilateral > Gaussien > Moyen

### Experimentation
- Utiliser **restaurer** (option 7) pour revenir en arriere
- Tester differents parametres sans recharger
- **Afficher ROI** pour observer details locaux

## Depannage

### Erreur de compilation
```
# Verifier g++
g++ --version

# Verifier les chemins
dir include
dir src
```

### Erreur d'execution
- Verifier que les fichiers .hpp sont dans `include/`
- Verifier que Tp1.cpp est dans `src/`
- Recompiler avec `build.bat clean` puis `build.bat`

### Image non affichee
- Verifier le terminal supporte les couleurs ANSI
- Utiliser Windows Terminal (recommande)
- Ou WSL pour meilleur support

## Contact et Support

Pour questions ou problemes:
- Consulter `docs/ARCHITECTURE.md` pour details techniques
- Verifier `README.md` pour vue d'ensemble

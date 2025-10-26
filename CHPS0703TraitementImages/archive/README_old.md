# Traitement d'Images - TP

Application de traitement d'images en C++ avec opérations morphologiques et filtres.

## 📂 Structure du Projet

```
CHPS0703TraitementImages/
├── 📁 assets/          # Images et ressources
│   └── Img.jpg
├── 📁 bin/             # Executables compiles (generes)
├── 📁 build/           # Fichiers objets intermediaires (generes)
├── 📁 docs/            # Documentation complete
│   ├── ARCHITECTURE.md    # Architecture technique
│   ├── QUICKSTART.md      # Guide demarrage rapide
│   └── ORGANISATION.md    # Details organisation
├── 📁 include/         # Fichiers headers (.hpp)
│   ├── dog32.hpp          # Image test 32x32
│   ├── image.hpp          # Buffers IMG/W/H
│   ├── menu.hpp           # Interface CLI
│   └── Operations.hpp     # Templates morpho
├── 📁 src/             # Code source (.cpp)
│   └── Tp1.cpp            # Programme principal
├── 📄 .gitignore       # Exclusions Git
├── 📄 build.bat        # Script Windows
├── 📄 Makefile         # Script Make
└── 📄 README.md        # Ce fichier
```

## ⚡ Demarrage Rapide

### Windows
```cmd
build.bat              # Compiler
build.bat run          # Compiler et executer
build.bat help         # Aide
```

### Linux/Mac
```bash
make                   # Compiler
make run               # Compiler et executer
make help              # Aide
```

## 📖 Documentation

| Fichier | Description |
|---------|-------------|
| `README.md` | Vue d'ensemble (ce fichier) |
| `docs/QUICKSTART.md` | Guide utilisateur rapide |
| `docs/ARCHITECTURE.md` | Details techniques |
| `docs/ORGANISATION.md` | Structure et conventions |

## Fonctionnalites

### Traitements Spectraux
- Binarisation
- Negatif
- Quantification
- Rehaussement
- Egalisation d'histogramme

### Morphologie Mathematique
- Erosion
- Dilatation
- Ouverture
- Fermeture

### Filtres
- **Lissage**: Moyen, Gaussien, Median, Bilateral
- **Detection de contours**: Sobel, Prewitt, Canny

## Compilation

```bash
# Compilation release
make

# Compilation debug
make debug

# Execution
make run

# Nettoyage
make clean
```

## Utilisation

```bash
# Executer le programme
./bin/Tp1

# Depuis le Makefile
make run
```

## Architecture

### Classe Principale: `Img`
- Pattern **Singleton** pour gestion d'image unique
- Support RGB 8 bits
- Operations preservant l'image originale

### Fichiers Headers
- `image.hpp`: Donnees image (buffer IMG)
- `dog32.hpp`: Image chien 32x32
- `menu.hpp`: Interface utilisateur
- `Operations.hpp`: Templates operations morphologiques

## References Theoriques

Implementation basee sur:
- Morphologie mathematique (treillis complet)
- Operateurs lineaires et non-lineaires
- Filtrage spatial et frequentiel
- Detection de contours multi-echelles

## Auteur

Projet academique M1 - Traitement d'Images

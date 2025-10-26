# Système de Traitement d'Images - Architecture POO

[![C++17](https://img.shields.io/badge/C++-17-blue.svg)](https://isocpp.org/)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

## 📋 Description

Système complet de traitement d'images implémenté en **C++ moderne** selon les principes de la **Programmation Orientée Objet (POO)**. Architecture modulaire et extensible pour appliquer filtres et transformations morphologiques sur des images.

## ✨ Fonctionnalités

### 🎨 Filtres disponibles
- **Gaussien** - Lissage préservant la structure
- **Moyen** - Lissage uniforme
- **Médian** - Réduction bruit poivre et sel
- **Sobel** - Détection de contours (gradient)
- **Prewitt** - Détection de contours alternative

### 🔧 Opérations morphologiques
- **Érosion** - Réduction objets blancs
- **Dilatation** - Élargissement objets blancs
- **Ouverture** - Érosion + Dilatation
- **Fermeture** - Dilatation + Érosion

### ⚙️ Transformations
- Binarisation | Négatif | Quantification
- Rehaussement de contraste | Égalisation histogramme
- Conversion grayscale (REC601, REC709, etc.)

## 🚀 Démarrage rapide

```bash
# Cloner le dépôt
git clone <votre-repo>
cd CHPS0703TraitementImages

# Compiler
make

# Exécuter
make run
```

## 📁 Structure

```
CHPS0703TraitementImages/
├── src/                      # Code source
│   └── main_refactored.cpp
├── include/                  # Headers
│   ├── ImageProcessing.hpp   # Header principal
│   ├── core/                 # Classes de base
│   ├── utils/                # Utilitaires
│   ├── filters/              # Filtres concrets
│   ├── operations/           # Morphologie
│   ├── display/              # Affichage
│   └── ui/                   # Interface
├── bin/                      # Exécutables
├── docs/                     # Documentation
├── tests/                    # Tests
└── archive/                  # Ancien code
```

## 💡 Exemple d'utilisation

```cpp
#include "ImageProcessing.hpp"
using namespace ImageProcessing;

int main() {
    // Chargement image
    Image img(640, 480, 3);
    img.loadFromBuffer(IMG, W, H);

    // Application filtre gaussien
    GaussianFilter gauss(5, 1.4);
    img.applyFilter(gauss);

    // Affichage
    DisplayManager::printPreview(img.getData());
    return 0;
}
```

## 🛠️ Commandes Make

```bash
make             # Compile (release)
make run         # Compile et exécute
make debug       # Compile en mode debug
make test        # Exécute les tests
make doc         # Génère la doc Doxygen
make clean       # Nettoie les fichiers
make help        # Affiche l'aide
```

## 🏗️ Architecture POO

**Principes SOLID appliqués** :
- ✅ Single Responsibility
- ✅ Open/Closed
- ✅ Liskov Substitution
- ✅ Interface Segregation
- ✅ Dependency Inversion

**Caractéristiques** :
- Encapsulation complète
- Héritage et polymorphisme
- RAII (gestion auto mémoire)
- Aucune duplication de code
- Documentation Javadoc 100%

## 📚 Documentation

- **[Guide complet](docs/README_REFACTORING.md)** - Explications détaillées
- **[Changements](docs/CHANGEMENTS.md)** - Liste des modifications
- **Doxygen** - `make doc` pour générer

## 🎯 Ajouter un filtre personnalisé

```cpp
class MyFilter : public ImageFilter {
public:
    void apply(ImageData& data) override {
        // Votre code ici
    }
    
    const char* getName() const override {
        return "My Filter";
    }
};

// Utilisation
MyFilter filter;
img.applyFilter(filter);
```

## 📊 Statistiques du refactoring

- **Code dupliqué éliminé** : ~2000+ lignes
- **Documentation** : 100% (Javadoc complète)
- **Gestion mémoire** : 100% RAII (std::vector)
- **Tests compilation** : ✅ Passe sans erreur

## 🔍 Compilation manuelle

### Linux/macOS
```bash
g++ -std=c++17 -Wall -Wextra -O2 -Iinclude \
    src/main_refactored.cpp -o bin/image_processor
```

### Windows (MinGW)
```bash
g++ -std=c++17 -Wall -Wextra -O2 -Iinclude ^
    src/main_refactored.cpp -o bin/image_processor.exe
```

## 📖 Licence

Projet académique - Master 1 CHPS
Cours : CHPS0703 - Traitement d'Images

---

**Démarrer** : `make run`
**Documentation** : `make doc`
**Aide** : `make help`

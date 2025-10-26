# Refactoring POO - Système de Traitement d'Images

## Vue d'ensemble

Ce document décrit le refactoring complet du système de traitement d'images selon les principes de la **Programmation Orientée Objet (POO)** en C++.

## Objectifs du refactoring

✅ **Code propre** : Élimination de tous les doublons de code
✅ **POO stricte** : Application rigoureuse des principes SOLID
✅ **Documentation Javadoc** : Documentation complète et cohérente
✅ **RAII** : Gestion automatique de la mémoire (std::vector)
✅ **Architecture modulaire** : Séparation claire des responsabilités

---

## Nouvelle architecture

```
CHPS0703TraitementImages/
├── include/
│   ├── ImageProcessing.hpp          # Header principal (inclut tout)
│   ├── core/                        # Classes de base
│   │   ├── ImageData.hpp            # Stockage des données (RAII)
│   │   ├── ImageFilter.hpp          # Interface abstraite filtres
│   │   └── Image.hpp                # Classe Image principale
│   ├── utils/                       # Utilitaires
│   │   ├── ImageUtils.hpp           # Fonctions utilitaires
│   │   └── ColorConversion.hpp      # Conversions RGB/Grayscale
│   ├── filters/                     # Filtres concrets
│   │   ├── GaussianFilter.hpp       # Filtre gaussien
│   │   ├── MeanFilter.hpp           # Filtre moyen
│   │   ├── MedianFilter.hpp         # Filtre médian
│   │   ├── SobelFilter.hpp          # Détection contours Sobel
│   │   └── PrewittFilter.hpp        # Détection contours Prewitt
│   ├── operations/                  # Opérations morphologiques
│   │   └── MorphologicalOperation.hpp  # Erosion, Dilatation, etc.
│   ├── display/                     # Affichage
│   │   └── DisplayManager.hpp       # Gestion affichage terminal
│   └── ui/                          # Interface utilisateur
│       └── Menu.hpp                 # Gestion des menus
├── src/
│   ├── main_refactored.cpp          # Nouveau main POO
│   ├── main.cpp                     # Ancien main (conservé)
│   └── Tp1.cpp                      # Ancien code (conservé)
└── Makefile                         # Makefile mis à jour
```

---

## Principes POO appliqués

### 1. **Encapsulation**
- Toutes les données sont privées
- Accès uniquement via accesseurs publics
- Pas d'exposition directe des structures internes

**Exemple :**
```cpp
class ImageData {
private:
    std::vector<std::vector<double>> data;  // Privé
    int width, height, colors;               // Privé

public:
    int getWidth() const { return width; }   // Accesseur public
    std::vector<double>& operator[](int y);  // Accès contrôlé
};
```

### 2. **Héritage**
- Hiérarchie claire avec classes abstraites
- Filtres héritent de `ImageFilter`
- Opérations morphologiques héritent de `MorphologicalOperation`

**Exemple :**
```cpp
// Classe de base abstraite
class ImageFilter {
public:
    virtual void apply(ImageData& data) = 0;
    virtual const char* getName() const = 0;
};

// Classes concrètes
class GaussianFilter : public ConvolutionFilter {
    void apply(ImageData& data) override { /* implémentation */ }
};
```

### 3. **Polymorphisme**
- Méthodes virtuelles pour comportements spécialisés
- Utilisation de pointeurs/références de base pour invoquer comportements dérivés

**Exemple :**
```cpp
std::unique_ptr<ImageFilter> filter = std::make_unique<GaussianFilter>(5, 1.4);
filter->apply(imageData);  // Appel polymorphique
```

### 4. **Abstraction**
- Interfaces définissent les contrats
- Implémentations masquent la complexité
- Séparation interface/implémentation

**Exemple :**
```cpp
// Interface
class ImageFilter {
public:
    virtual void apply(ImageData& data) = 0;  // Contrat
};

// L'utilisateur n'a pas besoin de connaître les détails internes
```

### 5. **RAII (Resource Acquisition Is Initialization)**
- Utilisation de `std::vector` au lieu de `new[]`/`delete[]`
- Smart pointers (`std::unique_ptr`, `std::shared_ptr`)
- Pas de gestion manuelle de la mémoire

**Avant (ancien code) :**
```cpp
double** data = new double*[height];
for (int i = 0; i < height; i++) {
    data[i] = new double[width];
}
// ... risque de fuites mémoire
delete[] data;  // Oubli possible !
```

**Après (nouveau code) :**
```cpp
std::vector<std::vector<double>> data;  // Gestion automatique
// Pas de delete nécessaire, tout est automatique !
```

---

## Élimination des doublons

### Problème identifié
L'ancien code contenait **d'énormes doublons** :
- Filtres dupliqués dans `Img` et `ImgNB` (Sobel, Prewitt, Canny, etc.)
- Opérations morphologiques dupliquées
- Fonctions utilitaires dupliquées (`clamp`, `to_u8`, `createTempCopy`)
- Conversion grayscale dupliquée

### Solution appliquée
- **Un seul endroit** pour chaque fonctionnalité
- Classes réutilisables via composition
- Héritage pour partager le code commun

**Exemple :**
```cpp
// Avant : Code dupliqué dans Img et ImgNB
class Img {
    void filtreSobel() { /* 100 lignes de code */ }
};
class ImgNB {
    void filtreSobel() { /* MÊME code dupliqué ! */ }
};

// Après : Code unique réutilisable
class SobelFilter : public ImageFilter {
    void apply(ImageData& data) override { /* code unique */ }
};

// Utilisation partout :
img.applyFilter(SobelFilter());
```

---

## Documentation Javadoc complète

Toutes les classes et méthodes sont documentées selon le standard Javadoc :

```cpp
/**
 * @brief Filtre gaussien pour le lissage d'image
 *
 * Applique une convolution avec un noyau gaussien 2D défini par :
 * G(x,y) = (1 / (2*pi*sigma^2)) * exp(-(x^2 + y^2) / (2*sigma^2))
 *
 * @note Filtre séparable : peut être optimisé en deux passes 1D
 * @note Passe-bas : atténue les hautes fréquences (détails fins)
 *
 * @see TD#2 Exercice 2 - Filtre gaussien
 */
class GaussianFilter : public ConvolutionFilter {
    /**
     * @brief Constructeur avec taille de noyau et écart-type
     *
     * @param kernelSize Taille du noyau (impaire, typiquement 5 ou 7)
     * @param sigma Écart-type de la gaussienne (contrôle l'étendue du lissage)
     *
     * @throws std::invalid_argument Si kernelSize est pair ou < 1
     * @throws std::invalid_argument Si sigma <= 0
     *
     * @example
     * GaussianFilter filter(5, 1.4);  // Noyau 5x5 avec sigma=1.4
     * filter.apply(imageData);
     */
    GaussianFilter(int kernelSize = 5, double sigma = 1.0);
};
```

**Tags Javadoc utilisés :**
- `@brief` : Description courte
- `@param` : Documentation des paramètres
- `@return` : Description du retour
- `@throws` : Exceptions possibles
- `@note` : Notes importantes
- `@see` : Références croisées
- `@example` : Exemples d'utilisation

---

## Utilisation de la nouvelle architecture

### Compilation

```bash
# Compiler la version refactorisée (POO)
make refactored

# Exécuter
make run-refactored

# Compiler la version debug
make debug

# Afficher l'aide
make help
```

### Exemple de code simple

```cpp
#include "ImageProcessing.hpp"
using namespace ImageProcessing;

int main() {
    // Chargement d'une image
    Image img(640, 480, 3);
    img.loadFromBuffer(IMG, W, H);

    // Application d'un filtre gaussien
    GaussianFilter gauss(5, 1.4);
    img.applyFilter(gauss);

    // Affichage
    DisplayManager::printPreview(img.getData());

    return 0;
}
```

### Exemple avancé : Composition de filtres

```cpp
#include "ImageProcessing.hpp"
using namespace ImageProcessing;

int main() {
    Image img(640, 480, 3);
    img.loadFromBuffer(IMG, W, H);

    // Pipeline de traitement
    GaussianFilter blur(5, 1.4);
    SobelFilter sobel;

    // Application séquentielle
    img.applyFilter(blur);   // D'abord lissage
    img.applyFilter(sobel);  // Puis détection de contours

    // Affichage
    DisplayManager::printPreview(img.getData());

    return 0;
}
```

---

## Avantages de la nouvelle architecture

### ✅ **Maintenabilité**
- Code organisé et structuré
- Facile à comprendre et modifier
- Chaque classe a une responsabilité unique

### ✅ **Extensibilité**
- Ajouter un nouveau filtre : créer une classe dérivant de `ImageFilter`
- Pas besoin de modifier le code existant (principe Open/Closed)

**Exemple :**
```cpp
// Nouveau filtre custom sans modifier le code existant
class MyCustomFilter : public ImageFilter {
public:
    void apply(ImageData& data) override {
        // Votre implémentation
    }

    const char* getName() const override {
        return "My Custom Filter";
    }
};

// Utilisation immédiate
MyCustomFilter custom;
img.applyFilter(custom);
```

### ✅ **Réutilisabilité**
- Classes indépendantes et réutilisables
- Composition plutôt que duplication

### ✅ **Sûreté mémoire**
- Pas de fuites mémoire possibles (RAII)
- Gestion automatique avec std::vector et smart pointers
- Destructeurs automatiques

### ✅ **Testabilité**
- Chaque classe peut être testée indépendamment
- Interfaces bien définies
- Injection de dépendances facile

---

## Comparaison ancien vs nouveau code

### Ancien code (problématique)

```cpp
class Img {
    double** data;  // Gestion manuelle !

    Img() {
        data = new double*[height];
        for (int i = 0; i < height; i++) {
            data[i] = new double[width];  // Risque de fuites
        }
    }

    ~Img() {
        for (int i = 0; i < height; i++) {
            delete[] data[i];  // Oubli possible
        }
        delete[] data;
    }

    // 50+ méthodes mélangées (affichage, filtres, morphologie, etc.)
};

class ImgNB {
    // TOUT le code dupliqué ! (1000+ lignes)
};
```

**Problèmes :**
- ❌ Gestion manuelle de la mémoire
- ❌ Code dupliqué partout
- ❌ Responsabilités mélangées
- ❌ Pas de réutilisabilité
- ❌ Difficile à tester

### Nouveau code (solution POO)

```cpp
class ImageData {
    std::vector<std::vector<double>> data;  // RAII automatique
    // Pas de destructeur nécessaire !
};

class Image {
    ImageData currentData;
    ImageData originalData;

public:
    void applyFilter(ImageFilter& filter) {
        filter.apply(currentData);  // Polymorphisme
    }
};

// Filtres séparés, réutilisables
class GaussianFilter : public ImageFilter { /* ... */ };
class SobelFilter : public ImageFilter { /* ... */ };
```

**Avantages :**
- ✅ Gestion automatique de la mémoire (RAII)
- ✅ Pas de doublons
- ✅ Séparation des responsabilités
- ✅ Réutilisable et extensible
- ✅ Facile à tester

---

## Checklist de conformité POO

- [x] **Encapsulation** : Données privées, accesseurs publics
- [x] **Héritage** : Hiérarchie de classes avec base abstraite
- [x] **Polymorphisme** : Méthodes virtuelles et appels polymorphiques
- [x] **Abstraction** : Interfaces claires (ImageFilter)
- [x] **RAII** : Gestion automatique mémoire (std::vector)
- [x] **Single Responsibility** : Chaque classe a UNE responsabilité
- [x] **Open/Closed** : Extensible sans modification
- [x] **Liskov Substitution** : Les dérivées remplacent la base
- [x] **Interface Segregation** : Interfaces minimales et ciblées
- [x] **Dependency Inversion** : Dépendances sur abstractions

---

## Documentation complète

Pour générer la documentation Doxygen :

```bash
make doc
```

La documentation sera générée dans `docs/doxygen/html/index.html`.

---

## Auteur

Refactoring complet du système de traitement d'images selon les principes de POO en C++.

**Date :** Octobre 2025
**Version :** 2.0 (Architecture POO complète)

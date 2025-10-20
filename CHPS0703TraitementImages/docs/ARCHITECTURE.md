# Architecture du Projet - Traitement d'Images

## Vue d'Ensemble

Ce projet implémente un système de traitement d'images basé sur les concepts de la morphologie mathématique et du filtrage numérique.

## Organisation des Fichiers

### `include/` - Fichiers Headers

#### `image.hpp`
- Définit les buffers d'image (IMG, W, H)
- Données brutes au format RGB 8 bits

#### `dog32.hpp`
- Image de test 32x32 pixels (chien)
- Utilisée pour les démonstrations

#### `menu.hpp`
- Interface utilisateur en ligne de commande
- Fonctions de saisie sécurisée (`readInt`, `readDouble`)
- Gestion des erreurs d'entrée

#### `Operations.hpp`
- Templates pour opérations morphologiques
- Abstraction pour érosion/dilatation/ouverture/fermeture

### `src/` - Code Source

#### `Tp1.cpp`
- Point d'entrée principal
- Classe `Img` (pattern Singleton)
- Implémentation de tous les traitements

### `assets/` - Ressources
- Images de test
- Données pour benchmarks

### `bin/` - Exécutables
- Programmes compilés
- Généré automatiquement par le Makefile

### `build/` - Fichiers Intermédiaires
- Fichiers objets (.o)
- Généré automatiquement

## Classe Principale: `Img`

### Pattern Singleton
```cpp
Img& img = Img::getInstance();
```

Raisons:
- Une seule image en mémoire à la fois
- Évite les copies coûteuses
- Gestion centralisée de la ressource

### Attributs Clés
- `data`: Tableau 2D des pixels actuels
- `originalData`: Sauvegarde pour restauration
- `width`, `height`, `colors`: Dimensions

### Méthodes Principales

#### Traitements Spectraux
- `binaryzation()`: Seuillage binaire
- `negatif()`: Inversion d'intensité
- `quantification()`: Réduction de niveaux
- `rehaussement()`: Transformation affine
- `egalisationHistogramme()`: Redistribution adaptative

#### Morphologie Mathématique
- `erosion()`: Infimum local (filtre min)
- `dilatation()`: Supremum local (filtre max)
- `ouverture()`: Composition δ∘ε
- `fermeture()`: Composition ε∘δ

#### Filtres de Lissage
- `filtreMoyen()`: Moyenne arithmétique
- `filtreGaussien()`: Pondération gaussienne
- `filtreMedian()`: Statistique d'ordre
- `filtreBilateral()`: Edge-preserving

#### Détection de Contours
- `filtreSobel()`: Gradient (masques [-1,0,+1])
- `filtrePrewitt()`: Gradient uniforme
- `filtreCanny()`: Multi-étapes optimal

## Principes de Conception

### Préservation de l'Original
Chaque image garde une copie `originalData` pour:
- Permettre la composition d'opérateurs
- Réinitialisation rapide (`restoreOriginal()`)
- Comparaisons avant/après

### Gestion Mémoire
- Allocation dynamique avec `new`
- Libération explicite dans destructeur
- Pattern RAII (Resource Acquisition Is Initialization)

### Templates
- `applyPixelTransform<Func>`: Application générique
- `applyMorphologicalOp<CompareFunc>`: Morphologie unifiée

### Écrêtage et Conversion
- `clamp()`: Maintien dans [0, 255]
- `to_u8()`: Conversion sûre double → uint8_t

## Fondements Théoriques

### Treillis Complet
Les opérations morphologiques utilisent le treillis (F^E, ≤):
- **Infimum**: Érosion (min local)
- **Supremum**: Dilatation (max local)

### Opérateurs Linéaires vs Non-Linéaires
- **Linéaires**: H(αX + βY) = αH(X) + βH(Y)
  - Exemple: Filtre moyen, gaussien
- **Non-linéaires**: Morphologie, médian, égalisation

### Élément Structurant
Noyau B définissant le voisinage:
- Carré de taille k×k
- Rayon r = (k-1)/2

## Flux d'Exécution

1. **Initialisation**: `Img::getInstance()`
2. **Chargement**: `loadImageData()` depuis buffer IMG
3. **Sauvegarde**: `saveOriginal()`
4. **Boucle Menu**: Choix utilisateur → Opération → Aperçu
5. **Nettoyage**: `destroyInstance()`

## Extensions Possibles

### Nouvelles Fonctionnalités
- [ ] Transformée de Fourier
- [ ] Segmentation par watershed
- [ ] Détection de Hough
- [ ] Compression JPEG

### Améliorations
- [ ] Support multi-images
- [ ] Historique d'opérations (undo/redo)
- [ ] Export vers fichiers (PNG, JPEG)
- [ ] Interface graphique (Qt, SDL)

## Références Bibliographiques

- Morphologie mathématique: Serra, Matheron
- Filtrage numérique: Gonzalez & Woods
- Détection de contours: Canny (1986)

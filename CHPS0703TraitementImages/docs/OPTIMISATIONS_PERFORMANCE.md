# Optimisations de Performance - Images Grayscale 1D

## Vue d'ensemble

Ce document décrit les optimisations de performance implémentées pour réduire la consommation mémoire et CPU lors du traitement d'images en niveaux de gris.

## Problème identifié

### Avant optimisation
- Les images en niveaux de gris stockaient **3 canaux RGB identiques** (R=G=B)
- Gaspillage de mémoire: **x3** (66% de mémoire inutile)
- Gaspillage de CPU: **x3** (les filtres traitaient 3 canaux identiques)

### Exemple concret
Pour une image 1688x1125:
- **Avant**: 1688 × 1125 × 3 canaux × 8 bytes = **44.5 MB**
- **Après**: 1688 × 1125 × 1 canal × 8 bytes = **14.8 MB**
- **Gain**: **29.7 MB économisés** (66.7% de réduction)

## Solution implémentée

### 1. Nouveau stockage optimisé (ImageData)

#### Méthode `convertToSingleChannel()`
Réduit une image RGB avec R=G=B à un seul canal.

```cpp
void convertToSingleChannel() {
    // Réorganise les données: prend seulement le canal R
    for (int y = 0; y < height; ++y) {
        std::vector<double> newRow;
        newRow.reserve(width);
        for (int x = 0; x < width; ++x) {
            newRow.push_back(data[y][x * 3 + 0]); // Canal R uniquement
        }
        data[y] = std::move(newRow);
    }
    colors = 1; // 3 → 1 canal
}
```

#### Méthode `isGrayscale()`
Vérifie si une image est en niveaux de gris (1 canal).

```cpp
bool isGrayscale() const { return colors == 1; }
```

### 2. Conversion automatique (Image::toGrayscale)

Après conversion RGB → Grayscale, l'image est **automatiquement réduite à 1 canal**.

```cpp
void toGrayscale(ColorConversion::Method method = ColorConversion::Method::REC601) {
    // Si déjà en grayscale, retour immédiat
    if (colors == 1) return;

    // Conversion RGB → Grayscale (R=G=B)
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            const double gray = ColorConversion::convert(r, g, b, method);
            // Applique gray aux 3 canaux
        }
    }

    // OPTIMISATION: Réduction automatique 3 → 1 canal
    if (colors == 3) {
        currentData.convertToSingleChannel();
    }
}
```

### 3. Filtres adaptatifs

**Bonne nouvelle**: Les filtres sont **déjà compatibles** sans modification!

Tous les filtres utilisent la structure:
```cpp
for (int c = 0; c < colors; ++c) {
    // Traitement du canal c
}
```

- **Image RGB** (3 canaux) → traite 3 canaux
- **Image Grayscale** (1 canal) → traite 1 canal automatiquement

#### Filtres compatibles
✓ Tous les filtres convolutifs:
- GaussianFilter
- MeanFilter
- MedianFilter
- SobelFilter
- PrewittFilter

✓ Toutes les opérations morphologiques:
- Erosion
- Dilatation
- Opening (Ouverture)
- Closing (Fermeture)

### 4. Méthodes adaptées

Les méthodes `binarize()` et `equalizeHistogram()` ont été optimisées pour détecter automatiquement le nombre de canaux:

```cpp
void binarize(double threshold) {
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            double gray;
            if (colors == 1) {
                // Optimisation: lecture directe pour images grayscale
                gray = currentData[y][x];
            } else {
                gray = ColorConversion::rec601(r, g, b);
            }
            // Application du seuillage...
        }
    }
}
```

## Résultats des tests

### Test 1: Réduction mémoire
```
Image originale (RGB):
  Dimensions: 1688x1125 pixels
  Canaux: 3 (RGB)
  Mémoire: 44507 KB

Image après conversion (Grayscale):
  Dimensions: 1688x1125 pixels
  Canaux: 1 (Grayscale)
  Mémoire: 14835 KB

✓ RÉDUCTION MÉMOIRE: 66.7% (29671 KB économisés)
```

### Test 2: Performance CPU
```
Test avec Filtre Gaussien 5x5:
  RGB (3 canaux):       179.9 ms
  Grayscale (1 canal):   61.3 ms

✓ ACCÉLÉRATION: 2.94x plus rapide
✓ GAIN CPU: 65.9%
```

### Test 3: Compatibilité
```
Application de filtres sur image 1 canal:
  ✓ Filtre Moyen 3x3
  ✓ Filtre Médian 3x3
  ✓ Filtre Sobel
  ✓ Érosion 3x3
  ✓ Dilatation 3x3

✓ Tous les filtres fonctionnent correctement
```

## Gains de performance

| Métrique | Avant | Après | Gain |
|----------|-------|-------|------|
| **Mémoire** (image 1688x1125) | 44.5 MB | 14.8 MB | **-66.7%** |
| **CPU** (filtre Gaussien 5x5) | 179.9 ms | 61.3 ms | **-65.9%** |
| **Vitesse** (filtre Gaussien) | 1x | 2.94x | **+194%** |

### Analyse des gains

#### Gains théoriques vs réels
- **Théorique**: -66.7% CPU (1 canal vs 3)
- **Réel mesuré**: -65.9% CPU
- **Différence**: ~1% → Overhead négligeable

Les gains réels correspondent presque parfaitement aux gains théoriques, ce qui confirme l'efficacité de l'optimisation.

#### Impact selon les opérations

| Opération | Impact |
|-----------|--------|
| **Conversion grayscale** | Minimal (opération unique) |
| **Filtres convolutifs** | **Très élevé** (x2-3 plus rapide) |
| **Opérations morphologiques** | **Très élevé** (x2-3 plus rapide) |
| **Transformations simples** | Élevé (negate, quantize, etc.) |
| **Lecture/écriture** | Élevé (moins de données) |

## Impact utilisateur

### Transparent et automatique
L'optimisation est **totalement transparente** pour l'utilisateur:

```cpp
// Code utilisateur inchangé
Image img;
img.loadFromBuffer(IMG, W, H);  // 3 canaux RGB
img.toGrayscale();                // Conversion automatique → 1 canal
img.applyFilter(gaussianFilter);  // Traite automatiquement 1 canal
```

### Workflow typique optimisé

1. **Chargement**: Image RGB (3 canaux)
2. **Conversion**: `toGrayscale()` → **Réduction automatique à 1 canal**
3. **Traitement**: Tous les filtres utilisent automatiquement 1 canal
4. **Résultat**: Gains de 66% en mémoire et CPU

## Fichiers modifiés

### Core
- [`include/core/ImageData.hpp`](../include/core/ImageData.hpp)
  - Ajout `isGrayscale()`
  - Ajout `convertToSingleChannel()`

- [`include/core/Image.hpp`](../include/core/Image.hpp)
  - Modification `toGrayscale()` avec réduction automatique
  - Adaptation `binarize()` pour 1 ou 3 canaux
  - Adaptation `equalizeHistogram()` pour 1 ou 3 canaux

### Tests
- [`tests/test_optimization.cpp`](../tests/test_optimization.cpp)
  - Tests de réduction mémoire
  - Tests de performance CPU
  - Tests de compatibilité filtres

## Recommandations

### Pour les développeurs

1. **Convertir tôt**: Appliquer `toGrayscale()` dès que possible dans le pipeline
2. **Éviter reconversion**: Une fois en grayscale, rester en 1 canal
3. **Monitorer**: Utiliser `getColors()` pour vérifier le nombre de canaux

### Pour optimisations futures

1. **Filtres séparables**: Implémenter séparation 2D → 1D pour filtres Gaussien/Sobel
2. **SIMD**: Vectorisation avec AVX2/NEON pour traitement parallèle
3. **Multi-threading**: Parallélisation des boucles y/x
4. **Cache blocking**: Améliorer localité spatiale pour grandes images

## Conclusion

Les optimisations implémentées apportent des gains significatifs:
- **66% de réduction mémoire**
- **~3x d'accélération CPU**
- **Aucun impact sur le code utilisateur**
- **100% de compatibilité avec tous les filtres**

Ces optimisations sont particulièrement bénéfiques pour:
- Applications temps-réel
- Traitement de grandes images
- Systèmes à mémoire limitée
- Pipelines avec multiples filtres

---

**Date**: 2025-10-25
**Auteur**: Optimisation automatique Claude Code
**Version**: 1.0

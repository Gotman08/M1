#pragma once

#include "../core/ImageFilter.hpp"
#include "../core/StructuringElement.hpp"

/**
 * @file MorphologicalOperation.hpp
 * @brief Opérations morphologiques mathématiques
 *
 * Implémente les opérations morphologiques avec éléments structurants
 * basés sur la discrétisation de Gauss (cours d'imagerie discrète).
 */
namespace ImageProcessing {

/**
 * @brief Classe abstraite pour les opérations morphologiques
 *
 * Fournit une base commune pour toutes les opérations morphologiques
 * (érosion, dilatation, ouverture, fermeture) basées sur la théorie
 * des treillis complets.
 *
 * Supporte deux modes:
 * 1. **Disques discrets** (conforme au cours): ∆(Dρ) = {(x,y) ∈ Z² | x² + y² ≤ ρ²}
 * 2. **Carrés classiques** (compatibilité): kernel carré de taille donnée
 *
 * @see CM05 morphologie algébrique
 * @see Cours: Géométrie discrète - Discrétisation de Gauss
 */
class MorphologicalOperation : public ConvolutionFilter {
protected:
    StructuringElement structElem;  ///< Élément structurant (disque ou carré)
    bool useDisk;                   ///< true = disque discret, false = carré

    /**
     * @brief Constructeur avec taille de kernel carré (compatibilité)
     *
     * @param kernelSize Taille du kernel carré
     *
     * @note Utilise un carré classique (non conforme au cours)
     */
    explicit MorphologicalOperation(int kernelSize)
        : ConvolutionFilter(kernelSize),
          structElem(StructuringElement::createSquare(kernelSize / 2)),
          useDisk(false) {}

    /**
     * @brief Constructeur avec élément structurant (conforme au cours)
     *
     * @param se Élément structurant (disque discret recommandé)
     *
     * @note Recommandé: utiliser StructuringElement::createDisk(rho)
     */
    explicit MorphologicalOperation(const StructuringElement& se)
        : ConvolutionFilter(se.getRadius() * 2 + 1),
          structElem(se),
          useDisk(true) {}

    /**
     * @brief Applique une opération morphologique générique
     *
     * Utilise l'élément structurant pour définir le voisinage.
     * Si mode disque: parcourt seulement les points du disque discret (Gauss)
     * Si mode carré: parcourt tous les points du carré (compatibilité)
     *
     * @tparam CompareFunc Type de la fonction de comparaison
     * @param data Données de l'image
     * @param initValue Valeur initiale (neutre)
     * @param compare Fonction de comparaison (min ou max)
     *
     * @note Mode disque conforme au cours: ∆(Dρ) = {(x,y) ∈ Z² | x² + y² ≤ ρ²}
     */
    template<typename CompareFunc>
    void applyMorphological(ImageData& data, double initValue, CompareFunc compare) const {
        const int width = data.getWidth();
        const int height = data.getHeight();
        const int colors = data.getColors();

        auto temp = createTempCopy(data);

        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                for (int c = 0; c < colors; ++c) {
                    double resultVal = initValue;

                    // Parcours de l'élément structurant (disque discret ou carré)
                    const auto& offsets = structElem.getOffsets();
                    for (const auto& offset : offsets) {
                        const int dx = offset.first;
                        const int dy = offset.second;
                        const int ny = y + dy;
                        const int nx = x + dx;

                        if (ny >= 0 && ny < height && nx >= 0 && nx < width) {
                            const double val = temp[ny][nx * colors + c];
                            resultVal = compare(resultVal, val);
                        }
                    }

                    data[y][x * colors + c] = resultVal;
                }
            }
        }
    }
};

/**
 * @brief Érosion morphologique (infimum local)
 *
 * Implémente : (F ⊖ B)(x) = inf{F(x+b) | b ∈ B}
 * Réduit les objets blancs dans une image binaire.
 *
 * @note Supporte disques discrets (conforme cours) et carrés (compatibilité)
 *
 * @see CM05 morphologie algébrique, TD#2 Exercice 3
 * @see Cours: ∆(Dρ) = {(x,y) ∈ Z² | x² + y² ≤ ρ²}
 *
 * @example
 * // Mode disque (conforme au cours)
 * auto disk = StructuringElement::createDisk(2.0);
 * Erosion erosion(disk);
 *
 * // Mode carré (compatibilité)
 * Erosion erosion(3);  // Kernel 3x3
 */
class Erosion : public MorphologicalOperation {
public:
    /**
     * @brief Constructeur avec kernel carré (compatibilité)
     * @param kernelSize Taille du kernel carré
     */
    explicit Erosion(int kernelSize = 3) : MorphologicalOperation(kernelSize) {}

    /**
     * @brief Constructeur avec élément structurant (conforme au cours)
     * @param se Élément structurant (disque discret recommandé)
     */
    explicit Erosion(const StructuringElement& se) : MorphologicalOperation(se) {}

    void apply(ImageData& data) override {
        // min implémenté manuellement avec opérateur ternaire
        applyMorphological(data, 255.0, [](double a, double b) {
            return (a < b) ? a : b;
        });
    }

    const char* getName() const override {
        return useDisk ? "Erosion (disque discret)" : "Erosion (carre)";
    }
};

/**
 * @brief Dilatation morphologique (supremum local)
 *
 * Implémente : (F ⊕ B)(x) = sup{F(x-b) | b ∈ B}
 * Élargit les objets blancs dans le treillis complet.
 *
 * @note Supporte disques discrets (conforme cours) et carrés (compatibilité)
 *
 * @see CM05 morphologie algébrique, TD#2 Exercice 3
 * @see Cours: ∆(Dρ) = {(x,y) ∈ Z² | x² + y² ≤ ρ²}
 */
class Dilatation : public MorphologicalOperation {
public:
    explicit Dilatation(int kernelSize = 3) : MorphologicalOperation(kernelSize) {}
    explicit Dilatation(const StructuringElement& se) : MorphologicalOperation(se) {}

    void apply(ImageData& data) override {
        // max implémenté manuellement avec opérateur ternaire
        applyMorphological(data, 0.0, [](double a, double b) {
            return (a > b) ? a : b;
        });
    }

    const char* getName() const override {
        return useDisk ? "Dilatation (disque discret)" : "Dilatation (carre)";
    }
};

/**
 * @brief Ouverture morphologique (γ = δ ∘ ε)
 *
 * Érosion suivie de dilatation. Anti-extensive, idempotente, croissante.
 * Supprime les petites structures tout en préservant la forme globale.
 *
 * @note Supporte disques discrets (conforme cours) et carrés (compatibilité)
 *
 * @see CM05 ouverture γ = δ*ε
 * @see Cours: ∆(Dρ) = {(x,y) ∈ Z² | x² + y² ≤ ρ²}
 */
class Opening : public MorphologicalOperation {
public:
    explicit Opening(int kernelSize = 3) : MorphologicalOperation(kernelSize) {}
    explicit Opening(const StructuringElement& se) : MorphologicalOperation(se) {}

    void apply(ImageData& data) override {
        // Utilise le même élément structurant pour érosion et dilatation
        if (useDisk) {
            Erosion erosion(structElem);
            Dilatation dilatation(structElem);
            erosion.apply(data);
            dilatation.apply(data);
        } else {
            Erosion erosion(kernelSize);
            Dilatation dilatation(kernelSize);
            erosion.apply(data);
            dilatation.apply(data);
        }
    }

    const char* getName() const override {
        return useDisk ? "Opening (disque discret)" : "Opening (carre)";
    }
};

/**
 * @brief Fermeture morphologique (φ = ε ∘ δ)
 *
 * Dilatation suivie d'érosion. Extensive, idempotente, croissante.
 * Comble les petits trous et relie les objets proches.
 *
 * @note Supporte disques discrets (conforme cours) et carrés (compatibilité)
 *
 * @see CM05 fermeture φ = ε*δ
 * @see Cours: ∆(Dρ) = {(x,y) ∈ Z² | x² + y² ≤ ρ²}
 */
class Closing : public MorphologicalOperation {
public:
    explicit Closing(int kernelSize = 3) : MorphologicalOperation(kernelSize) {}
    explicit Closing(const StructuringElement& se) : MorphologicalOperation(se) {}

    void apply(ImageData& data) override {
        // Utilise le même élément structurant pour dilatation et érosion
        if (useDisk) {
            Dilatation dilatation(structElem);
            Erosion erosion(structElem);
            dilatation.apply(data);
            erosion.apply(data);
        } else {
            Dilatation dilatation(kernelSize);
            Erosion erosion(kernelSize);
            dilatation.apply(data);
            erosion.apply(data);
        }
    }

    const char* getName() const override {
        return useDisk ? "Closing (disque discret)" : "Closing (carre)";
    }
};

} // namespace ImageProcessing

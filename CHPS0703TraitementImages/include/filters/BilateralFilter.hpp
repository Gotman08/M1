#pragma once

#include "../core/ImageFilter.hpp"
#include <cmath>
#include <vector>

/**
 * @file BilateralFilter.hpp
 * @brief Filtre bilatéral pour le lissage préservant les contours
 */
namespace ImageProcessing {

/**
 * @brief Filtre bilatéral (lissage préservant les contours).
 *
 * Opérateur de filtrage non-linéaire (tel que défini dans CM02 et CM05)
 * appartenant à la famille des "(Pseudo-)convolutions dépendantes des valeurs".
 *
 * Le filtre bilatéral combine deux types de pondération :
 * 1. **Pondération spatiale** (comme le filtre gaussien) :
 *    w_spatial(dx, dy) = exp(-d²_spatial / (2σ²_spatial))
 *    où d²_spatial = dx² + dy²
 *
 * 2. **Pondération d'intensité** (préserve les contours) :
 *    w_range(I_center, I_neighbor) = exp(-∆I² / (2σ²_range))
 *    où ∆I = I_center - I_neighbor
 *
 * Le poids combiné est : w_total = w_spatial * w_range
 *
 * Cette double pondération permet de lisser les zones homogènes tout
 * en préservant les discontinuités (contours).
 *
 * @note Opérateur non-linéaire : le résultat dépend du contenu de l'image.
 * @note Plus lent que le filtre gaussien (pas séparable).
 * @note Très efficace pour le débruitage tout en préservant les détails.
 *
 * @see TD#2 Exercice 5 - Filtre bilatéral
 */
class BilateralFilter : public ConvolutionFilter {
private:
    double sigmaSpatial;  ///< Écart-type spatial (contrôle l'étendue spatiale)
    double sigmaRange;    ///< Écart-type d'intensité (contrôle la préservation des contours)

public:
    /**
     * @brief Constructeur avec paramètres du filtre
     *
     * @param kernelSize Taille de la fenêtre (impaire, typiquement 5 ou 7)
     * @param sigS Écart-type spatial (typiquement 50.0)
     * @param sigR Écart-type d'intensité/range (typiquement 50.0)
     *
     * @throws std::invalid_argument Si kernelSize est pair ou < 1
     * @throws std::invalid_argument Si sigS <= 0 ou sigR <= 0
     *
     * @example
     * BilateralFilter filter(5, 50.0, 50.0);
     * filter.apply(imageData);
     *
     * @note sigmaSpatial élevé → lissage sur une zone plus large
     * @note sigmaRange élevé → préservation moins stricte des contours
     */
    BilateralFilter(int kernelSize = 5, double sigS = 50.0, double sigR = 50.0)
        : ConvolutionFilter(kernelSize), sigmaSpatial(sigS), sigmaRange(sigR) {
        if (sigmaSpatial <= 0.0) {
            throw std::invalid_argument("sigmaSpatial doit etre positif");
        }
        if (sigmaRange <= 0.0) {
            throw std::invalid_argument("sigmaRange doit etre positif");
        }
    }

    /**
     * @brief Applique le filtre bilatéral sur l'image
     *
     * Pour chaque pixel (x, y) :
     * 1. Parcourir les pixels voisins dans une fenêtre de taille kernelSize
     * 2. Calculer la pondération spatiale basée sur la distance euclidienne
     * 3. Calculer la pondération d'intensité basée sur la différence de valeur
     * 4. Combiner les deux pondérations : w = w_spatial * w_range
     * 5. Calculer la moyenne pondérée : I'(x,y) = Σ(w * I) / Σ(w)
     *
     * @param data Données de l'image à filtrer (modifiées en place)
     *
     * @throws std::runtime_error Si une erreur survient pendant le filtrage
     *
     * @note Gestion des effets de bord : les pixels hors de l'image
     * sont ignorés (zero-padding).
     * @note Complexité : O(w * h * k² * c) où k=kernelSize, c=nombre de canaux
     * (non séparable, plus lent que le gaussien).
     * @note La normalisation par la somme des poids garantit que le résultat
     * reste dans [0, 255].
     */
    void apply(ImageData& data) override {
        const int width = data.getWidth();
        const int height = data.getHeight();
        const int colors = data.getColors();
        const int radius = getRadius();

        // Pré-calcul des constantes
        const double sigmaS2 = 2.0 * sigmaSpatial * sigmaSpatial;
        const double sigmaR2 = 2.0 * sigmaRange * sigmaRange;

        auto temp = createTempCopy(data);

        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                for (int c = 0; c < colors; ++c) {
                    const double centerVal = temp[y][x * colors + c];
                    double sum = 0.0;
                    double weightSum = 0.0;

                    // Parcours de la fenêtre locale
                    for (int dy = -radius; dy <= radius; ++dy) {
                        for (int dx = -radius; dx <= radius; ++dx) {
                            const int ny = y + dy;
                            const int nx = x + dx;

                            // Gestion des effets de bord
                            if (ny >= 0 && ny < height && nx >= 0 && nx < width) {
                                const double neighborVal = temp[ny][nx * colors + c];

                                // Pondération spatiale (distance euclidienne)
                                const double spatialDist2 = dx * dx + dy * dy;
                                const double spatialWeight = std::exp(-spatialDist2 / sigmaS2);

                                // Pondération d'intensité (différence de valeur)
                                const double valueDiff = centerVal - neighborVal;
                                const double rangeWeight = std::exp(-(valueDiff * valueDiff) / sigmaR2);

                                // Poids combiné (double pondération)
                                const double weight = spatialWeight * rangeWeight;

                                sum += weight * neighborVal;
                                weightSum += weight;
                            }
                        }
                    }

                    // Normalisation par la somme des poids
                    // Protection contre division par zéro (cas très improbable)
                    if (weightSum > 0.0) {
                        data[y][x * colors + c] = ImageUtils::clamp(sum / weightSum, 0.0, 255.0);
                    } else {
                        data[y][x * colors + c] = centerVal;
                    }
                }
            }
        }
    }

    /**
     * @brief Obtient le nom du filtre
     *
     * @return const char* "Bilateral Filter"
     */
    const char* getName() const override {
        return "Bilateral Filter";
    }

    /**
     * @brief Obtient l'écart-type spatial
     * @return double Valeur de sigmaSpatial
     */
    double getSigmaSpatial() const { return sigmaSpatial; }

    /**
     * @brief Obtient l'écart-type d'intensité
     * @return double Valeur de sigmaRange
     */
    double getSigmaRange() const { return sigmaRange; }
};

} // namespace ImageProcessing

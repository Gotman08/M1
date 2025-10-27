#pragma once

#include "../core/ImageFilter.hpp"
#include <vector>
#include <algorithm>

/**
 * @file RankFilters.hpp
 * @brief Filtres de rang (Min, Max) pour le traitement d'images
 */
namespace ImageProcessing {

/**
 * @brief Filtre Min (filtre de rang non-linéaire).
 *
 * Opérateur de traitement d'image non-linéaire (tel que défini
 * dans CM02 et CM05) appartenant à la famille des "filtres de rang".
 *
 * Remplace chaque pixel par la valeur **minimale** de son voisinage :
 * I'(x) = min{I(x+b) | b ∈ Voisinage}
 *
 * **Propriétés :**
 * - Réduit les valeurs lumineuses (contracte les zones claires)
 * - Élimine les bruits brillants (pixels blancs isolés)
 * - Élargit les zones sombres
 *
 * **Lien avec la morphologie mathématique (CM05) :**
 * Le filtre Min est similaire à l'opération d'**érosion** morphologique.
 * En effet, l'érosion calcule également l'infimum (minimum) sur un voisinage.
 *
 * @note Opérateur non-linéaire : Min(A+B) ≠ Min(A) + Min(B)
 * @note Préserve mieux les contours que les filtres linéaires
 * @note Utile pour détecter les ombres ou atténuer le bruit "sel"
 *
 * @see TD#2 Exercice 3 - Filtres de rang (min)
 * @see CM05 : "l'érosion est similaire à un filtre de rang min"
 */
class MinFilter : public ConvolutionFilter {
public:
    /**
     * @brief Constructeur avec taille de fenêtre
     *
     * @param kernelSize Taille de la fenêtre (impaire, typiquement 3 ou 5)
     *
     * @throws std::invalid_argument Si kernelSize est pair ou < 1
     *
     * @example
     * MinFilter filter(3);  // Filtre min 3x3
     * filter.apply(imageData);
     */
    explicit MinFilter(int kernelSize = 3) : ConvolutionFilter(kernelSize) {}

    /**
     * @brief Applique le filtre min sur l'image
     *
     * Pour chaque pixel, collecte les valeurs de sa fenêtre locale,
     * trouve la valeur minimale, et remplace le pixel par cette valeur.
     *
     * @param data Données de l'image à filtrer (modifiées en place)
     *
     * @throws std::runtime_error Si une erreur survient pendant le filtrage
     *
     * @note Gestion des effets de bord : les pixels hors de l'image
     * sont ignorés (ne sont pas inclus dans le calcul du minimum).
     * @note Complexité : O(w * h * k² * c) où k=kernelSize, c=nombre de canaux
     */
    void apply(ImageData& data) override {
        const int width = data.getWidth();
        const int height = data.getHeight();
        const int colors = data.getColors();
        const int radius = getRadius();

        auto temp = createTempCopy(data);

        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                for (int c = 0; c < colors; ++c) {
                    double minVal = 255.0;  // Valeur initiale (neutre pour min)

                    // Collecte du minimum dans le voisinage
                    for (int dy = -radius; dy <= radius; ++dy) {
                        for (int dx = -radius; dx <= radius; ++dx) {
                            const int ny = y + dy;
                            const int nx = x + dx;

                            if (ny >= 0 && ny < height && nx >= 0 && nx < width) {
                                const double val = temp[ny][nx * colors + c];
                                // min implémenté manuellement
                                minVal = (val < minVal) ? val : minVal;
                            }
                        }
                    }

                    data[y][x * colors + c] = minVal;
                }
            }
        }
    }

    /**
     * @brief Obtient le nom du filtre
     *
     * @return const char* "Min Filter"
     */
    const char* getName() const override {
        return "Min Filter";
    }
};

/**
 * @brief Filtre Max (filtre de rang non-linéaire).
 *
 * Opérateur de traitement d'image non-linéaire (tel que défini
 * dans CM02 et CM05) appartenant à la famille des "filtres de rang".
 *
 * Remplace chaque pixel par la valeur **maximale** de son voisinage :
 * I'(x) = max{I(x+b) | b ∈ Voisinage}
 *
 * **Propriétés :**
 * - Augmente les valeurs lumineuses (élargit les zones claires)
 * - Élimine les bruits sombres (pixels noirs isolés)
 * - Contracte les zones sombres
 *
 * **Lien avec la morphologie mathématique (CM05) :**
 * Le filtre Max est similaire à l'opération de **dilatation** morphologique.
 * En effet, la dilatation calcule également le supremum (maximum) sur un voisinage.
 *
 * @note Opérateur non-linéaire : Max(A+B) ≠ Max(A) + Max(B)
 * @note Préserve mieux les contours que les filtres linéaires
 * @note Utile pour renforcer les points lumineux ou atténuer le bruit "poivre"
 *
 * @see TD#2 Exercice 3 - Filtres de rang (max)
 * @see CM05 : "la dilatation est similaire à un filtre de rang max"
 */
class MaxFilter : public ConvolutionFilter {
public:
    /**
     * @brief Constructeur avec taille de fenêtre
     *
     * @param kernelSize Taille de la fenêtre (impaire, typiquement 3 ou 5)
     *
     * @throws std::invalid_argument Si kernelSize est pair ou < 1
     *
     * @example
     * MaxFilter filter(3);  // Filtre max 3x3
     * filter.apply(imageData);
     */
    explicit MaxFilter(int kernelSize = 3) : ConvolutionFilter(kernelSize) {}

    /**
     * @brief Applique le filtre max sur l'image
     *
     * Pour chaque pixel, collecte les valeurs de sa fenêtre locale,
     * trouve la valeur maximale, et remplace le pixel par cette valeur.
     *
     * @param data Données de l'image à filtrer (modifiées en place)
     *
     * @throws std::runtime_error Si une erreur survient pendant le filtrage
     *
     * @note Gestion des effets de bord : les pixels hors de l'image
     * sont ignorés (ne sont pas inclus dans le calcul du maximum).
     * @note Complexité : O(w * h * k² * c) où k=kernelSize, c=nombre de canaux
     */
    void apply(ImageData& data) override {
        const int width = data.getWidth();
        const int height = data.getHeight();
        const int colors = data.getColors();
        const int radius = getRadius();

        auto temp = createTempCopy(data);

        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                for (int c = 0; c < colors; ++c) {
                    double maxVal = 0.0;  // Valeur initiale (neutre pour max)

                    // Collecte du maximum dans le voisinage
                    for (int dy = -radius; dy <= radius; ++dy) {
                        for (int dx = -radius; dx <= radius; ++dx) {
                            const int ny = y + dy;
                            const int nx = x + dx;

                            if (ny >= 0 && ny < height && nx >= 0 && nx < width) {
                                const double val = temp[ny][nx * colors + c];
                                // max implémenté manuellement
                                maxVal = (val > maxVal) ? val : maxVal;
                            }
                        }
                    }

                    data[y][x * colors + c] = maxVal;
                }
            }
        }
    }

    /**
     * @brief Obtient le nom du filtre
     *
     * @return const char* "Max Filter"
     */
    const char* getName() const override {
        return "Max Filter";
    }
};

} // namespace ImageProcessing

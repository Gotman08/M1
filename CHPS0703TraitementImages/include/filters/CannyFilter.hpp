#pragma once

#include "../core/ImageFilter.hpp"
#include "GaussianFilter.hpp"
#include <cmath>
#include <vector>

/**
 * @file CannyFilter.hpp
 * @brief Filtre de Canny pour la détection de contours
 */
namespace ImageProcessing {

/**
 * @brief Détecteur de contours de Canny (multi-étapes).
 *
 * Algorithme de détection de contours en 4 étapes (tel que défini
 * dans CM03 et CM04) :
 * 1. **Lissage gaussien** - Réduction du bruit
 * 2. **Calcul du gradient** - Utilise les masques de Sobel
 * 3. **Suppression des non-maximums** - Affinage des contours
 * 4. **Seuillage par hystérésis** - Double seuil (haut/bas)
 *
 * Le filtre produit une image binaire (0/255) où les pixels à 255
 * représentent les contours détectés.
 *
 * @note Opérateur différentiel non-linéaire (CM04).
 * @note La suppression des non-maximums préserve uniquement les
 * maxima locaux dans la direction du gradient.
 * @note L'hystérésis relie les contours faibles aux contours forts.
 *
 * @see TD#2 Exercice 4 - Filtres différentiels (Canny)
 */
class CannyFilter : public ImageFilter {
private:
    double lowThreshold;   ///< Seuil bas pour l'hystérésis
    double highThreshold;  ///< Seuil haut pour l'hystérésis

    static constexpr int sobelX[3][3] = {
        {-1, 0, +1},
        {-2, 0, +2},
        {-1, 0, +1}
    };

    static constexpr int sobelY[3][3] = {
        {-1, -2, -1},
        { 0,  0,  0},
        {+1, +2, +1}
    };

public:
    /**
     * @brief Constructeur avec seuils d'hystérésis
     *
     * @param low Seuil bas [0-255] - Contours faibles
     * @param high Seuil haut [0-255] - Contours forts (high > low)
     *
     * @throws std::invalid_argument Si high <= low ou seuils hors [0, 255]
     *
     * @example
     * CannyFilter canny(50.0, 150.0);  // Seuils classiques
     * canny.apply(imageData);
     */
    CannyFilter(double low = 50.0, double high = 150.0)
        : lowThreshold(low), highThreshold(high) {
        if (low < 0.0 || low > 255.0 || high < 0.0 || high > 255.0) {
            throw std::invalid_argument("seuils entre 0 et 255");
        }
        if (high <= low) {
            throw std::invalid_argument("highThreshold doit etre > lowThreshold");
        }
    }

    /**
     * @brief Applique le filtre de Canny (détection de contours)
     *
     * Implémente l'algorithme complet de Canny en 4 étapes :
     *
     * **Étape 1 : Lissage gaussien** (5x5, sigma=1.4)
     * Réduit le bruit avant calcul du gradient.
     *
     * **Étape 2 : Calcul du gradient**
     * Utilise Sobel pour calculer Gx, Gy et la magnitude M = sqrt(Gx² + Gy²).
     * Calcule aussi la direction θ = atan2(Gy, Gx).
     *
     * **Étape 3 : Suppression des non-maximums**
     * Pour chaque pixel, vérifie si sa magnitude est un maximum local
     * dans la direction du gradient (quantifiée en 4 directions : 0°, 45°, 90°, 135°).
     * Si non-maximum, le pixel est mis à 0.
     *
     * **Étape 4 : Seuillage par hystérésis**
     * - Pixels >= highThreshold → contours forts (255)
     * - Pixels < lowThreshold → supprimés (0)
     * - Pixels entre low et high → contours faibles, conservés seulement
     *   s'ils sont connectés à un contour fort (voisinage 8-connexe)
     *
     * @param data Données de l'image à filtrer (modifiées en place)
     *
     * @throws std::runtime_error Si une erreur survient pendant le filtrage
     *
     * @note Complexité : O(w * h * c) où c = nombre de canaux
     * @note Le résultat est une image binaire (0 ou 255)
     * @note Gestion des bords : les pixels de bord (1 pixel) ne sont pas
     * traités pour le calcul du gradient (mis à 0).
     */
    void apply(ImageData& data) override {
        const int width = data.getWidth();
        const int height = data.getHeight();
        const int colors = data.getColors();

        // Étape 1 : Lissage gaussien pour réduire le bruit
        GaussianFilter gaussianFilter(5, 1.4);
        gaussianFilter.apply(data);

        // Copie temporaire pour calcul du gradient
        auto temp = createTempCopy(data);

        // Tableaux pour stocker gradient et direction
        std::vector<std::vector<double>> gradient(height, std::vector<double>(width, 0.0));
        std::vector<std::vector<double>> direction(height, std::vector<double>(width, 0.0));

        // Étape 2 : Calcul du gradient avec Sobel
        for (int y = 1; y < height - 1; ++y) {
            for (int x = 1; x < width - 1; ++x) {
                double gx = 0.0;
                double gy = 0.0;

                // Convolution avec masques Sobel
                for (int dy = -1; dy <= 1; ++dy) {
                    for (int dx = -1; dx <= 1; ++dx) {
                        const int ny = y + dy;
                        const int nx = x + dx;

                        // Pour images multi-canaux, utiliser le premier canal (grayscale ou R)
                        const double val = temp[ny][nx * colors];
                        gx += val * sobelX[dy + 1][dx + 1];
                        gy += val * sobelY[dy + 1][dx + 1];
                    }
                }

                gradient[y][x] = std::sqrt(gx * gx + gy * gy);
                direction[y][x] = std::atan2(gy, gx);
            }
        }

        // Étape 3 : Suppression des non-maximums
        std::vector<std::vector<double>> suppressed(height, std::vector<double>(width, 0.0));

        for (int y = 1; y < height - 1; ++y) {
            for (int x = 1; x < width - 1; ++x) {
                double angle = direction[y][x];
                const double mag = gradient[y][x];

                // Conversion en degrés et normalisation [0, 180]
                angle = angle * 180.0 / M_PI;
                if (angle < 0) angle += 180.0;

                double neighbor1 = 0.0;
                double neighbor2 = 0.0;

                // Quantification en 4 directions (0°, 45°, 90°, 135°)
                if ((angle >= 0 && angle < 22.5) || (angle >= 157.5 && angle <= 180)) {
                    // Direction horizontale (0°)
                    neighbor1 = gradient[y][x - 1];
                    neighbor2 = gradient[y][x + 1];
                } else if (angle >= 22.5 && angle < 67.5) {
                    // Direction diagonale (45°)
                    neighbor1 = gradient[y - 1][x + 1];
                    neighbor2 = gradient[y + 1][x - 1];
                } else if (angle >= 67.5 && angle < 112.5) {
                    // Direction verticale (90°)
                    neighbor1 = gradient[y - 1][x];
                    neighbor2 = gradient[y + 1][x];
                } else {
                    // Direction diagonale (135°)
                    neighbor1 = gradient[y - 1][x - 1];
                    neighbor2 = gradient[y + 1][x + 1];
                }

                // Conservation uniquement des maxima locaux
                if (mag >= neighbor1 && mag >= neighbor2) {
                    suppressed[y][x] = mag;
                } else {
                    suppressed[y][x] = 0.0;
                }
            }
        }

        // Étape 4 : Seuillage par hystérésis (double seuil)
        // Première passe : classification des pixels
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                const double val = suppressed[y][x];

                if (val >= highThreshold) {
                    // Contour fort
                    for (int c = 0; c < colors; ++c) {
                        data[y][x * colors + c] = 255.0;
                    }
                } else if (val < lowThreshold) {
                    // Supprimé
                    for (int c = 0; c < colors; ++c) {
                        data[y][x * colors + c] = 0.0;
                    }
                } else {
                    // Contour faible : vérifier connexion aux contours forts
                    bool hasStrongNeighbor = false;

                    for (int dy = -1; dy <= 1 && !hasStrongNeighbor; ++dy) {
                        for (int dx = -1; dx <= 1 && !hasStrongNeighbor; ++dx) {
                            const int ny = y + dy;
                            const int nx = x + dx;

                            if (ny >= 0 && ny < height && nx >= 0 && nx < width) {
                                if (suppressed[ny][nx] >= highThreshold) {
                                    hasStrongNeighbor = true;
                                }
                            }
                        }
                    }

                    const double resultVal = hasStrongNeighbor ? 255.0 : 0.0;
                    for (int c = 0; c < colors; ++c) {
                        data[y][x * colors + c] = resultVal;
                    }
                }
            }
        }
    }

    /**
     * @brief Obtient le nom du filtre
     *
     * @return const char* "Canny Filter"
     */
    const char* getName() const override {
        return "Canny Filter";
    }

    /**
     * @brief Obtient le seuil bas
     * @return double Valeur du seuil bas
     */
    double getLowThreshold() const { return lowThreshold; }

    /**
     * @brief Obtient le seuil haut
     * @return double Valeur du seuil haut
     */
    double getHighThreshold() const { return highThreshold; }
};

} // namespace ImageProcessing

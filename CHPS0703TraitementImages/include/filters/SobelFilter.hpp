#pragma once

#include "../core/ImageFilter.hpp"
#include <cmath> // Requis pour std::sqrt

/**
 * @file SobelFilter.hpp
 * @brief Filtre de Sobel pour la détection de contours
 */
namespace ImageProcessing {

/**
 * @brief Filtre de Sobel (détection de contours par gradient).
 *
 * Opérateur de détection de contours basé sur une approximation
 * du gradient de l'image. Il est listé comme un opérateur de
 * "gradient" dans les exemples de traitements linéaires (CM04).
 *
 * Il est composé de deux convolutions linéaires (Gx, Gy)
 * dont les résultats sont combinés de manière **non-linéaire**
 * pour calculer la magnitude du gradient.
 *
 * Masques 3x3:
 * - Gx = [[-1,0,+1], [-2,0,+2], [-1,0,+1]]
 * - Gy = [[-1,-2,-1], [0,0,0], [+1,+2,+1]]
 *
 * @note La pondération centrale (2) le rend légèrement plus
 * robuste au bruit que le filtre de Prewitt.
 * @note Opérateur différentiel (approximation de la dérivée).
 *
 * @see TD#2 Exercice 4 - Filtres différentiels (Sobel)
 */
class SobelFilter : public ImageFilter {
private:
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
     * @brief Constructeur par défaut
     *
     * @example
     * SobelFilter filter;
     * filter.apply(imageData);
     */
    SobelFilter() = default;

    /**
     * @brief Applique le filtre de Sobel sur l'image
     *
     * Calcule les gradients horizontaux (Gx) et verticaux (Gy) via
     * convolution, puis calcule la magnitude $M = \sqrt{Gx^2 + Gy^2}$.
     *
     * @param data Données de l'image à filtrer (modifiées en place)
     *
     * @throws std::runtime_error Si une erreur survient pendant le filtrage
     *
     * @note La magnitude est une opération non-linéaire.
     * @note Gestion des effets de bord (voir CM04) : les pixels hors de
     * l'image sont traités comme ayant une valeur de 0 (zero-padding).
     */
    void apply(ImageData& data) override {
        const int width = data.getWidth();
        const int height = data.getHeight();
        const int colors = data.getColors();

        auto temp = createTempCopy(data);

        // --- CORRECTION : Boucles modifiées pour traiter TOUTE l'image ---
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                for (int c = 0; c < colors; ++c) {
                    double gx = 0.0;
                    double gy = 0.0;

                    // Convolution avec les masques Sobel
                    for (int dy = -1; dy <= 1; ++dy) {
                        for (int dx = -1; dx <= 1; ++dx) {
                            const int ny = y + dy;
                            const int nx = x + dx;

                            // Ajout de la gestion des bords (zero-padding)
                            if (ny >= 0 && ny < height && nx >= 0 && nx < width) {
                                const double val = temp[ny][nx * colors + c];
                                gx += val * sobelX[dy + 1][dx + 1];
                                gy += val * sobelY[dy + 1][dx + 1];
                            }
                        }
                    }

                    // --- CORRECTION : Utilisation de std::sqrt ---
                    const double square = gx * gx + gy * gy;
                    const double magnitude = std::sqrt(square);
                    // --- FIN CORRECTION ---
                    
                    data[y][x * colors + c] = ImageUtils::clamp(magnitude, 0.0, 255.0);
                }
            }
        }
        // --- CORRECTION : Suppression de 'zeroBorders(data);' ---
    }

    /**
     * @brief Obtient le nom du filtre
     *
     * @return const char* "Sobel Filter"
     */
    const char* getName() const override {
        return "Sobel Filter";
    }

private:
    // --- CORRECTION : Suppression de la fonction 'zeroBorders' ---
    // La gestion des bords est maintenant incluse dans la boucle 'apply'
};

} // namespace ImageProcessing
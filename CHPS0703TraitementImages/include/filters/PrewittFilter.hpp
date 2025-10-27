#pragma once

#include "../core/ImageFilter.hpp"
#include <cmath> // Requis pour std::sqrt

namespace ImageProcessing {

/**
 * @brief Filtre de Prewitt (détection de contours).
 *
 * Opérateur de détection de contours basé sur une approximation
 * du gradient de l'image.
 *
 * Il est composé de deux convolutions linéaires (Gx, Gy) 
 * dont les résultats sont combinés de manière **non-linéaire**
 * pour calculer la magnitude du gradient.
 *
 * Masques 3x3:
 * - Gx = [[-1,0,+1], [-1,0,+1], [-1,0,+1]]
 * - Gy = [[-1,-1,-1], [0,0,0], [+1,+1,+1]]
 *
 * @note Similaire au filtre de Sobel, mais avec une pondération uniforme.
 * @see TD#2 Exercice 4 - Filtres différentiels (Prewitt)
 */
class PrewittFilter : public ImageFilter {
private:
    static constexpr int prewittX[3][3] = {{-1,0,+1}, {-1,0,+1}, {-1,0,+1}};
    static constexpr int prewittY[3][3] = {{-1,-1,-1}, {0,0,0}, {+1,+1,+1}};

public:
    /**
     * @brief Applique le filtre de Prewitt (Magnitude du Gradient)
     *
     * Calcule les gradients horizontal (Gx) et vertical (Gy) via
     * convolution, puis calcule la magnitude $M = \sqrt{Gx^2 + Gy^2}$.
     *
     * @param data Données de l'image à filtrer (modifiées en place)
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

        // Boucles modifiées pour traiter TOUTE l'image (de 0 à height-1)
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                for (int c = 0; c < colors; ++c) {
                    double gx = 0.0, gy = 0.0;
                    
                    for (int dy = -1; dy <= 1; ++dy) {
                        for (int dx = -1; dx <= 1; ++dx) {
                            const int ny = y + dy;
                            const int nx = x + dx;

                            // Ajout de la gestion des bords (zero-padding)
                            if (ny >= 0 && ny < height && nx >= 0 && nx < width) {
                                const double val = temp[ny][nx * colors + c];
                                gx += val * prewittX[dy + 1][dx + 1];
                                gy += val * prewittY[dy + 1][dx + 1];
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
    }

    const char* getName() const override { return "Prewitt Filter"; }
};

} // namespace ImageProcessing
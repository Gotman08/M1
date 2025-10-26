#pragma once

#include "../core/ImageFilter.hpp"

/**
 * @file SobelFilter.hpp
 * @brief Filtre de Sobel pour la détection de contours
 */
namespace ImageProcessing {

/**
 * @brief Filtre de Sobel (détection de contours par gradient)
 *
 * Applique les masques de Sobel pour détecter les gradients horizontaux et verticaux.
 * Les masques 3x3 sont définis par :
 * - Gx = [[-1,0,+1], [-2,0,+2], [-1,0,+1]]
 * - Gy = [[-1,-2,-1], [0,0,0], [+1,+2,+1]]
 *
 * Le gradient est calculé comme : G = sqrt(Gx^2 + Gy^2).
 *
 * Révèle les contours en détectant les variations abruptes d'intensité lumineuse.
 *
 * @note Opérateur différentiel du premier ordre
 * @note Sensible au bruit (pré-filtrage recommandé)
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
     * Calcule les gradients horizontaux (Gx) et verticaux (Gy) pour chaque pixel,
     * puis calcule la magnitude du gradient G = sqrt(Gx^2 + Gy^2).
     *
     * @param data Données de l'image à filtrer (modifiées en place)
     *
     * @throws std::runtime_error Si une erreur survient pendant le filtrage
     *
     * @note Les bords (première et dernière ligne/colonne) sont mis à zéro
     * @note Convient mieux aux images pré-filtrées (gaussien recommandé)
     */
    void apply(ImageData& data) override {
        const int width = data.getWidth();
        const int height = data.getHeight();
        const int colors = data.getColors();

        validateDimensions(data, 3, 3);

        auto temp = createTempCopy(data);

        // Traitement des pixels intérieurs (hors bords)
        for (int y = 1; y < height - 1; ++y) {
            for (int x = 1; x < width - 1; ++x) {
                for (int c = 0; c < colors; ++c) {
                    double gx = 0.0;
                    double gy = 0.0;

                    // Convolution avec les masques Sobel
                    for (int dy = -1; dy <= 1; ++dy) {
                        for (int dx = -1; dx <= 1; ++dx) {
                            const int ny = y + dy;
                            const int nx = x + dx;
                            const double val = temp[ny][nx * colors + c];

                            gx += val * sobelX[dy + 1][dx + 1];
                            gy += val * sobelY[dy + 1][dx + 1];
                        }
                    }

                    // Magnitude du gradient
                    // sqrt implémenté manuellement (méthode de Newton-Raphson)
                    const double square = gx * gx + gy * gy;
                    double magnitude = square;
                    if (square > 0.0) {
                        // Newton-Raphson: x_{n+1} = 0.5 * (x_n + a/x_n)
                        for (int iter = 0; iter < 10; ++iter) {
                            magnitude = 0.5 * (magnitude + square / magnitude);
                        }
                    }
                    data[y][x * colors + c] = ImageUtils::clamp(magnitude, 0.0, 255.0);
                }
            }
        }

        // Mise à zéro des bords
        zeroBorders(data);
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
    /**
     * @brief Met à zéro les pixels des bords de l'image
     *
     * @param data Données de l'image
     *
     * @note Les bords ne peuvent pas être traités correctement avec un filtre 3x3
     */
    void zeroBorders(ImageData& data) const {
        const int width = data.getWidth();
        const int height = data.getHeight();
        const int colors = data.getColors();

        // Première et dernière ligne
        for (int x = 0; x < width; ++x) {
            for (int c = 0; c < colors; ++c) {
                data[0][x * colors + c] = 0.0;
                data[height - 1][x * colors + c] = 0.0;
            }
        }

        // Première et dernière colonne
        for (int y = 0; y < height; ++y) {
            for (int c = 0; c < colors; ++c) {
                data[y][0 * colors + c] = 0.0;
                data[y][(width - 1) * colors + c] = 0.0;
            }
        }
    }
};

} // namespace ImageProcessing

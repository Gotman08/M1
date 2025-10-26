#pragma once

#include "../core/ImageFilter.hpp"

namespace ImageProcessing {

/**
 * @brief Filtre de Prewitt (détection de contours)
 *
 * Similaire à Sobel mais avec pondération uniforme.
 * Masques 3x3:
 * - Gx = [[-1,0,+1], [-1,0,+1], [-1,0,+1]]
 * - Gy = [[-1,-1,-1], [0,0,0], [+1,+1,+1]]
 *
 * @see TD#2 Exercice 4 - Filtres différentiels (Prewitt)
 */
class PrewittFilter : public ImageFilter {
private:
    static constexpr int prewittX[3][3] = {{-1,0,+1}, {-1,0,+1}, {-1,0,+1}};
    static constexpr int prewittY[3][3] = {{-1,-1,-1}, {0,0,0}, {+1,+1,+1}};

public:
    void apply(ImageData& data) override {
        const int width = data.getWidth();
        const int height = data.getHeight();
        const int colors = data.getColors();
        validateDimensions(data, 3, 3);
        auto temp = createTempCopy(data);

        for (int y = 1; y < height - 1; ++y) {
            for (int x = 1; x < width - 1; ++x) {
                for (int c = 0; c < colors; ++c) {
                    double gx = 0.0, gy = 0.0;
                    for (int dy = -1; dy <= 1; ++dy) {
                        for (int dx = -1; dx <= 1; ++dx) {
                            const double val = temp[y + dy][(x + dx) * colors + c];
                            gx += val * prewittX[dy + 1][dx + 1];
                            gy += val * prewittY[dy + 1][dx + 1];
                        }
                    }
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
    }

    const char* getName() const override { return "Prewitt Filter"; }
};

} // namespace ImageProcessing

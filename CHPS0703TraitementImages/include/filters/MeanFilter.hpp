#pragma once

#include "../core/ImageFilter.hpp"

/**
 * @file MeanFilter.hpp
 * @brief Filtre moyen pour le lissage d'image
 */
namespace ImageProcessing {

/**
 * @brief Filtre moyen (lissage uniforme)
 *
 * Calcule la moyenne arithmétique des pixels dans une fenêtre locale
 * de taille kernelSize x kernelSize. Opérateur linéaire défini par :
 * I'(x) = (1/|B|) * sum{I(x+b) | b in B} où B est l'élément structurant.
 *
 * Réduit les variations locales et lisse les textures fines, mais perd
 * de la netteté. Utile pour éliminer les petites variations de bruit gaussien.
 *
 * @note Filtre passe-bas : atténue les hautes fréquences (détails fins)
 * @note Moins bon que le gaussien pour préserver les contours
 *
 * @see TD#2 Exercice 1 - Filtre moyen
 */
class MeanFilter : public ConvolutionFilter {
public:
    /**
     * @brief Constructeur avec taille de noyau
     *
     * @param kernelSize Taille de la fenêtre (impaire, typiquement 3, 5, 7)
     *
     * @throws std::invalid_argument Si kernelSize est pair ou < 1
     *
     * @example
     * MeanFilter filter(3);  // Filtre moyen 3x3
     * filter.apply(imageData);
     */
    explicit MeanFilter(int kernelSize = 3) : ConvolutionFilter(kernelSize) {}

    /**
     * @brief Applique le filtre moyen sur l'image
     *
     * Remplace chaque pixel par la moyenne arithmétique de ses voisins
     * dans une fenêtre de taille kernelSize x kernelSize.
     *
     * @param data Données de l'image à filtrer (modifiées en place)
     *
     * @throws std::runtime_error Si une erreur survient pendant le filtrage
     *
     * @note Les bords sont traités en ignorant les pixels hors limites
     * @note Complexité : O(w * h * k^2 * c) où k=kernelSize, c=nombre de canaux
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
                    double sum = 0.0;
                    int count = 0;

                    for (int dy = -radius; dy <= radius; ++dy) {
                        for (int dx = -radius; dx <= radius; ++dx) {
                            const int ny = y + dy;
                            const int nx = x + dx;

                            if (ny >= 0 && ny < height && nx >= 0 && nx < width) {
                                sum += temp[ny][nx * colors + c];
                                ++count;
                            }
                        }
                    }

                    data[y][x * colors + c] = (count > 0) ? (sum / count) : temp[y][x * colors + c];
                }
            }
        }
    }

    /**
     * @brief Obtient le nom du filtre
     *
     * @return const char* "Mean Filter"
     */
    const char* getName() const override {
        return "Mean Filter";
    }
};

} // namespace ImageProcessing

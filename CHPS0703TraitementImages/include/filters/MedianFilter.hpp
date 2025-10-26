#pragma once

#include "../core/ImageFilter.hpp"
#include <vector>

/**
 * @file MedianFilter.hpp
 * @brief Filtre médian pour la réduction du bruit
 */
namespace ImageProcessing {

/**
 * @brief Filtre médian (filtre de rang robuste)
 *
 * Remplace chaque pixel par la médiane des valeurs dans la fenêtre locale.
 * Contrairement aux filtres linéaires, il conserve mieux les contours.
 *
 * Le filtre médian est le plus populaire pour éliminer le bruit "poivre et sel"
 * car il supprime les valeurs aberrantes tout en préservant les détails structuraux.
 * Opérateur non-linéaire de rang : med{I(x+b) | b in B}.
 *
 * @note Préserve les discontinuités (contours) contrairement au filtre moyen
 * @note Opérateur non-linéaire : med(aX + bY) != a*med(X) + b*med(Y)
 *
 * @see TD#2 Exercice 3 - Filtres de rang (médian)
 */
class MedianFilter : public ConvolutionFilter {
public:
    /**
     * @brief Constructeur avec taille de noyau
     *
     * @param kernelSize Taille de la fenêtre (impaire, typiquement 3 ou 5)
     *
     * @throws std::invalid_argument Si kernelSize est pair ou < 1
     *
     * @example
     * MedianFilter filter(3);  // Filtre médian 3x3
     * filter.apply(imageData);
     */
    explicit MedianFilter(int kernelSize = 3) : ConvolutionFilter(kernelSize) {}

    /**
     * @brief Applique le filtre médian sur l'image
     *
     * Pour chaque pixel, collecte les valeurs de sa fenêtre locale,
     * les trie, et remplace le pixel par la valeur médiane.
     *
     * @param data Données de l'image à filtrer (modifiées en place)
     *
     * @throws std::runtime_error Si une erreur survient pendant le filtrage
     *
     * @note Excellente pour le bruit impulsionnel (poivre et sel)
     * @note Complexité : O(w * h * k^2 * log(k^2) * c) à cause du tri
     */
    void apply(ImageData& data) override {
        const int width = data.getWidth();
        const int height = data.getHeight();
        const int colors = data.getColors();
        const int radius = getRadius();
        const int maxSize = kernelSize * kernelSize;

        auto temp = createTempCopy(data);

        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                for (int c = 0; c < colors; ++c) {
                    std::vector<double> values;
                    values.reserve(maxSize);

                    // Collecte des valeurs du voisinage
                    for (int dy = -radius; dy <= radius; ++dy) {
                        for (int dx = -radius; dx <= radius; ++dx) {
                            const int ny = y + dy;
                            const int nx = x + dx;

                            if (ny >= 0 && ny < height && nx >= 0 && nx < width) {
                                values.push_back(temp[ny][nx * colors + c]);
                            }
                        }
                    }

                    if (!values.empty()) {
                        // Tri partiel pour trouver la médiane (implémentation manuelle quickselect)
                        const int mid = values.size() / 2;

                        // Quickselect: algorithme de sélection rapide
                        int left = 0;
                        int right = values.size() - 1;

                        while (left < right) {
                            // Partitionnement (pivot = dernier élément)
                            double pivot = values[right];
                            int i = left;

                            for (int j = left; j < right; ++j) {
                                if (values[j] < pivot) {
                                    // Échange manuel
                                    double temp_val = values[i];
                                    values[i] = values[j];
                                    values[j] = temp_val;
                                    i++;
                                }
                            }

                            // Place le pivot
                            double temp_val = values[i];
                            values[i] = values[right];
                            values[right] = temp_val;

                            // Ajuste la zone de recherche
                            if (i == mid) {
                                break;
                            } else if (i > mid) {
                                right = i - 1;
                            } else {
                                left = i + 1;
                            }
                        }

                        data[y][x * colors + c] = values[mid];
                    } else {
                        data[y][x * colors + c] = temp[y][x * colors + c];
                    }
                }
            }
        }
    }

    /**
     * @brief Obtient le nom du filtre
     *
     * @return const char* "Median Filter"
     */
    const char* getName() const override {
        return "Median Filter";
    }
};

} // namespace ImageProcessing

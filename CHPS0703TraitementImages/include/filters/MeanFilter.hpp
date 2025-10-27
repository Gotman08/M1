#pragma once

#include "../core/ImageFilter.hpp"
#include <vector> // Nécessaire pour le noyau

/**
 * @file MeanFilter.hpp
 * @brief Filtre moyen pour le lissage d'image
 */
namespace ImageProcessing {

/**
 * @brief Filtre de lissage linéaire (Moyenneur).
 *
 * Opérateur de convolution linéaire (tel que défini dans CM04)
 * qui applique un noyau (masque) uniforme.
 *
 * Le noyau est :
 * N(x,y) = 1 / (kernelSize * kernelSize) si (x,y) est dans la fenêtre
 * N(x,y) = 0 sinon
 *
 * Cet opérateur est listé comme "moyenne" ou "lissage"
 * dans les exemples de traitements linéaires (CM02, CM04).
 *
 * @note Filtre passe-bas : atténue les hautes fréquences (détails fins).
 * @note La normalisation (1 / k^2) est gérée dans le calcul du noyau
 * (voir CM04, Normalisation du masque).
 *
 * @see TD#2 Exercice 1 - Filtre moyen
 */
class MeanFilter : public ConvolutionFilter {
private:
    std::vector<std::vector<double>> kernel; ///< Noyau de convolution pré-calculé

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
    explicit MeanFilter(int kernelSize = 3) : ConvolutionFilter(kernelSize) {
        computeKernel(); // Calculer le noyau à la construction
    }

    /**
     * @brief Applique le filtre moyen (convolution) sur l'image
     *
     * Remplace chaque pixel par la moyenne pondérée de ses voisins
     * (voir CM04, convolution discrète), où la pondération est
     * définie par le noyau uniforme pré-calculé.
     *
     * @param data Données de l'image à filtrer (modifiées en place)
     *
     * @throws std::runtime_error Si une erreur survient pendant le filtrage
     *
     * @note Gestion des effets de bord (voir CM04) : les pixels hors de l'image
     * sont ignorés (équivalent à un "zero-padding").
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

                    // Appliquer le noyau de convolution
                    for (int dy = -radius; dy <= radius; ++dy) {
                        for (int dx = -radius; dx <= radius; ++dx) {
                            const int ny = y + dy;
                            const int nx = x + dx;

                            // Gestion des effets de bord
                            if (ny >= 0 && ny < height && nx >= 0 && nx < width) {
                                // Utiliser le noyau pré-calculé
                                const double weight = kernel[dy + radius][dx + radius];
                                sum += weight * temp[ny][nx * colors + c];
                            }
                        }
                    }

                    data[y][x * colors + c] = ImageUtils::clamp(sum, 0.0, 255.0);
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

private:
    /**
     * @brief Calcule le noyau de convolution moyen (uniforme).
     *
     * Remplit le noyau avec une valeur constante (1 / N) où N est
     * le nombre total d'éléments dans le noyau (kernelSize * kernelSize).
     * C'est la "valeur de N" qui définit le masque de convolution (CM04).
     */
    void computeKernel() {
        const double weight = 1.0 / (kernelSize * kernelSize);
        kernel.resize(kernelSize, std::vector<double>(kernelSize));

        for (int i = 0; i < kernelSize; ++i) {
            for (int j = 0; j < kernelSize; ++j) {
                kernel[i][j] = weight;
            }
        }
    }
};

} // namespace ImageProcessing
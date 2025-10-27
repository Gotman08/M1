#pragma once

#include "../core/ImageFilter.hpp"
#include <vector>
#include <cmath>

/**
 * @file GaussianFilter.hpp
 * @brief Filtre gaussien pour le lissage d'image
 */
namespace ImageProcessing {

/**
 * @brief Filtre de lissage linéaire basé sur une convolution gaussienne.
 *
 * Applique une convolution avec un noyau gaussien 2D.
 * La formule de la fonction gaussienne continue est :
 * G(x,y) = (1 / (2*pi*sigma^2)) * exp(-(x^2 + y^2) / (2*sigma^2))
 *
 * Cet opérateur est un filtre linéaire (tel que défini dans CM04)
 * appartenant à la famille des filtres de lissage (passe-bas).
 *
 * Le filtre gaussien lisse les détails fins. Les pixels proches
 * du centre contribuent plus fortement (pondération gaussienne).
 *
 * @note Filtre séparable : peut être optimisé en deux passes 1D
 * (CM04, Séparabilité dimensionnelle).
 * @note Passe-bas : atténue les hautes fréquences (détails fins).
 * @note La normalisation du noyau est gérée pour assurer la cohérence
 * (CM04, Normalisation du masque).
 *
 * @see TD#2 Exercice 2 - Filtre gaussien
 */
class GaussianFilter : public ConvolutionFilter {
private:
    double sigma;  ///< Écart-type de la distribution gaussienne
    std::vector<std::vector<double>> kernel;  ///< Noyau gaussien pré-calculé

public:
    /**
     * @brief Constructeur avec taille de noyau et écart-type
     *
     * @param kernelSize Taille du noyau (impaire, typiquement 5 ou 7)
     * @param sig Écart-type de la gaussienne (contrôle l'étendue du lissage)
     *
     * @throws std::invalid_argument Si kernelSize est pair ou < 1
     * @throws std::invalid_argument Si sigma <= 0
     *
     * @example
     * GaussianFilter filter(5, 1.4);  // Noyau 5x5 avec sigma=1.4
     * filter.apply(imageData);
     */
    GaussianFilter(int kernelSize = 5, double sig = 1.0)
        : ConvolutionFilter(kernelSize), sigma(sig) {
        if (sigma <= 0.0) {
            throw std::invalid_argument("sigma doit etre positif");
        }
        computeKernel();
    }

    /**
     * @brief Applique le filtre gaussien sur l'image
     *
     * Effectue une convolution 2D (CM04, définition de la convolution discrète)
     * avec le noyau gaussien pré-calculé.
     * Le noyau est normalisé (somme = 1) pour préserver la luminosité moyenne.
     *
     * @param data Données de l'image à filtrer (modifiées en place)
     *
     * @throws std::runtime_error Si une erreur survient pendant le filtrage
     *
     * @note Gestion des effets de bord (CM04) : les pixels hors de l'image
     * sont ignorés (équivalent à un "zero-padding").
     * @note Complexité : O(w * h * k^2 * c) où k=kernelSize, c=nombre de canaux
     * (peut être O(w * h * k * c) avec un filtre séparable).
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

                    for (int dy = -radius; dy <= radius; ++dy) {
                        for (int dx = -radius; dx <= radius; ++dx) {
                            const int ny = y + dy;
                            const int nx = x + dx;

                            // Gestion des effets de bord
                            if (ny >= 0 && ny < height && nx >= 0 && nx < width) {
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
     * @return const char* "Gaussian Filter"
     */
    const char* getName() const override {
        return "Gaussian Filter";
    }

    /**
     * @brief Obtient l'écart-type sigma du filtre
     *
     * @return double Valeur de sigma
     */
    double getSigma() const { return sigma; }

private:
    /**
     * @brief Calcule et normalise le noyau gaussien 2D
     *
     * Génère un noyau gaussien 2D en évaluant la fonction gaussienne
     * (sans le coefficient de normalisation) pour chaque position (dx, dy)
     * relative au centre.
     * Le noyau est ensuite normalisé pour que la somme de tous ses
     * éléments soit égale à 1.
     *
     * @note Appelé une seule fois lors de la construction
     * @note Formule échantillonnée : G'(dx,dy) = exp(-(dx^2 + dy^2) / (2*sigma^2))
     */
    void computeKernel() {
        const int radius = getRadius();
        const double sigma2 = 2.0 * sigma * sigma;

        kernel.resize(kernelSize, std::vector<double>(kernelSize));
        double sum = 0.0;

        // Calcul des valeurs du noyau
        for (int dy = -radius; dy <= radius; ++dy) {
            for (int dx = -radius; dx <= radius; ++dx) {
                const double dist2 = dx * dx + dy * dy;

                const double value = std::exp(-dist2 / sigma2);

                kernel[dy + radius][dx + radius] = value;
                sum += value;
            }
        }

        // Normalisation (somme = 1)
        for (int i = 0; i < kernelSize; ++i) {
            for (int j = 0; j < kernelSize; ++j) {
                kernel[i][j] /= sum;
            }
        }
    }
};

} // namespace ImageProcessing
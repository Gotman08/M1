#pragma once

#include "../core/ImageFilter.hpp"
#include <vector>
#include <algorithm> // Requis pour std::nth_element
#include <iterator>  // Requis pour std::begin / std::end

/**
 * @file MedianFilter.hpp
 * @brief Filtre médian (non-linéaire) pour la réduction du bruit.
 */
namespace ImageProcessing {

/**
 * @brief Filtre médian (filtre de rang non-linéaire).
 *
 * Opérateur de traitement d'image non-linéaire (tel que défini
 * dans CM02 et CM05).
 * Il appartient à la famille des "filtres de rang" (CM02, CM05).
 *
 * Remplace chaque pixel par la valeur médiane de son voisinage.
 * I'(x) = Mediane{I(x+b) | b in Voisinage}
 *
 * Très efficace contre le bruit impulsionnel ("poivre et sel")
 * car il ignore les valeurs aberrantes (extrema).
 *
 * @note Opérateur non-linéaire : son comportement dépend du
 * contenu de l'image (CM02). Med(A+B) != Med(A)+Med(B).
 * @note Préserve mieux les contours (discontinuités) que les
 * filtres de lissage linéaires (Moyen, Gaussien).
 * @note Hérite de ConvolutionFilter par commodité (pour réutiliser
 * la gestion de kernelSize/radius), mais N'EST PAS une convolution.
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
     * trouve la valeur médiane (via std::nth_element), et remplace
     * le pixel par cette valeur.
     *
     * @param data Données de l'image à filtrer (modifiées en place)
     *
     * @throws std::runtime_error Si une erreur survient pendant le filtrage
     *
     * @note Gestion des effets de bord : les pixels hors de l'image
     * sont ignorés (ne sont pas inclus dans le calcul de la médiane).
     * @note Complexité (moyenne) : O(w * h * k^2 * c)
     * (grâce à std::nth_element qui est en O(N) moyen, où N=k^2).
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
                        // --- CORRECTION : Utilisation de std::nth_element ---
                        // Tri partiel efficace (O(N) moyen) pour trouver la médiane.
                        // Place le N-ième élément (la médiane) à sa position
                        // correcte, comme s'il était trié.
                        auto median_it = values.begin() + values.size() / 2;
                        std::nth_element(values.begin(), median_it, values.end());
                        
                        data[y][x * colors + c] = *median_it;


                    } else {
                        // Ne devrait pas arriver avec kernelSize >= 1, mais sécurité
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
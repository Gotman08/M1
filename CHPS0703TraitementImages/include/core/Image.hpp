#pragma once

#include "ImageData.hpp"
#include "../utils/ColorConversion.hpp"
#include "../utils/ImageUtils.hpp"
#include <memory>
#include <stdexcept>

/**
 * @file Image.hpp
 * @brief Classe principale pour la gestion d'images
 */
namespace ImageProcessing {

/**
 * @brief Classe principale pour gérer les images RGB et leurs transformations
 *
 * Cette classe encapsule les données d'une image et fournit des opérations
 * de base (affichage, transformation de couleur, sauvegarde/restauration).
 * Elle utilise ImageData pour le stockage avec gestion automatique RAII.
 *
 * Pour les filtres et opérations morphologiques, utilisez les classes dédiées
 * (GaussianFilter, Erosion, etc.) via la méthode applyFilter().
 *
 * @note N'est plus un Singleton - créez des instances normalement
 * @note Thread-safe pour les lectures simultanées
 *
 * @example
 * Image img(640, 480, 3);
 * img.loadFromBuffer(IMG, W, H);
 * auto gaussianFilter = std::make_unique<GaussianFilter>(5, 1.4);
 * img.applyFilter(*gaussianFilter);
 */
class Image {
private:
    ImageData currentData;      ///< Données actuelles de l'image
    ImageData originalData;     ///< Copie de l'image originale

public:
    /**
     * @brief Constructeur par défaut
     */
    Image() = default;

    /**
     * @brief Constructeur avec dimensions
     *
     * @param width Largeur de l'image
     * @param height Hauteur de l'image
     * @param colors Nombre de canaux (1=grayscale, 3=RGB)
     *
     * @throws std::invalid_argument Si les dimensions sont invalides
     */
    Image(int width, int height, int colors)
        : currentData(width, height, colors),
          originalData(width, height, colors) {}

    /**
     * @brief Charge une image depuis un buffer externe
     *
     * @param buffer Buffer source (format : RGB entrelacé)
     * @param width Largeur du buffer
     * @param height Hauteur du buffer
     *
     * @throws std::invalid_argument Si les dimensions sont invalides
     * @throws std::runtime_error Si le buffer est nullptr
     *
     * @example
     * Image img;
     * img.loadFromBuffer(IMG, W, H); // IMG défini dans image.hpp
     */
    void loadFromBuffer(const unsigned char* buffer, int width, int height) {
        if (!buffer) {
            throw std::runtime_error("buffer null");
        }
        if (width <= 0 || height <= 0) {
            throw std::invalid_argument("dimensions invalides");
        }

        currentData = ImageData(width, height, 3);

        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                const size_t base = (static_cast<size_t>(y) * width + x) * 3;
                currentData[y][x * 3 + 0] = static_cast<double>(buffer[base + 0]);
                currentData[y][x * 3 + 1] = static_cast<double>(buffer[base + 1]);
                currentData[y][x * 3 + 2] = static_cast<double>(buffer[base + 2]);
            }
        }

        saveOriginal();
    }

    /**
     * @brief Applique un filtre sur l'image
     *
     * @param filter Référence vers un filtre (GaussianFilter, SobelFilter, etc.)
     *
     * @throws std::runtime_error Si le filtre échoue
     *
     * @example
     * GaussianFilter gauss(5, 1.4);
     * img.applyFilter(gauss);
     */
    void applyFilter(ImageFilter& filter) {
        filter.apply(currentData);
    }

    /**
     * @brief Convertit l'image en niveaux de gris
     *
     * OPTIMISATION: Après conversion, réduit automatiquement à 1 canal
     * pour gains de performance (mémoire -66%, CPU -66%).
     *
     * @param method Méthode de conversion (défaut: REC601)
     *
     * @example
     * img.toGrayscale(ColorConversion::Method::REC709);
     * // L'image passe automatiquement de 3 canaux à 1 canal
     */
    void toGrayscale(ColorConversion::Method method = ColorConversion::Method::REC601) {
        const int width = currentData.getWidth();
        const int height = currentData.getHeight();
        const int colors = currentData.getColors();

        // Si déjà en grayscale (1 canal), rien à faire
        if (colors == 1) {
            return;
        }

        // Conversion RGB → Grayscale (R=G=B)
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                const int base = x * colors;
                const double r = currentData[y][base + 0];
                const double g = (colors > 1) ? currentData[y][base + 1] : r;
                const double b = (colors > 2) ? currentData[y][base + 2] : r;

                const double gray = ColorConversion::convert(r, g, b, method);

                currentData[y][base + 0] = gray;
                if (colors > 1) currentData[y][base + 1] = gray;
                if (colors > 2) currentData[y][base + 2] = gray;
            }
        }

        // OPTIMISATION: Réduction de 3 canaux → 1 canal
        // Gain mémoire: -66%, Gain CPU pour filtres: -66%
        if (colors == 3) {
            currentData.convertToSingleChannel();
        }
    }

    /**
     * @brief Applique un seuillage binaire
     *
     * Compatible avec images 1 canal (grayscale) et 3 canaux (RGB).
     * Pour images RGB, applique d'abord une conversion grayscale.
     *
     * @param threshold Seuil [0-255]
     *
     * @example
     * img.binarize(128.0);
     */
    void binarize(double threshold) {
        const int width = currentData.getWidth();
        const int height = currentData.getHeight();
        const int colors = currentData.getColors();

        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                const int base = x * colors;

                // Calcul de la valeur grayscale
                double gray;
                if (colors == 1) {
                    // Optimisation: lecture directe pour images grayscale
                    gray = currentData[y][x];
                } else {
                    const double r = currentData[y][base + 0];
                    const double g = (colors > 1) ? currentData[y][base + 1] : r;
                    const double b = (colors > 2) ? currentData[y][base + 2] : r;
                    gray = ColorConversion::rec601(r, g, b);
                }

                const double v = (gray > threshold) ? 255.0 : 0.0;

                // Application du seuillage
                currentData[y][base + 0] = v;
                if (colors > 1) currentData[y][base + 1] = v;
                if (colors > 2) currentData[y][base + 2] = v;
            }
        }
    }

    /**
     * @brief Applique le négatif de l'image
     */
    void negate() {
        // Accès direct aux données internes (pas via getter public)
        auto& data = currentData.getData();
        for (auto& row : data) {
            for (double& val : row) {
                val = 255.0 - val;
            }
        }
    }

    /**
     * @brief Quantification uniforme
     *
     * @param levels Nombre de niveaux [2-256]
     *
     * @throws std::invalid_argument Si levels hors limites
     */
    void quantize(int levels) {
        if (levels <= 1 || levels > 256) {
            throw std::invalid_argument("levels entre 2 et 256");
        }

        const double step = 256.0 / levels;
        auto& data = currentData.getData();

        for (auto& row : data) {
            for (double& val : row) {
                // min implémenté manuellement avec opérateur ternaire
                const int levelCalc = static_cast<int>(val / step);
                const int levelIndex = (levelCalc < levels - 1) ? levelCalc : levels - 1;
                val = ImageUtils::clamp(levelIndex * step + step / 2.0, 0.0, 255.0);
            }
        }
    }

    /**
     * @brief Rehaussement de contraste
     *
     * @param alpha Gain multiplicatif
     * @param beta Offset additif
     */
    void enhance(double alpha, double beta) {
        auto& data = currentData.getData();
        for (auto& row : data) {
            for (double& val : row) {
                val = ImageUtils::clamp(alpha * val + beta, 0.0, 255.0);
            }
        }
    }

    /**
     * @brief Égalisation d'histogramme
     *
     * Compatible avec images 1 canal (grayscale) et 3 canaux (RGB).
     * Pour images RGB, applique l'égalisation sur la luminance.
     */
    void equalizeHistogram() {
        const int width = currentData.getWidth();
        const int height = currentData.getHeight();
        const int colors = currentData.getColors();
        const int N = width * height;

        unsigned int hist[256] = {0};

        // Calcul de l'histogramme
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                const int base = x * colors;

                double gray;
                if (colors == 1) {
                    // Optimisation: lecture directe pour images grayscale
                    gray = currentData[y][x];
                } else {
                    const double r = currentData[y][base + 0];
                    const double g = (colors > 1) ? currentData[y][base + 1] : r;
                    const double b = (colors > 2) ? currentData[y][base + 2] : r;
                    gray = ColorConversion::rec601(r, g, b);
                }

                ++hist[ImageUtils::toUInt8(gray)];
            }
        }

        // Calcul de la CDF
        unsigned int cdf[256];
        unsigned int acc = 0;
        for (int i = 0; i < 256; ++i) {
            acc += hist[i];
            cdf[i] = acc;
        }

        unsigned int cdfMin = 0;
        for (int i = 0; i < 256; ++i) {
            if (cdf[i] != 0) {
                cdfMin = cdf[i];
                break;
            }
        }

        // LUT
        uint8_t lut[256];
        const unsigned int denom = (N > static_cast<int>(cdfMin)) ? (N - cdfMin) : 1;
        for (int i = 0; i < 256; ++i) {
            if (cdf[i] <= cdfMin) {
                lut[i] = 0;
            } else {
                const double val = (static_cast<double>(cdf[i] - cdfMin) * 255.0) / denom;
                lut[i] = ImageUtils::toUInt8(val);
            }
        }

        // Application de la LUT
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                const int base = x * colors;

                double gray;
                if (colors == 1) {
                    // Optimisation: lecture directe pour images grayscale
                    gray = currentData[y][x];
                } else {
                    const double r = currentData[y][base + 0];
                    const double g = (colors > 1) ? currentData[y][base + 1] : r;
                    const double b = (colors > 2) ? currentData[y][base + 2] : r;
                    gray = ColorConversion::rec601(r, g, b);
                }

                const double v = static_cast<double>(lut[ImageUtils::toUInt8(gray)]);

                currentData[y][base + 0] = v;
                if (colors > 1) currentData[y][base + 1] = v;
                if (colors > 2) currentData[y][base + 2] = v;
            }
        }
    }

    /**
     * @brief Sauvegarde l'état actuel comme original
     */
    void saveOriginal() {
        originalData = currentData;
    }

    /**
     * @brief Restaure l'image originale
     */
    void restoreOriginal() {
        currentData = originalData;
    }

    /**
     * @brief Obtient une référence constante vers les données actuelles
     *
     * @return const ImageData& Référence en lecture seule
     *
     * @note Retourne une référence const pour protéger l'intégrité des données
     * @note Pour modifier l'image, utiliser les méthodes publiques (applyFilter, toGrayscale, etc.)
     */
    const ImageData& getData() const { return currentData; }

    /**
     * @brief Obtient les dimensions
     */
    int getWidth() const { return currentData.getWidth(); }
    int getHeight() const { return currentData.getHeight(); }
    int getColors() const { return currentData.getColors(); }
};

} // namespace ImageProcessing

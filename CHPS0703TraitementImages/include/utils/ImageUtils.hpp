#pragma once

#include <cstdint>
#include <vector>
#include <stdexcept>

/**
 * @file ImageUtils.hpp
 * @brief Utilitaires génériques pour le traitement d'images
 *
 * Cette classe fournit des fonctions utilitaires statiques pour manipuler
 * les valeurs de pixels, écrêter les valeurs, et effectuer des conversions.
 */
namespace ImageProcessing {

/**
 * @brief Classe utilitaire pour les opérations de base sur les images
 *
 * Fournit des méthodes statiques pour les opérations courantes :
 * - Écrêtage de valeurs (clamp)
 * - Conversion sûre vers uint8_t
 * - Allocation/copie de buffers
 */
class ImageUtils {
public:
    /**
     * @brief Écrête une valeur dans l'intervalle [min, max]
     *
     * Cette fonction garantit qu'une valeur reste dans les bornes spécifiées.
     * Si la valeur est inférieure au minimum, elle retourne le minimum.
     * Si la valeur est supérieure au maximum, elle retourne le maximum.
     * Sinon, elle retourne la valeur inchangée.
     *
     * @param value Valeur à écrêter
     * @param minVal Valeur minimale de l'intervalle
     * @param maxVal Valeur maximale de l'intervalle
     * @return double Valeur écrêtée dans [minVal, maxVal]
     *
     * @note Cette fonction utilise des comparaisons directes pour une performance optimale
     *
     * @example
     * double result = ImageUtils::clamp(300.0, 0.0, 255.0); // retourne 255.0
     * double result2 = ImageUtils::clamp(-10.0, 0.0, 255.0); // retourne 0.0
     * double result3 = ImageUtils::clamp(128.0, 0.0, 255.0); // retourne 128.0
     */
    static inline double clamp(double value, double minVal, double maxVal) {
        if (value < minVal) return minVal;
        if (value > maxVal) return maxVal;
        return value;
    }

    /**
     * @brief Conversion sûre double vers uint8_t avec écrêtage dans [0,255]
     *
     * Assure la quantification finale vers l'espace V = {0,1,...,255} des images
     * 8 bits. L'écrêtage préserve les bornes après application d'opérateurs
     * pouvant déborder (rehaussement, quantification).
     * La fonction effectue un arrondi à 0.5 près avant la troncature entière.
     *
     * @param value Valeur en virgule flottante à convertir
     * @return uint8_t Valeur quantifiée et écrêtée dans [0, 255]
     *
     * @note Arrondi à 0.5 près avant troncature entière (cast vers uint8_t)
     * @note Les valeurs négatives sont écrêtées à 0
     * @note Les valeurs > 255 sont écrêtées à 255
     *
     * @example
     * uint8_t val1 = ImageUtils::toUInt8(127.3); // retourne 127
     * uint8_t val2 = ImageUtils::toUInt8(127.6); // retourne 128
     * uint8_t val3 = ImageUtils::toUInt8(-5.0);  // retourne 0
     * uint8_t val4 = ImageUtils::toUInt8(300.0); // retourne 255
     */
    static inline uint8_t toUInt8(double value) {
        if (value < 0.0) return 0;
        if (value > 255.0) return 255;
        return static_cast<uint8_t>(value + 0.5);
    }

    /**
     * @brief Crée une copie profonde d'un buffer 2D de doubles
     *
     * Cette fonction alloue un nouveau buffer 2D et copie toutes les valeurs
     * du buffer source. La mémoire est gérée automatiquement par std::vector (RAII).
     *
     * @param source Buffer source à copier
     * @param height Hauteur du buffer (nombre de lignes)
     * @param width Largeur du buffer (nombre de colonnes par ligne)
     * @return std::vector<std::vector<double>> Copie profonde du buffer
     *
     * @throws std::runtime_error Si les dimensions sont invalides
     *
     * @note Utilise std::vector pour la gestion automatique de la mémoire (RAII)
     * @note Aucune libération manuelle nécessaire - destruction automatique
     *
     * @example
     * auto copy = ImageUtils::createCopy(originalData, 480, 640);
     * // Utilisation de copy...
     * // Destruction automatique en fin de scope
     */
    static std::vector<std::vector<double>> createCopy(
        const std::vector<std::vector<double>>& source,
        int height,
        int width
    ) {
        if (height <= 0 || width <= 0) {
            throw std::runtime_error("dimensions invalides pour la copie");
        }

        std::vector<std::vector<double>> copy(height, std::vector<double>(width));

        for (int i = 0; i < height; ++i) {
            for (int j = 0; j < width; ++j) {
                copy[i][j] = source[i][j];
            }
        }

        return copy;
    }

    /**
     * @brief Vérifie si des coordonnées sont valides pour une image donnée
     *
     * @param x Coordonnée X à vérifier
     * @param y Coordonnée Y à vérifier
     * @param width Largeur de l'image
     * @param height Hauteur de l'image
     * @return bool true si les coordonnées sont valides, false sinon
     *
     * @example
     * if (ImageUtils::isValidCoordinate(x, y, width, height)) {
     *     // Accès sûr au pixel
     * }
     */
    static inline bool isValidCoordinate(int x, int y, int width, int height) {
        return x >= 0 && x < width && y >= 0 && y < height;
    }

    /**
     * @brief Calcule l'indice linéaire d'un pixel dans un buffer 1D
     *
     * Convertit des coordonnées 2D (x, y) en un indice 1D pour un buffer
     * organisé en row-major order (lignes consécutives).
     *
     * @param x Coordonnée X du pixel
     * @param y Coordonnée Y du pixel
     * @param width Largeur de l'image
     * @param colors Nombre de canaux de couleur par pixel
     * @return int Indice linéaire dans le buffer 1D
     *
     * @note Formule: index = (y * width + x) * colors
     *
     * @example
     * int index = ImageUtils::getLinearIndex(10, 20, 640, 3);
     * // Accès au pixel RGB à la position (10, 20)
     */
    static inline int getLinearIndex(int x, int y, int width, int colors) {
        return (y * width + x) * colors;
    }

private:
    // Constructeur privé pour empêcher l'instanciation
    ImageUtils() = delete;
    ~ImageUtils() = delete;
    ImageUtils(const ImageUtils&) = delete;
    ImageUtils& operator=(const ImageUtils&) = delete;
};

} // namespace ImageProcessing

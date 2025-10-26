#pragma once

#include "../core/ImageData.hpp"
#include "../utils/ImageUtils.hpp"
#include <iostream>
#include <iomanip>

/**
 * @file DisplayManager.hpp
 * @brief Gestionnaire d'affichage pour les images
 */
namespace ImageProcessing {

/**
 * @brief Classe pour gérer l'affichage d'images dans le terminal
 *
 * Fournit des méthodes pour afficher des aperçus d'images en couleur
 * dans le terminal avec des caractères Unicode, ainsi que des vues
 * détaillées de régions d'intérêt (ROI) avec les valeurs numériques.
 *
 * @note Utilise les codes ANSI pour les couleurs 24-bit
 * @note Compatible Windows (ASCII) et Linux/macOS (Unicode)
 */
class DisplayManager {
public:
    /**
     * @brief Affiche un aperçu de l'image dans le terminal avec couleurs
     *
     * Utilise des caractères Unicode (ou ASCII sous Windows) colorés avec
     * les codes ANSI 24-bit pour représenter visuellement l'image.
     * L'image est automatiquement redimensionnée pour tenir dans les limites.
     *
     * @param data Données de l'image à afficher
     * @param maxCols Nombre maximum de colonnes (défaut: 100)
     * @param maxRows Nombre maximum de lignes (défaut: 40)
     *
     * @note Sous Linux/macOS, utilise le caractère '▀' (demi-bloc supérieur)
     * @note Sous Windows, utilise le caractère '█' (bloc plein ASCII)
     *
     * @example
     * DisplayManager::printPreview(imageData, 80, 30);
     */
    static void printPreview(const ImageData& data, int maxCols = 100, int maxRows = 40) {
        const int width = data.getWidth();
        const int height = data.getHeight();

        if (width <= 0 || height <= 0) {
            std::cout << "image vide\n";
            return;
        }

        // Calcul des dimensions cibles (min implémenté manuellement)
        const int targetW = (width < maxCols) ? width : maxCols;
        const int targetH = (height < maxRows * 2) ? height : maxRows * 2;

        const double sx = static_cast<double>(width) / targetW;
        const double sy = static_cast<double>(height) / targetH;

        for (int ty = 0; ty < targetH; ty += 2) {
            const int yTopCalc = static_cast<int>(ty * sy);
            const int yTop = (yTopCalc < height - 1) ? yTopCalc : height - 1;

            const int yBotCalc = static_cast<int>((ty + 1) * sy);
            const int yBot = (yBotCalc < height - 1) ? yBotCalc : height - 1;

            for (int tx = 0; tx < targetW; ++tx) {
                const int xSrcCalc = static_cast<int>(tx * sx);
                const int xSrc = (xSrcCalc < width - 1) ? xSrcCalc : width - 1;

                int rt, gt, bt, rb, gb, bb;
                getRGB(data, xSrc, yTop, rt, gt, bt);
                getRGB(data, xSrc, yBot, rb, gb, bb);

#ifdef _WIN32
                // Windows : caractère ASCII compatible
                std::cout << "\033[38;2;" << rt << ";" << gt << ";" << bt << "m"
                         << "\033[48;2;" << rb << ";" << gb << ";" << bb << "m"
                         << "\xDB";  // Bloc plein ASCII (█)
#else
                // Linux/macOS : demi-bloc Unicode
                std::cout << "\033[38;2;" << rt << ";" << gt << ";" << bt << "m"
                         << "\033[48;2;" << rb << ";" << gb << ";" << bb << "m"
                         << "\u2580";  // Demi-bloc supérieur (▀)
#endif
            }
            std::cout << "\033[0m\n";
        }
        std::cout << std::endl;
    }

    /**
     * @brief Affiche une région d'intérêt (ROI) avec les valeurs de pixels
     *
     * Affiche les valeurs numériques des pixels dans une région rectangulaire
     * de l'image, utile pour le débogage et l'analyse détaillée.
     *
     * @param data Données de l'image
     * @param y0 Coordonnée Y de début (inclusive)
     * @param y1 Coordonnée Y de fin (exclusive)
     * @param x0 Coordonnée X de début (inclusive)
     * @param x1 Coordonnée X de fin (exclusive)
     * @param step Pas d'échantillonnage (1 = tous les pixels)
     * @param channel Canal à afficher (-1=RGB complet, 0=R, 1=G, 2=B)
     *
     * @example
     * // Affiche les pixels de (10,10) à (20,20), canal rouge uniquement
     * DisplayManager::printROI(data, 10, 20, 10, 20, 1, 0);
     */
    static void printROI(
        const ImageData& data,
        int y0, int y1, int x0, int x1,
        int step = 1,
        int channel = -1
    ) {
        const int width = data.getWidth();
        const int height = data.getHeight();

        // Ajustement des bornes (min/max implémentés manuellement)
        y0 = (y0 > 0) ? y0 : 0;
        x0 = (x0 > 0) ? x0 : 0;
        y1 = (y1 < height) ? y1 : height;
        x1 = (x1 < width) ? x1 : width;

        if (y0 >= y1 || x0 >= x1) {
            std::cout << "roi vide\n";
            return;
        }

        for (int y = y0; y < y1; y += step) {
            for (int x = x0; x < x1; x += step) {
                int r, g, b;
                getRGB(data, x, y, r, g, b);

                if (channel == 0) {
                    std::cout << std::setw(3) << r << " ";
                } else if (channel == 1) {
                    std::cout << std::setw(3) << g << " ";
                } else if (channel == 2) {
                    std::cout << std::setw(3) << b << " ";
                } else {
                    std::cout << "[" << std::setw(3) << r
                             << "," << std::setw(3) << g
                             << "," << std::setw(3) << b << "] ";
                }
            }
            std::cout << "\n";
        }
        std::cout << std::endl;
    }

    /**
     * @brief Affiche les informations de base sur l'image
     *
     * @param data Données de l'image
     *
     * @example
     * DisplayManager::printInfo(imageData);
     * // Affiche: "Image: 640x480, 3 canaux (RGB)"
     */
    static void printInfo(const ImageData& data) {
        const int width = data.getWidth();
        const int height = data.getHeight();
        const int colors = data.getColors();

        std::cout << "Image: " << width << "x" << height
                  << ", " << colors << " canaux";

        if (colors == 1) {
            std::cout << " (Grayscale)";
        } else if (colors == 3) {
            std::cout << " (RGB)";
        }

        std::cout << std::endl;
    }

private:
    /**
     * @brief Extrait les composantes RGB d'un pixel
     *
     * @param data Données de l'image
     * @param x Coordonnée X
     * @param y Coordonnée Y
     * @param r Référence pour la composante rouge
     * @param g Référence pour la composante verte
     * @param b Référence pour la composante bleue
     */
    static inline void getRGB(const ImageData& data, int x, int y, int& r, int& g, int& b) {
        const int colors = data.getColors();
        const int base = x * colors;

        r = ImageUtils::toUInt8(data[y][base + 0]);
        g = (colors > 1) ? ImageUtils::toUInt8(data[y][base + 1]) : r;
        b = (colors > 2) ? ImageUtils::toUInt8(data[y][base + 2]) : r;
    }

    // Constructeur privé pour empêcher l'instanciation
    DisplayManager() = delete;
    ~DisplayManager() = delete;
    DisplayManager(const DisplayManager&) = delete;
    DisplayManager& operator=(const DisplayManager&) = delete;
};

} // namespace ImageProcessing

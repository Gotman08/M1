#pragma once

#include "TP1App.hpp"
#include "grayscale.hpp"
#include <cmath>
#include <algorithm>
#include <iomanip>
#include <iostream>

/**
 * @brief Classe ImgNB pour le traitement d'images en niveaux de gris.
 * 
 * Cette classe encapsule Img et fournit des fonctionnalités spécifiques
 * au traitement d'images en niveaux de gris (noir et blanc).
 * Toutes les opérations travaillent sur le canal de luminance uniquement.
 */
class ImgNB {
private:
    Img& img;
    double** grayData;
    int width;
    int height;
    
    /**
     * @brief Constructeur privé prenant une référence à Img.
     * 
     * @param imgRef Référence vers l'instance Img
     */
    explicit ImgNB(Img& imgRef) : img(imgRef), grayData(nullptr) {
        width = img.getWidth();
        height = img.getHeight();
        convertToGrayscale();
    }
    
    // NOTE: suppression des constructeurs de copie et déplacement
    ImgNB(const ImgNB& other) = delete;
    ImgNB& operator=(const ImgNB& other) = delete;
    ImgNB(ImgNB&& other) = delete;
    ImgNB& operator=(ImgNB&& other) = delete;
    
    static ImgNB* instance;
    
    /**
     * @brief Convertit l'image RGB en données grayscale internes.
     */
    void convertToGrayscale() {
        if (grayData) {
            freeGrayData();
        }
        
        grayData = new double*[height];
        for (int i = 0; i < height; i++) {
            grayData[i] = new double[width];
        }
        
        double** imgData = img.getImg();
        int colors = img.getColors();
        
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                int base = x * colors;
                
                if (colors == 1) {
                    // NOTE: image déjà en niveaux de gris
                    grayData[y][x] = imgData[y][base];
                } else {
                    // NOTE: conversion REC601 (0.299R + 0.587G + 0.114B)
                    double r = imgData[y][base + 0];
                    double g = (colors > 1) ? imgData[y][base + 1] : r;
                    double b = (colors > 2) ? imgData[y][base + 2] : r;
                    grayData[y][x] = 0.299 * r + 0.587 * g + 0.114 * b;
                }
            }
        }
    }
    
    /**
     * @brief Libère la mémoire des données grayscale.
     */
    void freeGrayData() {
        if (grayData) {
            for (int i = 0; i < height; i++) {
                delete[] grayData[i];
            }
            delete[] grayData;
            grayData = nullptr;
        }
    }
    
    /**
     * @brief Synchronise les données grayscale vers l'image RGB.
     */
    void syncToImg() const {
        double** imgData = img.getImg();
        int colors = img.getColors();
        
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                int base = x * colors;
                double gray = clamp(grayData[y][x], 0.0, 255.0);
                
                imgData[y][base + 0] = gray;
                if (colors > 1) imgData[y][base + 1] = gray;
                if (colors > 2) imgData[y][base + 2] = gray;
            }
        }
    }
    
    /**
     * @brief Écrête une valeur dans l'intervalle [min, max].
     */
    static inline double clamp(double value, double minVal, double maxVal) {
        if (value < minVal) return minVal;
        if (value > maxVal) return maxVal;
        return value;
    }
    
    /**
     * @brief Conversion sûre double->uint8 avec écrêtage.
     */
    static inline uint8_t to_u8(double v) {
        if (v < 0.0) return 0;
        if (v > 255.0) return 255;
        return static_cast<uint8_t>(v + 0.5);
    }

public:
    /**
     * @brief Destructeur.
     */
    ~ImgNB() {
        freeGrayData();
    }
    /**
     * @brief Retourne l'instance unique de la classe ImgNB.
     * 
     * @param w Largeur de l'image
     * @param h Hauteur de l'image
     * @param c Nombre de canaux de couleur
     * @return ImgNB& Référence vers l'instance unique
     */
    static ImgNB& getInstance(int w = 0, int h = 0, int c = 0) {
        if (instance == nullptr) {
            instance = new ImgNB(Img::getInstance(w, h, c));
        }
        return *instance;
    }

    /**
     * @brief Affiche un aperçu de l'image dans le terminal.
     * 
     * @param maxCols Nombre maximum de colonnes
     * @param maxRows Nombre maximum de lignes
     */
    void printPreview(int maxCols = 100, int maxRows = 40) const {
        syncToImg();
        img.printPreview(maxCols, maxRows);
    }

    /**
     * @brief Affiche une région d'intérêt (ROI) de l'image.
     * 
     * @param y0 Coordonnée Y de début
     * @param y1 Coordonnée Y de fin
     * @param x0 Coordonnée X de début
     * @param x1 Coordonnée X de fin
     * @param step Pas d'échantillonnage
     * @param channel Canal à afficher
     */
    void printROI(int y0, int y1, int x0, int x1, int step = 1, int channel = -1) const {
        if (y0 < 0) y0 = 0;
        if (x0 < 0) x0 = 0;
        if (y1 > height) y1 = height;
        if (x1 > width) x1 = width;
        
        if (y0 >= y1 || x0 >= x1) { 
            std::cout << "roi vide\n"; 
            return; 
        }

        for (int y = y0; y < y1; y += step) {
            for (int x = x0; x < x1; x += step) {
                int gray = to_u8(grayData[y][x]);
                std::cout << std::setw(3) << gray << " ";
            }
            std::cout << "\n";
        }
        std::cout << std::endl;
    }

    /**
     * @brief Applique un seuillage binaire sur l'image grayscale.
     * 
     * @param threshold Seuil pour la binarisation
     */
    void binaryzation(double threshold) {
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                grayData[y][x] = (grayData[y][x] > threshold) ? 255.0 : 0.0;
            }
        }
        syncToImg();
    }

    /**
     * @brief Applique l'opérateur négatif sur l'image grayscale.
     */
    void negatif() {
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                grayData[y][x] = 255.0 - grayData[y][x];
            }
        }
        syncToImg();
    }

    /**
     * @brief Quantification uniforme sur l'image grayscale.
     * 
     * @param n Nombre de niveaux
     */
    void quantification(int n) {
        if (n <= 1 || n > 256) {
            throw std::runtime_error("n entre 2 et 256");
        }
        
        const double step = 256.0 / n;
        
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                double niveau = grayData[y][x] / step;
                int indiceNiveau = static_cast<int>(niveau);
                if (indiceNiveau < 0) indiceNiveau = 0;
                if (indiceNiveau >= n) indiceNiveau = n - 1;
                double repr = indiceNiveau * step + step / 2.0;
                grayData[y][x] = clamp(repr, 0.0, 255.0);
            }
        }
        syncToImg();
    }

    /**
     * @brief Rehaussement de contraste sur l'image grayscale.
     * 
     * @param alpha Gain multiplicatif
     * @param beta Offset additif
     */
    void rehaussement(double alpha, double beta) {
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                double nouvelleValeur = alpha * grayData[y][x] + beta;
                grayData[y][x] = clamp(nouvelleValeur, 0.0, 255.0);
            }
        }
        syncToImg();
    }

    /**
     * @brief Égalisation d'histogramme sur l'image grayscale.
     */
    void egalisationHistogramme() {
        if (width <= 0 || height <= 0) return;
        
        // NOTE: calcul de l'histogramme
        unsigned int hist[256] = {0};
        const int N = width * height;
        
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                uint8_t gv = to_u8(grayData[y][x]);
                ++hist[gv];
            }
        }
        
        // NOTE: calcul de la CDF (fonction de répartition cumulée)
        unsigned int cdf[256];
        unsigned int acc = 0;
        for (int i = 0; i < 256; i++) {
            acc += hist[i];
            cdf[i] = acc;
        }
        
        // NOTE: recherche du minimum non nul
        unsigned int cdfMin = 0;
        for (int i = 0; i < 256; i++) { 
            if (cdf[i] != 0) { 
                cdfMin = cdf[i]; 
                break; 
            } 
        }

        // NOTE: construction de la LUT (Look-Up Table)
        uint8_t lut[256];
        const unsigned int denom = (N > 0 && N > (int)cdfMin) ? (N - cdfMin) : 1;
        for (int i = 0; i < 256; i++) {
            if (cdf[i] <= cdfMin) {
                lut[i] = 0;
            } else {
                double val = (static_cast<double>(cdf[i] - cdfMin) * 255.0) / static_cast<double>(denom);
                lut[i] = to_u8(val);
            }
        }
        
        // NOTE: application de la LUT
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                uint8_t gv = to_u8(grayData[y][x]);
                grayData[y][x] = static_cast<double>(lut[gv]);
            }
        }
        syncToImg();
    }

    /**
     * @brief Recharge l'image depuis le buffer source.
     */
    void reload() {
        img.reload();
        int newWidth = img.getWidth();
        int newHeight = img.getHeight();
        
        // NOTE: réallocation si dimensions changées
        if (newWidth != width || newHeight != height) {
            width = newWidth;
            height = newHeight;
        }
        
        convertToGrayscale();
    }

    /**
     * @brief Restaure l'image à son état original.
     */
    void restoreOriginal() {
        img.restoreOriginal();
        convertToGrayscale();
    }

    /**
     * @brief Érosion morphologique sur l'image grayscale.
     * 
     * @param kernelSize Taille de l'élément structurant
     */
    void erosion(int kernelSize = 3) {
        if (kernelSize < 1 || kernelSize % 2 == 0) {
            throw std::runtime_error("taille noyau impair");
        }

        const int radius = kernelSize / 2;
        double** temp = createTempCopy();

        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                double minVal = 255.0;
                
                for (int dy = -radius; dy <= radius; dy++) {
                    for (int dx = -radius; dx <= radius; dx++) {
                        int ny = y + dy;
                        int nx = x + dx;
                        
                        if (ny >= 0 && ny < height && nx >= 0 && nx < width) {
                            if (temp[ny][nx] < minVal) {
                                minVal = temp[ny][nx];
                            }
                        }
                    }
                }
                
                grayData[y][x] = minVal;
            }
        }

        freeTempCopy(temp);
        syncToImg();
    }

    /**
     * @brief Dilatation morphologique sur l'image grayscale.
     * 
     * @param kernelSize Taille de l'élément structurant
     */
    void dilatation(int kernelSize = 3) {
        if (kernelSize < 1 || kernelSize % 2 == 0) {
            throw std::runtime_error("taille noyau impair");
        }

        const int radius = kernelSize / 2;
        double** temp = createTempCopy();

        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                double maxVal = 0.0;
                
                for (int dy = -radius; dy <= radius; dy++) {
                    for (int dx = -radius; dx <= radius; dx++) {
                        int ny = y + dy;
                        int nx = x + dx;
                        
                        if (ny >= 0 && ny < height && nx >= 0 && nx < width) {
                            if (temp[ny][nx] > maxVal) {
                                maxVal = temp[ny][nx];
                            }
                        }
                    }
                }
                
                grayData[y][x] = maxVal;
            }
        }

        freeTempCopy(temp);
        syncToImg();
    }

    /**
     * @brief Ouverture morphologique sur l'image grayscale.
     * 
     * @param kernelSize Taille de l'élément structurant
     */
    void ouverture(int kernelSize = 3) {
        erosion(kernelSize);
        dilatation(kernelSize);
    }

    /**
     * @brief Fermeture morphologique sur l'image grayscale.
     * 
     * @param kernelSize Taille de l'élément structurant
     */
    void fermeture(int kernelSize = 3) {
        dilatation(kernelSize);
        erosion(kernelSize);
    }

    /**
     * @brief Filtre moyen sur l'image grayscale.
     * 
     * @param kernelSize Taille de la fenêtre
     */
    void filtreMoyen(int kernelSize = 3) {
        if (kernelSize < 1 || kernelSize % 2 == 0) {
            throw std::runtime_error("taille noyau impair");
        }

        const int radius = kernelSize / 2;
        double** temp = createTempCopy();

        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                double sum = 0.0;
                int count = 0;
                
                for (int dy = -radius; dy <= radius; dy++) {
                    for (int dx = -radius; dx <= radius; dx++) {
                        int ny = y + dy;
                        int nx = x + dx;
                        
                        if (ny >= 0 && ny < height && nx >= 0 && nx < width) {
                            sum += temp[ny][nx];
                            count++;
                        }
                    }
                }
                
                grayData[y][x] = (count > 0) ? (sum / count) : temp[y][x];
            }
        }

        freeTempCopy(temp);
        syncToImg();
    }

    /**
     * @brief Filtre gaussien sur l'image grayscale.
     * 
     * @param kernelSize Taille de la fenêtre
     * @param sigma Écart-type de la gaussienne
     */
    void filtreGaussien(int kernelSize = 5, double sigma = 1.0) {
        if (kernelSize < 1 || kernelSize % 2 == 0) {
            throw std::runtime_error("taille noyau impair");
        }
        if (sigma <= 0.0) {
            throw std::runtime_error("sigma positif");
        }

        const int radius = kernelSize / 2;
        const double sigma2 = 2.0 * sigma * sigma;
        
        // NOTE: allocation dynamique du noyau gaussien 2D
        double** kernel = new double*[kernelSize];
        for (int i = 0; i < kernelSize; i++) {
            kernel[i] = new double[kernelSize];
        }
        
        double kernelSum = 0.0;
        
        for (int dy = -radius; dy <= radius; dy++) {
            for (int dx = -radius; dx <= radius; dx++) {
                double dist2 = dx * dx + dy * dy;
                double value = std::exp(-dist2 / sigma2);
                kernel[dy + radius][dx + radius] = value;
                kernelSum += value;
            }
        }
        
        // NOTE: normalisation du noyau
        for (int dy = 0; dy < kernelSize; dy++) {
            for (int dx = 0; dx < kernelSize; dx++) {
                kernel[dy][dx] /= kernelSum;
            }
        }
        
        double** temp = createTempCopy();

        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                double sum = 0.0;
                
                for (int dy = -radius; dy <= radius; dy++) {
                    for (int dx = -radius; dx <= radius; dx++) {
                        int ny = y + dy;
                        int nx = x + dx;
                        
                        if (ny >= 0 && ny < height && nx >= 0 && nx < width) {
                            double weight = kernel[dy + radius][dx + radius];
                            sum += weight * temp[ny][nx];
                        }
                    }
                }
                
                grayData[y][x] = clamp(sum, 0.0, 255.0);
            }
        }

        // NOTE: libération du noyau
        for (int i = 0; i < kernelSize; i++) {
            delete[] kernel[i];
        }
        delete[] kernel;
        
        freeTempCopy(temp);
        syncToImg();
    }

    /**
     * @brief Filtre médian sur l'image grayscale.
     * 
     * @param kernelSize Taille de la fenêtre
     */
    void filtreMedian(int kernelSize = 3) {
        if (kernelSize < 1 || kernelSize % 2 == 0) {
            throw std::runtime_error("taille noyau impair");
        }

        const int radius = kernelSize / 2;
        const int maxSize = kernelSize * kernelSize;
        double** temp = createTempCopy();

        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                double* values = new double[maxSize];
                int count = 0;
                
                // NOTE: collecte des valeurs du voisinage
                for (int dy = -radius; dy <= radius; dy++) {
                    for (int dx = -radius; dx <= radius; dx++) {
                        int ny = y + dy;
                        int nx = x + dx;
                        
                        if (ny >= 0 && ny < height && nx >= 0 && nx < width) {
                            values[count++] = temp[ny][nx];
                        }
                    }
                }
                
                if (count > 0) {
                    // NOTE: tri par sélection pour trouver la médiane
                    for (int i = 0; i < count - 1; i++) {
                        int minIdx = i;
                        for (int j = i + 1; j < count; j++) {
                            if (values[j] < values[minIdx]) {
                                minIdx = j;
                            }
                        }
                        if (minIdx != i) {
                            double tmp = values[i];
                            values[i] = values[minIdx];
                            values[minIdx] = tmp;
                        }
                    }
                    
                    grayData[y][x] = values[count / 2];
                } else {
                    grayData[y][x] = temp[y][x];
                }
                
                delete[] values;
            }
        }

        freeTempCopy(temp);
        syncToImg();
    }

    /**
     * @brief Filtre de Sobel sur l'image grayscale.
     */
    void filtreSobel() {
        double** temp = createTempCopy();
        
        // NOTE: masques de Sobel 3x3
        const int sobelX[3][3] = {
            {-1, 0, +1},
            {-2, 0, +2},
            {-1, 0, +1}
        };
        const int sobelY[3][3] = {
            {-1, -2, -1},
            { 0,  0,  0},
            {+1, +2, +1}
        };

        // NOTE: initialisation des bords à 0
        for (int y = 0; y < height; y++) {
            if (y == 0 || y == height - 1) {
                for (int x = 0; x < width; x++) {
                    grayData[y][x] = 0.0;
                }
            } else {
                grayData[y][0] = 0.0;
                grayData[y][width - 1] = 0.0;
            }
        }

        for (int y = 1; y < height - 1; y++) {
            for (int x = 1; x < width - 1; x++) {
                double gx = 0.0;
                double gy = 0.0;
                
                for (int dy = -1; dy <= 1; dy++) {
                    for (int dx = -1; dx <= 1; dx++) {
                        int ny = y + dy;
                        int nx = x + dx;
                        double val = temp[ny][nx];
                        
                        gx += val * sobelX[dy + 1][dx + 1];
                        gy += val * sobelY[dy + 1][dx + 1];
                    }
                }
                
                // NOTE: magnitude du gradient
                double magnitude = std::sqrt(gx * gx + gy * gy);
                grayData[y][x] = clamp(magnitude, 0.0, 255.0);
            }
        }

        freeTempCopy(temp);
        syncToImg();
    }

    /**
     * @brief Filtre de Prewitt sur l'image grayscale.
     */
    void filtrePrewitt() {
        double** temp = createTempCopy();
        
        // NOTE: masques de Prewitt 3x3
        const int prewittX[3][3] = {
            {-1, 0, +1},
            {-1, 0, +1},
            {-1, 0, +1}
        };
        const int prewittY[3][3] = {
            {-1, -1, -1},
            { 0,  0,  0},
            {+1, +1, +1}
        };

        // NOTE: initialisation des bords à 0
        for (int y = 0; y < height; y++) {
            if (y == 0 || y == height - 1) {
                for (int x = 0; x < width; x++) {
                    grayData[y][x] = 0.0;
                }
            } else {
                grayData[y][0] = 0.0;
                grayData[y][width - 1] = 0.0;
            }
        }

        for (int y = 1; y < height - 1; y++) {
            for (int x = 1; x < width - 1; x++) {
                double gx = 0.0;
                double gy = 0.0;
                
                for (int dy = -1; dy <= 1; dy++) {
                    for (int dx = -1; dx <= 1; dx++) {
                        int ny = y + dy;
                        int nx = x + dx;
                        double val = temp[ny][nx];
                        
                        gx += val * prewittX[dy + 1][dx + 1];
                        gy += val * prewittY[dy + 1][dx + 1];
                    }
                }
                
                double magnitude = std::sqrt(gx * gx + gy * gy);
                grayData[y][x] = clamp(magnitude, 0.0, 255.0);
            }
        }

        freeTempCopy(temp);
        syncToImg();
    }

    /**
     * @brief Filtre de Canny sur l'image grayscale.
     * 
     * @param lowThreshold Seuil bas pour l'hystérésis
     * @param highThreshold Seuil haut pour l'hystérésis
     */
    void filtreCanny(double lowThreshold = 50.0, double highThreshold = 150.0) {
        // NOTE: étape 1 - lissage gaussien
        filtreGaussien(5, 1.4);
        
        double** temp = createTempCopy();
        double** gradient = new double*[height];
        double** direction = new double*[height];
        
        // NOTE: initialisation à zéro des tableaux gradient et direction
        for (int i = 0; i < height; i++) {
            gradient[i] = new double[width];
            direction[i] = new double[width];
            for (int j = 0; j < width; j++) {
                gradient[i][j] = 0.0;
                direction[i][j] = 0.0;
            }
        }
        
        // NOTE: étape 2 - calcul du gradient avec Sobel
        const int sobelX[3][3] = {{-1,0,+1},{-2,0,+2},{-1,0,+1}};
        const int sobelY[3][3] = {{-1,-2,-1},{0,0,0},{+1,+2,+1}};
        
        for (int y = 1; y < height - 1; y++) {
            for (int x = 1; x < width - 1; x++) {
                double gx = 0.0, gy = 0.0;
                
                for (int dy = -1; dy <= 1; dy++) {
                    for (int dx = -1; dx <= 1; dx++) {
                        double val = temp[y + dy][x + dx];
                        gx += val * sobelX[dy + 1][dx + 1];
                        gy += val * sobelY[dy + 1][dx + 1];
                    }
                }
                
                gradient[y][x] = std::sqrt(gx * gx + gy * gy);
                direction[y][x] = std::atan2(gy, gx);
            }
        }
        
        // NOTE: étape 3 - suppression des non-maximums
        for (int y = 1; y < height - 1; y++) {
            for (int x = 1; x < width - 1; x++) {
                double angle = direction[y][x];
                double mag = gradient[y][x];
                
                // NOTE: quantification de la direction
                angle = angle * 180.0 / 3.14159265;
                if (angle < 0) angle += 180.0;
                
                double neighbor1 = 0.0, neighbor2 = 0.0;
                
                if ((angle >= 0 && angle < 22.5) || (angle >= 157.5 && angle <= 180)) {
                    neighbor1 = gradient[y][x - 1];
                    neighbor2 = gradient[y][x + 1];
                } else if (angle >= 22.5 && angle < 67.5) {
                    neighbor1 = gradient[y - 1][x + 1];
                    neighbor2 = gradient[y + 1][x - 1];
                } else if (angle >= 67.5 && angle < 112.5) {
                    neighbor1 = gradient[y - 1][x];
                    neighbor2 = gradient[y + 1][x];
                } else {
                    neighbor1 = gradient[y - 1][x - 1];
                    neighbor2 = gradient[y + 1][x + 1];
                }
                
                if (mag < neighbor1 || mag < neighbor2) {
                    grayData[y][x] = 0.0;
                } else {
                    grayData[y][x] = mag;
                }
            }
        }
        
        // NOTE: étape 4 - seuillage par hystérésis
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                double val = grayData[y][x];
                if (val >= highThreshold) {
                    grayData[y][x] = 255.0;
                } else if (val < lowThreshold) {
                    grayData[y][x] = 0.0;
                } else {
                    bool hasStrongNeighbor = false;
                    for (int dy = -1; dy <= 1 && !hasStrongNeighbor; dy++) {
                        for (int dx = -1; dx <= 1 && !hasStrongNeighbor; dx++) {
                            int ny = y + dy, nx = x + dx;
                            if (ny >= 0 && ny < height && nx >= 0 && nx < width) {
                                if (grayData[ny][nx] >= highThreshold) {
                                    hasStrongNeighbor = true;
                                }
                            }
                        }
                    }
                    grayData[y][x] = hasStrongNeighbor ? 255.0 : 0.0;
                }
            }
        }
        
        freeTempCopy(temp);
        for (int i = 0; i < height; i++) {
            delete[] gradient[i];
            delete[] direction[i];
        }
        delete[] gradient;
        delete[] direction;
        
        syncToImg();
    }

    /**
     * @brief Filtre bilatéral sur l'image grayscale.
     * 
     * @param kernelSize Taille de la fenêtre
     * @param sigmaSpatial Écart-type spatial
     * @param sigmaRange Écart-type d'intensité
     */
    void filtreBilateral(int kernelSize = 5, double sigmaSpatial = 50.0, double sigmaRange = 50.0) {
        if (kernelSize < 1 || kernelSize % 2 == 0) {
            throw std::runtime_error("taille noyau impair");
        }
        if (sigmaSpatial <= 0.0 || sigmaRange <= 0.0) {
            throw std::runtime_error("sigma positif");
        }

        const int radius = kernelSize / 2;
        const double sigmaS2 = 2.0 * sigmaSpatial * sigmaSpatial;
        const double sigmaR2 = 2.0 * sigmaRange * sigmaRange;
        double** temp = createTempCopy();

        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                double centerVal = temp[y][x];
                double sum = 0.0;
                double weightSum = 0.0;
                
                for (int dy = -radius; dy <= radius; dy++) {
                    for (int dx = -radius; dx <= radius; dx++) {
                        int ny = y + dy;
                        int nx = x + dx;
                        
                        if (ny >= 0 && ny < height && nx >= 0 && nx < width) {
                            double neighborVal = temp[ny][nx];
                            
                            // NOTE: pondération spatiale
                            double spatialDist2 = dx * dx + dy * dy;
                            double spatialWeight = std::exp(-spatialDist2 / sigmaS2);
                            
                            // NOTE: pondération d'intensité
                            double valueDiff = centerVal - neighborVal;
                            double rangeWeight = std::exp(-(valueDiff * valueDiff) / sigmaR2);
                            
                            // NOTE: poids combiné
                            double weight = spatialWeight * rangeWeight;
                            
                            sum += weight * neighborVal;
                            weightSum += weight;
                        }
                    }
                }
                
                grayData[y][x] = (weightSum > 0.0) ? (sum / weightSum) : centerVal;
            }
        }

        freeTempCopy(temp);
        syncToImg();
    }

    /**
     * @brief Convertit l'image RGB en niveaux de gris (déjà fait lors de la création).
     * 
     * @param method Méthode de conversion (ignoré, toujours REC601)
     */
    void toGrayscale(Grayscale::Method method = Grayscale::Method::REC601) {
        // NOTE: déjà en niveaux de gris, rien à faire
        syncToImg();
    }

    /**
     * @brief Applique une transformation à tous les pixels de l'image grayscale.
     * 
     * @tparam Func Type de la fonction de transformation
     * @param transform Fonction prenant un double et retournant un double
     */
    template<typename Func>
    void applyPixelTransform(Func transform) {
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                grayData[y][x] = transform(grayData[y][x]);
            }
        }
        syncToImg();
    }

    /**
     * @brief Accesseurs.
     */
    int getWidth() const { return width; }
    int getHeight() const { return height; }
    
private:
    /**
     * @brief Crée une copie temporaire des données grayscale.
     */
    double** createTempCopy() const {
        double** temp = new double*[height];
        for (int i = 0; i < height; i++) {
            temp[i] = new double[width];
            for (int j = 0; j < width; j++) {
                temp[i][j] = grayData[i][j];
            }
        }
        return temp;
    }
    
    /**
     * @brief Libère une copie temporaire.
     */
    void freeTempCopy(double** temp) const {
        if (temp) {
            for (int i = 0; i < height; i++) {
                delete[] temp[i];
            }
            delete[] temp;
        }
    }
};

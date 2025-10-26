#pragma once

#include <vector>
#include <stdexcept>
#include "../utils/ImageUtils.hpp"

/**
 * @file ImageData.hpp
 * @brief Classe de base pour le stockage des données d'image
 *
 * Fournit une abstraction pour gérer les données d'image avec gestion
 * automatique de la mémoire via std::vector (RAII).
 */
namespace ImageProcessing {

/**
 * @brief Classe de base pour le stockage et la manipulation des données d'image
 *
 * Cette classe encapsule les données d'une image sous forme de tableau 2D
 * utilisant std::vector pour une gestion automatique de la mémoire (RAII).
 * Elle fournit des méthodes de base pour accéder et manipuler les données.
 *
 * @note Utilise le principe RAII : pas de gestion manuelle de la mémoire
 * @note Thread-safe pour les lectures simultanées (pas de modification concurrente)
 */
class ImageData {
protected:
    std::vector<std::vector<double>> data;   ///< Données de l'image (row-major order)
    int width;                                ///< Largeur de l'image en pixels
    int height;                               ///< Hauteur de l'image en pixels
    int colors;                               ///< Nombre de canaux de couleur par pixel

public:
    /**
     * @brief Constructeur par défaut
     *
     * Initialise une image vide avec des dimensions nulles.
     */
    ImageData() : width(0), height(0), colors(0) {}

    /**
     * @brief Constructeur avec dimensions
     *
     * Crée une image avec les dimensions spécifiées, initialisée à zéro.
     *
     * @param w Largeur de l'image (doit être > 0)
     * @param h Hauteur de l'image (doit être > 0)
     * @param c Nombre de canaux de couleur (1=grayscale, 3=RGB)
     *
     * @throws std::invalid_argument Si les dimensions sont invalides (<= 0)
     *
     * @example
     * ImageData img(640, 480, 3); // Image RGB 640x480
     * ImageData gray(640, 480, 1); // Image grayscale 640x480
     */
    ImageData(int w, int h, int c) : width(w), height(h), colors(c) {
        if (w <= 0 || h <= 0 || c <= 0) {
            throw std::invalid_argument("dimensions invalides");
        }
        allocate();
    }

    /**
     * @brief Destructeur virtuel
     *
     * @note Virtuel pour permettre la destruction polymorphique
     * @note La mémoire est automatiquement libérée par std::vector (RAII)
     */
    virtual ~ImageData() = default;

    /**
     * @brief Constructeur de copie
     *
     * Effectue une copie profonde de l'image source.
     *
     * @param other Image source à copier
     */
    ImageData(const ImageData& other)
        : data(other.data), width(other.width), height(other.height), colors(other.colors) {}

    /**
     * @brief Opérateur d'affectation par copie
     *
     * Effectue une copie profonde de l'image source.
     *
     * @param other Image source à copier
     * @return ImageData& Référence vers cette instance
     */
    ImageData& operator=(const ImageData& other) {
        if (this != &other) {
            data = other.data;
            width = other.width;
            height = other.height;
            colors = other.colors;
        }
        return *this;
    }

    /**
     * @brief Constructeur de déplacement
     *
     * Transfère les ressources de l'image source sans copie.
     *
     * @param other Image source à déplacer
     */
    ImageData(ImageData&& other) noexcept
        : data(std::move(other.data)),
          width(other.width),
          height(other.height),
          colors(other.colors) {
        other.width = 0;
        other.height = 0;
        other.colors = 0;
    }

    /**
     * @brief Opérateur d'affectation par déplacement
     *
     * Transfère les ressources de l'image source sans copie.
     *
     * @param other Image source à déplacer
     * @return ImageData& Référence vers cette instance
     */
    ImageData& operator=(ImageData&& other) noexcept {
        if (this != &other) {
            data = std::move(other.data);
            width = other.width;
            height = other.height;
            colors = other.colors;
            other.width = 0;
            other.height = 0;
            other.colors = 0;
        }
        return *this;
    }

    /**
     * @brief Accès aux données d'une ligne (opérateur [])
     *
     * Permet d'accéder aux données d'une ligne spécifique.
     *
     * @param y Indice de la ligne
     * @return std::vector<double>& Référence vers la ligne
     *
     * @throws std::out_of_range Si y est hors limites
     *
     * @example
     * double pixelRed = img[y][x * 3 + 0];  // Canal rouge
     * double pixelGreen = img[y][x * 3 + 1]; // Canal vert
     * double pixelBlue = img[y][x * 3 + 2];  // Canal bleu
     */
    std::vector<double>& operator[](int y) {
        return data.at(y);
    }

    /**
     * @brief Accès en lecture seule aux données d'une ligne (opérateur [] const)
     *
     * @param y Indice de la ligne
     * @return const std::vector<double>& Référence constante vers la ligne
     *
     * @throws std::out_of_range Si y est hors limites
     */
    const std::vector<double>& operator[](int y) const {
        return data.at(y);
    }

    /**
     * @brief Obtient la largeur de l'image
     *
     * @return int Largeur en pixels
     */
    int getWidth() const { return width; }

    /**
     * @brief Obtient la hauteur de l'image
     *
     * @return int Hauteur en pixels
     */
    int getHeight() const { return height; }

    /**
     * @brief Obtient le nombre de canaux de couleur
     *
     * @return int Nombre de canaux (1=grayscale, 3=RGB)
     */
    int getColors() const { return colors; }

    /**
     * @brief Vérifie si l'image est en niveaux de gris
     *
     * @return bool true si l'image a un seul canal
     */
    bool isGrayscale() const { return colors == 1; }

    /**
     * @brief Obtient une référence vers les données brutes
     *
     * @return std::vector<std::vector<double>>& Référence vers les données
     *
     * @note À utiliser avec précaution, privilégier l'opérateur []
     */
    std::vector<std::vector<double>>& getData() { return data; }

    /**
     * @brief Obtient une référence constante vers les données brutes
     *
     * @return const std::vector<std::vector<double>>& Référence constante vers les données
     */
    const std::vector<std::vector<double>>& getData() const { return data; }

    /**
     * @brief Vérifie si les coordonnées sont valides
     *
     * @param x Coordonnée X
     * @param y Coordonnée Y
     * @return bool true si les coordonnées sont dans les limites
     *
     * @example
     * if (img.isValidCoordinate(x, y)) {
     *     // Accès sûr au pixel
     * }
     */
    bool isValidCoordinate(int x, int y) const {
        return ImageUtils::isValidCoordinate(x, y, width, height);
    }

    /**
     * @brief Réinitialise toutes les valeurs à zéro
     *
     * @example
     * img.clear(); // Toutes les valeurs deviennent 0.0
     */
    void clear() {
        // Remplissage manuel (implémentation de std::fill)
        for (auto& row : data) {
            for (double& val : row) {
                val = 0.0;
            }
        }
    }

    /**
     * @brief Crée une copie profonde des données
     *
     * @return std::vector<std::vector<double>> Copie des données
     *
     * @example
     * auto backup = img.createCopy();
     * // Modification de img...
     * // Restauration : img.getData() = backup;
     */
    std::vector<std::vector<double>> createCopy() const {
        return data;
    }

    /**
     * @brief Convertit une image RGB en grayscale à 1 canal
     *
     * OPTIMISATION PERFORMANCE: Réduit la consommation mémoire et CPU de 66%
     * pour les images en niveaux de gris où R=G=B.
     *
     * Prend le premier canal (R) comme valeur unique pour chaque pixel.
     * Cette méthode doit être appelée APRÈS une conversion grayscale pour
     * réduire de 3 canaux à 1 seul canal.
     *
     * @throws std::invalid_argument Si l'image n'a pas 3 canaux
     *
     * @note L'image doit déjà être en niveaux de gris (R=G=B) avant l'appel
     * @note Cette opération est irréversible (pas de retour RGB possible)
     *
     * @example
     * ImageData img(640, 480, 3);
     * // ... conversion en grayscale (R=G=B) ...
     * img.convertToSingleChannel(); // 3 canaux → 1 canal
     * // Gain mémoire: -66%, Gain CPU: -66%
     */
    void convertToSingleChannel() {
        if (colors != 3) {
            throw std::invalid_argument("convertToSingleChannel necessite 3 canaux");
        }

        // Réorganise les données: prend seulement le canal R
        for (int y = 0; y < height; ++y) {
            std::vector<double> newRow;
            newRow.reserve(width);

            for (int x = 0; x < width; ++x) {
                newRow.push_back(data[y][x * 3 + 0]); // Canal R uniquement
            }

            data[y] = std::move(newRow);
        }

        colors = 1;
    }

protected:
    /**
     * @brief Alloue la mémoire pour les données de l'image
     *
     * Initialise le vecteur 2D avec les dimensions spécifiées,
     * toutes les valeurs sont initialisées à 0.0.
     *
     * @note Méthode protégée, utilisée par les constructeurs
     */
    void allocate() {
        data.resize(height);
        for (int i = 0; i < height; ++i) {
            data[i].resize(width * colors, 0.0);
        }
    }

    /**
     * @brief Redimensionne l'image avec de nouvelles dimensions
     *
     * Détruit les données existantes et alloue un nouveau buffer
     * avec les dimensions spécifiées.
     *
     * @param w Nouvelle largeur
     * @param h Nouvelle hauteur
     * @param c Nouveau nombre de canaux
     *
     * @throws std::invalid_argument Si les dimensions sont invalides
     *
     * @note Les données existantes sont perdues
     */
    void resize(int w, int h, int c) {
        if (w <= 0 || h <= 0 || c <= 0) {
            throw std::invalid_argument("dimensions invalides");
        }
        width = w;
        height = h;
        colors = c;
        allocate();
    }
};

} // namespace ImageProcessing

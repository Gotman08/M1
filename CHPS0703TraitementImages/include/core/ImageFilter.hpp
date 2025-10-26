#pragma once

#include "ImageData.hpp"

/**
 * @file ImageFilter.hpp
 * @brief Interface abstraite pour les filtres d'image
 *
 * Définit le contrat que doivent respecter tous les filtres d'image.
 * Utilise le pattern Strategy pour permettre l'interchangeabilité des filtres.
 */
namespace ImageProcessing {

/**
 * @brief Classe abstraite de base pour tous les filtres d'image
 *
 * Cette classe définit l'interface commune pour tous les filtres d'image.
 * Elle implémente le pattern Strategy, permettant de changer dynamiquement
 * l'algorithme de filtrage appliqué à une image.
 *
 * Les classes dérivées doivent implémenter la méthode apply() pour définir
 * le comportement spécifique du filtre.
 *
 * @note Cette classe est abstraite et ne peut pas être instanciée directement
 * @note Utilisez le polymorphisme pour appliquer différents filtres
 *
 * @example
 * std::unique_ptr<ImageFilter> filter = std::make_unique<GaussianFilter>(5, 1.0);
 * filter->apply(imageData);
 */
class ImageFilter {
public:
    /**
     * @brief Destructeur virtuel
     *
     * @note Nécessaire pour permettre la destruction polymorphique
     */
    virtual ~ImageFilter() = default;

    /**
     * @brief Applique le filtre sur les données d'image
     *
     * Méthode virtuelle pure qui doit être implémentée par toutes les
     * classes dérivées. Elle définit le comportement spécifique du filtre.
     *
     * @param data Données de l'image à filtrer (modifiées en place)
     *
     * @throws std::runtime_error Si une erreur survient pendant le filtrage
     * @throws std::invalid_argument Si les paramètres du filtre sont invalides
     *
     * @note Les données sont modifiées directement (filtre en place)
     * @note Pour préserver l'original, créez une copie avant d'appliquer le filtre
     *
     * @example
     * ImageData data(640, 480, 3);
     * auto copy = data.createCopy(); // Sauvegarde optionnelle
     * filter->apply(data);
     */
    virtual void apply(ImageData& data) = 0;

    /**
     * @brief Obtient le nom du filtre
     *
     * Retourne une chaîne décrivant le filtre pour l'affichage ou le logging.
     *
     * @return const char* Nom du filtre
     *
     * @example
     * std::cout << "Application du filtre: " << filter->getName() << std::endl;
     */
    virtual const char* getName() const = 0;

protected:
    /**
     * @brief Constructeur protégé
     *
     * @note Protégé pour empêcher l'instanciation directe de la classe abstraite
     */
    ImageFilter() = default;

    /**
     * @brief Crée une copie temporaire des données pour le filtrage
     *
     * Méthode utilitaire pour les filtres qui nécessitent une copie temporaire
     * des données d'entrée afin d'éviter les effets de bord lors du traitement.
     *
     * @param data Données source à copier
     * @return std::vector<std::vector<double>> Copie des données
     *
     * @note Utilisé par les filtres convolutifs pour éviter les dépendances temporelles
     *
     * @example
     * auto temp = createTempCopy(data);
     * // Traitement utilisant temp en lecture, data en écriture
     */
    std::vector<std::vector<double>> createTempCopy(const ImageData& data) const {
        return data.createCopy();
    }

    /**
     * @brief Vérifie que les dimensions d'une image sont valides pour le filtre
     *
     * @param data Données de l'image à vérifier
     * @param minWidth Largeur minimale requise
     * @param minHeight Hauteur minimale requise
     *
     * @throws std::invalid_argument Si les dimensions sont insuffisantes
     *
     * @example
     * validateDimensions(data, 3, 3); // Pour un filtre 3x3
     */
    void validateDimensions(const ImageData& data, int minWidth, int minHeight) const {
        if (data.getWidth() < minWidth || data.getHeight() < minHeight) {
            throw std::invalid_argument("dimensions image insuffisantes pour le filtre");
        }
    }
};

/**
 * @brief Classe abstraite pour les filtres convolutifs
 *
 * Sous-classe d'ImageFilter spécialisée pour les filtres par convolution.
 * Fournit des méthodes utilitaires communes pour les opérations de convolution.
 */
class ConvolutionFilter : public ImageFilter {
protected:
    int kernelSize;  ///< Taille du noyau de convolution (impair)

    /**
     * @brief Constructeur avec taille de noyau
     *
     * @param kSize Taille du noyau (doit être impair et >= 1)
     *
     * @throws std::invalid_argument Si la taille du noyau est invalide
     */
    explicit ConvolutionFilter(int kSize) : kernelSize(kSize) {
        if (kSize < 1 || kSize % 2 == 0) {
            throw std::invalid_argument("taille noyau doit etre impaire");
        }
    }

public:
    /**
     * @brief Obtient la taille du noyau de convolution
     *
     * @return int Taille du noyau
     */
    int getKernelSize() const { return kernelSize; }

    /**
     * @brief Obtient le rayon du noyau (distance du centre au bord)
     *
     * @return int Rayon du noyau (kernelSize / 2)
     *
     * @example
     * Pour un noyau 5x5, getRadius() retourne 2
     */
    int getRadius() const { return kernelSize / 2; }

protected:
    /**
     * @brief Applique une convolution 2D sur une image
     *
     * Méthode template générique pour appliquer une convolution avec un noyau
     * personnalisé. Le functor kernelFunc est appelé pour chaque position du noyau.
     *
     * @tparam KernelFunc Type du functor du noyau
     * @param data Données de l'image (modifiées en place)
     * @param kernelFunc Fonction retournant le poids du noyau à (dy, dx)
     *
     * @note Le noyau doit être normalisé (somme = 1) pour préserver la luminosité
     *
     * @example
     * applyConvolution(data, [](int dy, int dx) {
     *     return 1.0 / 9.0; // Noyau moyen 3x3
     * });
     */
    template<typename KernelFunc>
    void applyConvolution(ImageData& data, KernelFunc kernelFunc) const {
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

                            if (ny >= 0 && ny < height && nx >= 0 && nx < width) {
                                const double weight = kernelFunc(dy, dx);
                                sum += weight * temp[ny][nx * colors + c];
                            }
                        }
                    }

                    data[y][x * colors + c] = ImageUtils::clamp(sum, 0.0, 255.0);
                }
            }
        }
    }
};

} // namespace ImageProcessing

#pragma once

#include <cstdint>

/**
 * @file ColorConversion.hpp
 * @brief Utilitaires de conversion RGB vers niveaux de gris
 *
 * Ce fichier fournit différentes méthodes de conversion d'images couleur RGB
 * vers des images en niveaux de gris, respectant les standards de l'industrie
 * et les propriétés perceptuelles de la vision humaine.
 */
namespace ImageProcessing {

/**
 * @brief Classe utilitaire pour les conversions de couleur
 *
 * Fournit des méthodes statiques pour convertir des pixels RGB en niveaux
 * de gris selon différents standards et algorithmes.
 */
class ColorConversion {
public:
    /**
     * @brief Énumération des méthodes de conversion disponibles
     */
    enum class Method {
        REC601,      ///< ITU-R BT.601 (SDTV) - recommandé par défaut
        REC709,      ///< ITU-R BT.709 (HDTV) - standard moderne
        AVERAGE,     ///< Moyenne arithmétique simple
        LIGHTNESS,   ///< Luminosité HSL
        MAXIMUM,     ///< Valeur maximale RGB
        MINIMUM,     ///< Valeur minimale RGB
        RED,         ///< Canal rouge uniquement
        GREEN,       ///< Canal vert uniquement
        BLUE         ///< Canal bleu uniquement
    };

    /**
     * @brief Conversion RGB vers luminance selon la recommandation ITU-R BT.601 (SDTV)
     *
     * Formule pondérée reflétant la sensibilité de l'œil humain :
     * Y = 0.299*R + 0.587*G + 0.114*B
     *
     * Cette méthode respecte la perception humaine où l'œil est plus sensible
     * au vert (57%), puis au rouge (30%), et moins au bleu (11%).
     * Standard pour la télévision à définition standard (SDTV).
     *
     * @param r Composante rouge [0-255]
     * @param g Composante verte [0-255]
     * @param b Composante bleue [0-255]
     * @return double Valeur de luminance [0-255]
     *
     * @see ITU-R Recommendation BT.601
     *
     * @example
     * double gray = ColorConversion::rec601(255, 128, 64);
     */
    static inline double rec601(double r, double g, double b) {
        return 0.299 * r + 0.587 * g + 0.114 * b;
    }

    /**
     * @brief Conversion RGB vers luminance selon la recommandation ITU-R BT.709 (HDTV)
     *
     * Formule moderne pour la télévision haute définition :
     * Y = 0.2126*R + 0.7152*G + 0.0722*B
     *
     * Standard pour la HDTV et le contenu numérique moderne. Ajuste les coefficients
     * pour refléter les primaires de couleur des écrans modernes et la réponse
     * colorimétrique de l'œil humain dans l'espace sRGB.
     *
     * @param r Composante rouge [0-255]
     * @param g Composante verte [0-255]
     * @param b Composante bleue [0-255]
     * @return double Valeur de luminance [0-255]
     *
     * @see ITU-R Recommendation BT.709
     *
     * @example
     * double gray = ColorConversion::rec709(255, 128, 64);
     */
    static inline double rec709(double r, double g, double b) {
        return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    }

    /**
     * @brief Conversion par moyenne arithmétique simple (méthode rapide)
     *
     * Formule : Gray = (R + G + B) / 3
     *
     * Méthode la plus simple et rapide mais non perceptuelle. Donne un poids
     * égal à chaque canal sans tenir compte de la sensibilité de l'œil.
     * Utile pour un traitement rapide quand la précision perceptuelle n'est pas critique.
     *
     * @param r Composante rouge [0-255]
     * @param g Composante verte [0-255]
     * @param b Composante bleue [0-255]
     * @return double Valeur de gris [0-255]
     *
     * @note Non recommandé pour la visualisation (résultats peu naturels)
     *
     * @example
     * double gray = ColorConversion::average(255, 128, 64);
     */
    static inline double average(double r, double g, double b) {
        return (r + g + b) / 3.0;
    }

    /**
     * @brief Conversion par luminosité (lightness) selon le modèle HSL
     *
     * Formule : Lightness = (max(R,G,B) + min(R,G,B)) / 2
     *
     * Calcule la composante L du modèle HSL (Hue, Saturation, Lightness).
     * Représente la luminosité perçue en prenant la moyenne entre la valeur
     * maximale et minimale des canaux RGB.
     *
     * @param r Composante rouge [0-255]
     * @param g Composante verte [0-255]
     * @param b Composante bleue [0-255]
     * @return double Valeur de lightness [0-255]
     *
     * @see Modèle HSL (Hue, Saturation, Lightness)
     *
     * @example
     * double gray = ColorConversion::lightness(255, 128, 64);
     */
    static inline double lightness(double r, double g, double b) {
        double maxVal = (r > g) ? ((r > b) ? r : b) : ((g > b) ? g : b);
        double minVal = (r < g) ? ((r < b) ? r : b) : ((g < b) ? g : b);
        return (maxVal + minVal) / 2.0;
    }

    /**
     * @brief Conversion par luminosité maximale (max RGB)
     *
     * Formule : Gray = max(R, G, B)
     *
     * Sélectionne la valeur maximale parmi les trois canaux. Préserve les zones
     * lumineuses et produit des images plus claires. Utile pour détecter les
     * zones de forte intensité.
     *
     * @param r Composante rouge [0-255]
     * @param g Composante verte [0-255]
     * @param b Composante bleue [0-255]
     * @return double Valeur maximale [0-255]
     *
     * @example
     * double gray = ColorConversion::maximum(255, 128, 64); // retourne 255
     */
    static inline double maximum(double r, double g, double b) {
        double max1 = (r > g) ? r : g;
        return (max1 > b) ? max1 : b;
    }

    /**
     * @brief Conversion par luminosité minimale (min RGB)
     *
     * Formule : Gray = min(R, G, B)
     *
     * Sélectionne la valeur minimale parmi les trois canaux. Préserve les zones
     * sombres et produit des images plus sombres. Utile pour détecter les
     * ombres et les zones de faible intensité.
     *
     * @param r Composante rouge [0-255]
     * @param g Composante verte [0-255]
     * @param b Composante bleue [0-255]
     * @return double Valeur minimale [0-255]
     *
     * @example
     * double gray = ColorConversion::minimum(255, 128, 64); // retourne 64
     */
    static inline double minimum(double r, double g, double b) {
        double min1 = (r < g) ? r : g;
        return (min1 < b) ? min1 : b;
    }

    /**
     * @brief Extraction du canal rouge uniquement
     *
     * Formule : Gray = R
     *
     * Conserve uniquement la composante rouge. Utile pour l'analyse spectrale
     * ou lorsque l'information du canal rouge est la plus pertinente.
     *
     * @param r Composante rouge [0-255]
     * @param g Composante verte [0-255] (ignorée)
     * @param b Composante bleue [0-255] (ignorée)
     * @return double Valeur du canal rouge [0-255]
     *
     * @example
     * double gray = ColorConversion::redChannel(255, 128, 64); // retourne 255
     */
    static inline double redChannel(double r, double /*g*/, double /*b*/) {
        return r;
    }

    /**
     * @brief Extraction du canal vert uniquement
     *
     * Formule : Gray = G
     *
     * Conserve uniquement la composante verte. Le canal vert contient souvent
     * le plus d'information de luminance car l'œil y est le plus sensible.
     *
     * @param r Composante rouge [0-255] (ignorée)
     * @param g Composante verte [0-255]
     * @param b Composante bleue [0-255] (ignorée)
     * @return double Valeur du canal vert [0-255]
     *
     * @example
     * double gray = ColorConversion::greenChannel(255, 128, 64); // retourne 128
     */
    static inline double greenChannel(double /*r*/, double g, double /*b*/) {
        return g;
    }

    /**
     * @brief Extraction du canal bleu uniquement
     *
     * Formule : Gray = B
     *
     * Conserve uniquement la composante bleue. Utile pour certaines analyses
     * spectrales ou applications spécifiques (ex: détection sous-marine).
     *
     * @param r Composante rouge [0-255] (ignorée)
     * @param g Composante verte [0-255] (ignorée)
     * @param b Composante bleue [0-255]
     * @return double Valeur du canal bleu [0-255]
     *
     * @example
     * double gray = ColorConversion::blueChannel(255, 128, 64); // retourne 64
     */
    static inline double blueChannel(double /*r*/, double /*g*/, double b) {
        return b;
    }

    /**
     * @brief Conversion RGB vers niveaux de gris avec méthode sélectionnable
     *
     * Fonction générique permettant de choisir la méthode de conversion.
     * Par défaut utilise REC601 (standard industriel pour compatibilité maximale).
     *
     * @param r Composante rouge [0-255]
     * @param g Composante verte [0-255]
     * @param b Composante bleue [0-255]
     * @param method Méthode de conversion (défaut: REC601)
     * @return double Valeur de gris [0-255]
     *
     * @example
     * double gray1 = ColorConversion::convert(255, 128, 64); // Utilise REC601 par défaut
     * double gray2 = ColorConversion::convert(255, 128, 64, Method::REC709);
     * double gray3 = ColorConversion::convert(255, 128, 64, Method::AVERAGE);
     */
    static inline double convert(double r, double g, double b, Method method = Method::REC601) {
        switch (method) {
            case Method::REC601:     return rec601(r, g, b);
            case Method::REC709:     return rec709(r, g, b);
            case Method::AVERAGE:    return average(r, g, b);
            case Method::LIGHTNESS:  return lightness(r, g, b);
            case Method::MAXIMUM:    return maximum(r, g, b);
            case Method::MINIMUM:    return minimum(r, g, b);
            case Method::RED:        return redChannel(r, g, b);
            case Method::GREEN:      return greenChannel(r, g, b);
            case Method::BLUE:       return blueChannel(r, g, b);
            default:                 return rec601(r, g, b);
        }
    }

    /**
     * @brief Retourne le nom de la méthode de conversion
     *
     * @param method Méthode de conversion
     * @return const char* Nom descriptif de la méthode
     *
     * @example
     * const char* name = ColorConversion::getMethodName(Method::REC601);
     * // name == "rec601 sdtv"
     */
    static inline const char* getMethodName(Method method) {
        switch (method) {
            case Method::REC601:     return "rec601 sdtv";
            case Method::REC709:     return "rec709 hdtv";
            case Method::AVERAGE:    return "moyenne";
            case Method::LIGHTNESS:  return "lightness hsl";
            case Method::MAXIMUM:    return "max rgb";
            case Method::MINIMUM:    return "min rgb";
            case Method::RED:        return "canal rouge";
            case Method::GREEN:      return "canal vert";
            case Method::BLUE:       return "canal bleu";
            default:                 return "inconnu";
        }
    }

private:
    // Constructeur privé pour empêcher l'instanciation
    ColorConversion() = delete;
    ~ColorConversion() = delete;
    ColorConversion(const ColorConversion&) = delete;
    ColorConversion& operator=(const ColorConversion&) = delete;
};

} // namespace ImageProcessing

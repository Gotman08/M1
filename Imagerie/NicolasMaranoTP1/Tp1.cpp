#include <iostream>
#include <iomanip>
#include <algorithm>
#include <limits>
#include <cstdint>
#include "image.hpp"
#include "menu.hpp"
#include "Operations.hpp"

using std::cout;
using std::cin;
using std::endl;


/**
 * @brief Classe Img implémentant le pattern Singleton pour la gestion d'image.
 * 
 * Cette classe modélise une image I : Omega->V au sens du cours, où :
 * - Omega ⊂ Z^2 représente le support spatial de l'image (grille cartésienne)
 * - V = [0,255]^3 est l'espace des valeurs RGB (quantification 8 bits)
 * L'image peut être vue comme un vecteur VI e R^n dans l'espace vectoriel des images,
 * permettant l'application d'opérateurs linéaires H : E->F et non-linéaires.
 * 
 * @note Sauvegarde de l'image originale pour permettre la composition d'opérateurs
 * @see CM02 pour la définition image = vecteur, CM04 pour l'espace vectoriel
 */
class Img {
private:
    double** data;
    int width;
    int height;
    int colors;
    double** originalData; 
    
    static Img* instance;

    /**
     * @brief Constructeur privé pour le pattern Singleton.
     * 
     * @param w Largeur de l'image 0 pour charger depuis image.hpp
     * @param h Hauteur de l'image 0 pour charger depuis image.hpp
     * @param c Nombre de canaux de couleur 0 pour valeur par défaut de 3
     */
    Img(int w, int h, int c) : data(nullptr), width(w), height(h), colors(c), originalData(nullptr) {

        if (w == 0 || h == 0 || c == 0) {
            if (W <= 0 || H <= 0) {
                throw std::runtime_error("dimensions invalides");
            }
            width  = W;
            height = H;
            colors = 3;

            allocateMemory();
            loadImageData();
            saveOriginal();
            return;
        }

        validateDimensions();
        allocateMemory();
        saveOriginal();
    }
    
    /**
     * @brief Alloue la mémoire pour les données de l'image.
     */
    void allocateMemory() {
        data = new double*[height];

        for (int i = 0; i < height; i++) {
            data[i] = new double[width * colors];
            for (int j = 0; j < width * colors; j++) {
                data[i][j] = 0.0;
            }
        }
    }

    /**
     * @brief Valide les dimensions de l'image.
     * @throws std::runtime_error Si dimensions invalides
     */
    void validateDimensions() const {
        if (width <= 0 || height <= 0) {
            throw std::runtime_error("dimensions invalides");
        }
    }

    /**
     * @brief Écrête une valeur dans l'intervalle [min, max].
     * @param value Valeur à écrêter
     * @param minVal Valeur minimale
     * @param maxVal Valeur maximale
     * @return double Valeur écrêtée
     */
    static inline double clamp(double value, double minVal, double maxVal) {
        if (value < minVal) return minVal;
        if (value > maxVal) return maxVal;
        return value;
    }
    
    /**
     * @brief Charge les données depuis le buffer IMG global.
     */
    void loadImageData() {
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                size_t base = (static_cast<size_t>(y) * width + x) * 3;
                for (int k = 0; k < colors; k++) {
                    data[y][x * colors + k] = static_cast<double>(IMG[base + k]);
                }
            }
        }
    }
    
    /**
     * @brief Sauvegarde une copie de l'image originale pour permettre les resets.
     */
    void saveOriginal() {
        if (originalData) {
            freeMemory(originalData);
        }
        
        originalData = new double*[height];
        for (int i = 0; i < height; i++) {
            originalData[i] = new double[width * colors];
            std::copy(data[i], data[i] + (width * colors), originalData[i]);
        }
    }
    
    /**
     * @brief Libère la mémoire allouée pour un tableau 2D.
     * @param ptr Pointeur vers le tableau à libérer
     */
    void freeMemory(double** ptr) {
        if (ptr) {
            for (int i = 0; i < height; i++) {
                delete[] ptr[i];
            }
            delete[] ptr;
        }
    }

    /**
     * @brief Destructeur privé.
     */
    ~Img() {
        freeMemory(data);
        freeMemory(originalData);
        data = nullptr;
        originalData = nullptr;
    }

    // Suppression du constructeur de copie
    Img(const Img& other) = delete;
    
    // Suppression de l'opérateur d'affectation
    Img& operator=(const Img& other) = delete;
    
    // Suppression du constructeur de déplacement
    Img(Img&& other) = delete;
    
    // Suppression de l'opérateur d'affectation par déplacement
    Img& operator=(Img&& other) = delete;

public:
    /**
     * @brief Retourne l'instance unique de la classe Img.
     * 
     * @param w Largeur de l'image (utilisé uniquement lors de la première création)
     * @param h Hauteur de l'image (utilisé uniquement lors de la première création)
     * @param c Nombre de canaux de couleur (utilisé uniquement lors de la première création)
     * @return Img& Référence vers l'instance unique
     */
    static Img& getInstance(int w = 0, int h = 0, int c = 0) {
        if (instance == nullptr) {
            instance = new Img(w, h, c);
        }
        return *instance;
    }
    
    /**
     * @brief Détruit l'instance unique de la classe Img.
     */
    static void destroyInstance() {
        if (instance != nullptr) {
            delete instance;
            instance = nullptr;
        }
    }

    double* operator[](int i) { return data[i]; }
    const double* operator[](int i) const { return data[i]; }

    double** getImg() const { return data; }
    int getWidth()  const { return width; }
    int getHeight() const { return height; }
    int getColors() const { return colors; }

    /**
     * @brief Conversion sûre double->uint8 avec écrêtage dans [0,255].
     * 
     * Assure la quantification finale vers l'espace V = {0,1,...,255} des images
     * 8 bits. L'écrêtage préserve les bornes après application d'opérateurs
     * pouvant déborder (rehaussement, quantification).
     * 
     * @param v Valeur en virgule flottante
     * @return uint8_t Valeur quantifiée et écrêtée
     * @note Arrondi à 0.5 près avant truncature entière
     */
    static inline uint8_t to_u8(double v) {
        if (v < 0.0) return 0;
        if (v > 255.0) return 255;
        return static_cast<uint8_t>(v + 0.5);
    }

    /**
     * @brief Extrait les composantes RGB d'un pixel à la position (y, x).
     * 
     * @param y Coordonnée Y du pixel
     * @param x Coordonnée X du pixel
     * @param r Référence pour stocker la composante rouge
     * @param g Référence pour stocker la composante verte
     * @param b Référence pour stocker la composante bleue
     */
    inline void getRGB(int y, int x, int &r, int &g, int &b) const {
        const int C = colors;
        const int base = x * C;
        r = to_u8(data[y][base + 0]);
        g = (C > 1) ? to_u8(data[y][base + 1]) : r;
        b = (C > 2) ? to_u8(data[y][base + 2]) : r;
    }

    /**
     * @brief Affiche un aperçu de l'image dans le terminal avec des caractères Unicode colorés.
     * 
     * @param maxCols Nombre maximum de colonnes à afficher
     * @param maxRows Nombre maximum de lignes à afficher
     */
    void printPreview(int maxCols = 100, int maxRows = 40) const {
        if (width <= 0 || height <= 0) { 
            cout << "image vide\n"; 
            return; 
        }

        int targetW = (width < maxCols) ? width : maxCols;
        if (targetW < 1) targetW = 1;
        
        int targetH = (height < maxRows * 2) ? height : maxRows * 2;
        if (targetH < 1) targetH = 1;

        const double sx = static_cast<double>(width)  / targetW;
        const double sy = static_cast<double>(height) / targetH;

        for (int ty = 0; ty < targetH; ty += 2) {
            int yTop = static_cast<int>(ty * sy);
            yTop = (yTop > height - 1) ? height - 1 : yTop;
            
            int yBot = static_cast<int>((ty + 1) * sy);
            yBot = (yBot > height - 1) ? height - 1 : yBot;

            for (int tx = 0; tx < targetW; ++tx) {
                int xSrc = static_cast<int>(tx * sx);
                xSrc = (xSrc > width - 1) ? width - 1 : xSrc;

                int rt, gt, bt; getRGB(yTop, xSrc, rt, gt, bt);
                int rb, gb, bb; getRGB(yBot, xSrc, rb, gb, bb);

                cout << "\033[38;2;" << rt << ";" << gt << ";" << bt << "m"
                     << "\033[48;2;" << rb << ";" << gb << ";" << bb << "m"
                     << "▀";
            }
            cout << "\033[0m\n";
        }
        cout << endl;
    }

    /**
     * @brief Affiche une région d'intérêt (ROI) de l'image avec les valeurs de pixels.
     * 
     * @param y0 Coordonnée Y de début
     * @param y1 Coordonnée Y de fin (exclusive)
     * @param x0 Coordonnée X de début
     * @param x1 Coordonnée X de fin (exclusive)
     * @param step Pas d'échantillonnage (1 = tous les pixels)
     * @param channel Canal à afficher (-1=RGB, 0=R, 1=G, 2=B)
     */
    void printROI(int y0, int y1, int x0, int x1, int step = 1, int channel = -1) const {
        if (y0 < 0) y0 = 0;
        if (x0 < 0) x0 = 0;
        if (y1 > height) y1 = height;
        if (x1 > width) x1 = width;
        
        if (y0 >= y1 || x0 >= x1) { 
            cout << "roi vide\n"; 
            return; 
        }

        for (int y = y0; y < y1; y += step) {
            for (int x = x0; x < x1; x += step) {
                int r, g, b; 
                getRGB(y, x, r, g, b);
                
                if (channel == 0) {
                    cout << std::setw(3) << r << " ";
                } else if (channel == 1) {
                    cout << std::setw(3) << g << " ";
                } else if (channel == 2) {
                    cout << std::setw(3) << b << " ";
                } else {
                    cout << "[" << std::setw(3) << r
                         << "," << std::setw(3) << g
                         << "," << std::setw(3) << b << "] ";
                }
            }
            cout << "\n";
        }
        cout << endl;
    }

    /**
     * @brief Inverse les couleurs de l'image (effet miroir des valeurs).
     * 
     * @note Cette opération est réversible en l'appliquant deux fois.
     */
    void invertColors() {
        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width * colors; j++) {
                data[i][j] = 255.0 - data[i][j];
            }
        }
    }

    /**
     * @brief Réinitialise l'inversion des couleurs (identique à invertColors car réversible).
     */
    void resetInvertColors() {
        invertColors();
    }

    /**
     * @brief Applique un seuillage binaire (opérateur spectral non-linéaire).
     * 
     * Implémente l'opérateur de seuillage X_t(F) = {p e Omega | F(p) > t}
     * défini dans le cours sur les traitements spectraux. Calcule d'abord la 
     * luminance Y = 0.299R + 0.587G + 0.114B (Rec. 601), puis applique la fonction 
     * de seuillage F : V -> {0,255} indépendamment de l'organisation spatiale.
     * 
     * @param threshold Seuil t e [0,255] pour la binarisation
     * @note Opérateur spectral pur : F agit sur les valeurs indépendamment du voisinage
     * @see CM02 famille "traitements uniquement spectraux", exercice 1 du TD
     */
    void binaryzation(double threshold) {
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                const int base = x * colors;
                const double r = data[y][base + 0];
                const double g = (colors > 1) ? data[y][base + 1] : r;
                const double b = (colors > 2) ? data[y][base + 2] : r;
                const double gray = 0.299 * r + 0.587 * g + 0.114 * b;
                const double v = (gray > threshold) ? 255.0 : 0.0;

                data[y][base + 0] = v;
                if (colors > 1) data[y][base + 1] = v;
                if (colors > 2) data[y][base + 2] = v;
            }
        }
    }

    /**
     * @brief Restaure l'image à son état avant binarisation.
     */
    void resetBinaryzation() {
        restoreOriginal();
    }

    /**
     * @brief Applique l'opérateur négatif (transformation affine spectrale).
     * 
     * Implémente l'opérateur affine I'(x) = 255 - I(x), appartenant à la famille
     * des traitements spectraux linéaires du cours. Cet opérateur est réversible
     * (involution) et préserve la topologie de l'image.
     * 
     * @note Opérateur linéaire spectral : H(lambdaX) = lambdaH(X) et H(X+Y) = H(X)+H(Y)
     * @see CM02 famille "traitements uniquement spectraux", CM04 applications linéaires
     */
    void negatif() {
        invertColors();
    }

    /**
     * @brief Quantification uniforme (modification d'intensité non-linéaire).
     * 
     * Réduit l'espace des valeurs V = [0,255] vers un sous-ensemble discret
     * de n niveaux par quantification uniforme. Opérateur non-linéaire car
     * H(lambdaX) != lambdaH(X) (fonction en escalier). Utilise un pas uniforme s = 256/n
     * et affecte chaque pixel au niveau représentatif de son intervalle.
     * 
     * @param n Nombre de niveaux souhaités e [2,256]
     * @throws std::runtime_error Si n hors de la plage valide
     * @see CM05 "modification d'intensité non-linéaire", exercice 3 du TD
     */
    void quantification(int n) {
        if (n <= 1 || n > 256) {
            throw std::runtime_error("n entre 2 et 256");
        }
        
        const double step = 256.0 / n;
        
        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width * colors; j++) {
                double niveau = data[i][j] / step;
                int indiceNiveau = static_cast<int>(niveau);
                if (indiceNiveau < 0) indiceNiveau = 0;
                if (indiceNiveau >= n) indiceNiveau = n - 1;
                double repr = indiceNiveau * step + step / 2.0;
                data[i][j] = clamp(repr, 0.0, 255.0);
            }
        }
    }


    /**
     * @brief Rehaussement de contraste (opérateur affine spectral).
     * 
     * Applique la transformation affine I'(x) = alpha*I(x) + beta, où alpha contrôle le gain
     * et beta l'offset. Opérateur linéaire spectral : agit indépendamment de la
     * géométrie spatiale. L'écrêtage final dans [0,255] préserve la dynamique 8 bits.
     * 
     * @param alpha Gain multiplicatif (alpha > 1 augmente le contraste)
     * @param beta Offset additif (beta > 0 éclaircit l'image)
     * @note Opérateur de la forme H*X où H est une matrice diagonale
     * @see CM04 applications linéaires, CM02 traitements spectraux
     */
    void rehaussement(double alpha, double beta) {
        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width * colors; j++) {
                double nouvelleValeur = alpha * data[i][j] + beta;
                data[i][j] = clamp(nouvelleValeur, 0.0, 255.0);
            }
        }
    }

    /**
     * @brief Égalisation d'histogramme (transformation non-linéaire adaptative).
     * 
     * Applique une modification d'intensité non-linéaire basée sur la fonction
     * de répartition cumulée (CDF) normalisée. L'opérateur dépend du contenu 
     * de l'image (histogramme), violant la linéarité. Redistribue les niveaux
     * pour maximiser l'utilisation de la dynamique [0,255].
     * 
     * @note Opérateur adaptatif : H dépend de X, donc H(X_1) != H(X_2) en général
     * @see CM05 "modification d'intensité non-linéaire", exercice 5 du TD
     */
    void egalisationHistogramme() {
        if (width <= 0 || height <= 0) return;
        unsigned int hist[256] = {0};
        const int N = width * height;
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                const int base = x * colors;
                const double r = data[y][base + 0];
                const double g = (colors > 1) ? data[y][base + 1] : r;
                const double b = (colors > 2) ? data[y][base + 2] : r;
                const double gray = 0.299 * r + 0.587 * g + 0.114 * b;
                const uint8_t gv = to_u8(gray);
                ++hist[gv];
            }
        }
        unsigned int cdf[256];
        unsigned int acc = 0;
        for (int i = 0; i < 256; ++i) {
            acc += hist[i];
            cdf[i] = acc;
        }
        unsigned int cdfMin = 0;
        for (int i = 0; i < 256; ++i) { if (cdf[i] != 0) { cdfMin = cdf[i]; break; } }

        uint8_t lut[256];
        const unsigned int denom = (N > 0 && N > (int)cdfMin) ? (N - cdfMin) : 1;
        for (int i = 0; i < 256; ++i) {
            if (cdf[i] <= cdfMin) {
                lut[i] = 0;
            } else {
                double val = (static_cast<double>(cdf[i] - cdfMin) * 255.0) / static_cast<double>(denom);
                lut[i] = to_u8(val);
            }
        }
        for (int y = 0; y < height; ++y) {
            for (int x = 0; x < width; ++x) {
                const int base = x * colors;
                const double r = data[y][base + 0];
                const double g = (colors > 1) ? data[y][base + 1] : r;
                const double b = (colors > 2) ? data[y][base + 2] : r;
                const double gray = 0.299 * r + 0.587 * g + 0.114 * b;
                const uint8_t gv = to_u8(gray);
                const double v = static_cast<double>(lut[gv]);
                data[y][base + 0] = v;
                if (colors > 1) data[y][base + 1] = v;
                if (colors > 2) data[y][base + 2] = v;
            }
        }
    }


    /**
     * @brief Recharge l'image depuis le buffer source (IMG) et réinitialise tout.
     * 
     * @throws std::runtime_error Si les dimensions W ou H sont invalides
     */
    void reload() {
        freeMemory(data);
        freeMemory(originalData);
        data = nullptr;
        originalData = nullptr;
        
        if (W <= 0 || H <= 0) {
            throw std::runtime_error("dimensions invalides");
        }
        
        width  = W;
        height = H;
        colors = 3;
        
        allocateMemory();
        loadImageData();
        saveOriginal();
    }
    
    /**
     * @brief Restaure l'image à son état original.
     */
    void restoreOriginal() {
        if (!originalData) {
            throw std::runtime_error("pas d'original");
        }
        
        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width * colors; j++) {
                data[i][j] = originalData[i][j];
            }
        }
    }
    
    /**
     * @brief Applique une transformation à tous les pixels de l'image.
     * 
     * @tparam Func Type de la fonction de transformation
     * @param transform Fonction prenant un double et retournant un double
     */
    template<typename Func>
    void applyPixelTransform(Func transform) {
        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width * colors; j++) {
                data[i][j] = transform(data[i][j]);
            }
        }
    }

private:
    /**
     * @brief Crée une copie temporaire des données de l'image.
     * @return double** Pointeur vers la copie temporaire
     */
    double** createTempCopy() const {
        double** temp = new double*[height];
        for (int i = 0; i < height; i++) {
            temp[i] = new double[width * colors];
            std::copy(data[i], data[i] + (width * colors), temp[i]);
        }
        return temp;
    }

    /**
     * @brief Applique une opération morphologique générique sur le treillis complet.
     * 
     * Méthode template implémentant le pattern morphologique générique :
     * - Création d'une copie temporaire (évite les effets de bord)
     * - Application de l'opérateur de comparaison sur le voisinage B
     * - L'initialisation distingue inf/sup selon l'opérateur (255->min, 0->max)
     * 
     * @tparam CompareFunc Type de fonction de comparaison (min ou max)
     * @param kernelSize Rayon de l'élément structurant carré
     * @param initValue Élément neutre du treillis (top pour inf, bot pour sup)
     * @param compare Fonction de comparaison définissant l'opérateur
     * @see CM05 treillis complet, supremum/infimum, élément structurant
     */
    template<typename CompareFunc>
    void applyMorphologicalOp(int kernelSize, double initValue, CompareFunc compare) {
        if (kernelSize < 1 || kernelSize % 2 == 0) {
            throw std::runtime_error("taille noyau impair");
        }

        const int radius = kernelSize / 2;
        double** temp = createTempCopy();

        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                for (int c = 0; c < colors; c++) {
                    double resultVal = initValue;
                    
                    for (int dy = -radius; dy <= radius; dy++) {
                        for (int dx = -radius; dx <= radius; dx++) {
                            int ny = y + dy;
                            int nx = x + dx;
                            
                            if (ny >= 0 && ny < height && nx >= 0 && nx < width) {
                                double val = temp[ny][nx * colors + c];
                                resultVal = compare(resultVal, val);
                            }
                        }
                    }
                    
                    data[y][x * colors + c] = resultVal;
                }
            }
        }

        freeMemory(temp);
    }

public:
    /**
     * @brief Érosion morphologique (opérateur de rang, infimum local).
     * 
     * Implémente l'érosion dans le cadre algébrique de la morphologie mathématique :
     * (F ominus B)(x) = inf{F(x+b) | b e B} où B est l'élément structurant carré.
     * Opérateur non-linéaire commutant avec l'infimum sur le treillis (F^E, <=).
     * Réduit les objets blancs dans une image binaire.
     * 
     * @param kernelSize Taille de l'élément structurant B (carré de côté k)
     * @note Érosion duale de la dilatation dans l'adjonction (epsilon,delta)
     * @see CM05 morphologie algébrique, adjonction érosion-dilatation
     */
    void erosion(int kernelSize = 3) {
        applyMorphologicalOp(kernelSize, 255.0, [](double a, double b) { 
            return (b < a) ? b : a; 
        });
    }

    /**
     * @brief Dilatation morphologique (opérateur de rang, supremum local).
     * 
     * Implémente la dilatation : (F oplus B)(x) = sup{F(x-b) | b e B}.
     * Opérateur non-linéaire commutant avec le supremum. Élargit les objets
     * blancs dans le treillis complet (2^Omega, subseteq) pour les images binaires.
     * Duale de l'érosion par l'adjonction fondamentale.
     * 
     * @param kernelSize Taille de l'élément structurant B (carré de côté k)
     * @note Filtre de rang max sur la "fenêtre d'observation" B
     * @see CM05 morphologie algébrique, somme de Minkowski X oplus B
     */
    void dilatation(int kernelSize = 3) {
        applyMorphologicalOp(kernelSize, 0.0, [](double a, double b) { 
            return (b > a) ? b : a; 
        });
    }

    /**
     * @brief Ouverture morphologique gamma = delta circ epsilon (érosion puis dilatation).
     * 
     * Composition d'opérateurs : gamma = delta*epsilon dans l'algèbre des opérateurs morphologiques.
     * Propriétés : anti-extensive (gamma(X) subseteq X), idempotente (gamma*gamma = gamma), croissante.
     * Supprime les petites structures tout en préservant la forme globale.
     * 
     * @param kernelSize Taille commune de l'élément structurant
     * @note gamma(X) subseteq X (anti-extensivité), filtre passe-bas morphologique
     * @see CM05 ouverture gamma = delta*epsilon, propriétés algébriques des opérateurs
     */
    void ouverture(int kernelSize = 3) {
        erosion(kernelSize);
        dilatation(kernelSize);
    }

    /**
     * @brief Fermeture morphologique phi = epsilon circ delta (dilatation puis érosion).
     * 
     * Composition duale : phi = epsilon*delta. Propriétés : extensive (X subseteq phi(X)), idempotente,
     * croissante. Comble les petits trous et relie les objets proches.
     * Filtre morphologique préservant les grandes structures.
     * 
     * @param kernelSize Taille commune de l'élément structurant
     * @note X subseteq phi(X) (extensivité), duale de l'ouverture par adjonction
     * @see CM05 fermeture phi = epsilon*delta, dualité ouverture-fermeture
     */
    void fermeture(int kernelSize = 3) {
        dilatation(kernelSize);
        erosion(kernelSize);
    }

};

Img* Img::instance = nullptr;

/**
 * @brief Point d'entree de l'application de traitement d'image.
 *
 * Boucle principale:
 *  - Affiche le menu (afficherMenu)
 *  - Lit le choix utilisateur
 *  - Applique l'operation correspondante sur l'image
 *  - Affiche un apercu apres chaque operation
 *
 * Gestion des erreurs:
 *  - Verifie les saisies avec readInt/readDouble
 *  - Capture les exceptions standards et libere proprement l'instance Img
 *
 * @return int Code de retour du processus (0 si succes, 1 si erreur)
 */
int main() {
    try {
        Img& img = Img::getInstance(0, 0, 0);
        int choice;
        
        do {
            choice = afficherMenu();
            
            switch (choice) {
                case 1:
                    img.printPreview();
                    break;
                    
                case 2: {
                    double threshold;
                    if (!readDouble("seuil (0-255): ", threshold)) break;
                    
                    if (threshold < 0 || threshold > 255) {
                        cout << "valeur invalide" << endl;
                        break;
                    }
                    
                    img.binaryzation(threshold);
                    img.printPreview();
                    break;
                }

                case 3:
                    img.negatif();
                    img.printPreview();
                    break;

                case 4: {
                    int n;
                    if (!readInt("niveaux (2-256): ", n)) break;
                    
                    try {
                        img.quantification(n);
                        img.printPreview();
                    } catch (const std::runtime_error& e) {
                        cout << "erreur" << endl;
                    }
                    break;
                }

                case 5: {
                    double alpha, beta;
                    if (!readDouble("alpha: ", alpha)) break;
                    if (!readDouble("beta: ", beta)) break;
                    
                    img.rehaussement(alpha, beta);
                    img.printPreview();
                    break;
                }

                case 13: {
                    img.egalisationHistogramme();
                    img.printPreview();
                    break;
                }

                case 6: {
                    int y0, y1, x0, x1, step, channel;
                    if (!readInt("y0: ", y0)) break;
                    if (!readInt("y1: ", y1)) break;
                    if (!readInt("x0: ", x0)) break;
                    if (!readInt("x1: ", x1)) break;
                    if (!readInt("step: ", step)) break;
                    if (!readInt("channel: ", channel)) break;
                    
                    img.printROI(y0, y1, x0, x1, step, channel);
                    break;
                }
                
                case 7:
                    try {
                        img.restoreOriginal();
                        img.printPreview();
                    } catch (const std::runtime_error& e) {
                        cout << "echec restauration" << endl;
                    }
                    break;

                case 8:
                    try {
                        img.reload();
                        img.printPreview();
                        cout << "image rechargee" << endl;
                    } catch (const std::runtime_error& e) {
                        cout << "echec rechargement" << endl;
                    }
                    break;

                case 9:
                    cout << "info: erosion fonctionne mieux sur image binaire" << endl;
                    cout << "conseil: binariser d'abord (option 2)" << endl;
                    applyMorphologicalOperation(img, 
                        [&img](int k) { img.erosion(k); }, 
                        "erosion");
                    break;

                case 10:
                    cout << "info: dilatation fonctionne mieux sur image binaire" << endl;
                    cout << "conseil: binariser d'abord (option 2)" << endl;
                    applyMorphologicalOperation(img, 
                        [&img](int k) { img.dilatation(k); }, 
                        "dilatation");
                    break;

                case 11:
                    applyMorphologicalOperation(img, 
                        [&img](int k) { img.ouverture(k); }, 
                        "ouverture");
                    break;

                case 12:
                    applyMorphologicalOperation(img, 
                        [&img](int k) { img.fermeture(k); }, 
                        "fermeture");
                    break;
                    
                case 0:
                    cout << "au revoir" << endl;
                    break;
                    
                default:
                    cout << "choix invalide" << endl;
                    break;
            }
        } while (choice != 0);
        
        Img::destroyInstance();
        return 0;
        
    } catch (const std::exception& e) {
        std::cerr << "erreur fatale" << endl;
        Img::destroyInstance();
        return 1;
    }
}


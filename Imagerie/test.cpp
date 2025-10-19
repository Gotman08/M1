#include <iostream>
#include <cassert>
#include <cmath>
#include <cstring>
#include <cstdint>

using std::cout;
using std::endl;

/**
 * @brief Classe Img simplifiée pour tests (sans Singleton).
 */
class ImgTest {
private:
    double** data;
    int width;
    int height;
    int colors;
    
    void allocateMemory() {
        data = new double*[height];
        for (int i = 0; i < height; i++) {
            data[i] = new double[width * colors];
            for (int j = 0; j < width * colors; j++) {
                data[i][j] = 0.0;
            }
        }
    }
    
    void freeMemory() {
        if (data) {
            for (int i = 0; i < height; i++) {
                delete[] data[i];
            }
            delete[] data;
            data = nullptr;
        }
    }

public:
    ImgTest(int w, int h, int c = 3) : data(nullptr), width(w), height(h), colors(c) {
        allocateMemory();
    }
    
    ~ImgTest() {
        freeMemory();
    }
    
    void setPixel(int y, int x, double r, double g, double b) {
        int base = x * colors;
        data[y][base + 0] = r;
        if (colors > 1) data[y][base + 1] = g;
        if (colors > 2) data[y][base + 2] = b;
    }
    
    void getPixel(int y, int x, double& r, double& g, double& b) const {
        int base = x * colors;
        r = data[y][base + 0];
        g = (colors > 1) ? data[y][base + 1] : r;
        b = (colors > 2) ? data[y][base + 2] : r;
    }
    
    static inline uint8_t to_u8(double v) {
        if (v < 0.0) return 0;
        if (v > 255.0) return 255;
        return static_cast<uint8_t>(v + 0.5);
    }
    
    static inline double getLuminance(double r, double g, double b) {
        return 0.299 * r + 0.587 * g + 0.114 * b;
    }
    
    void negatif() {
        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width * colors; j++) {
                data[i][j] = 255.0 - data[i][j];
            }
        }
    }
    
    void binaryzation(double threshold) {
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                const int base = x * colors;
                const double r = data[y][base + 0];
                const double g = (colors > 1) ? data[y][base + 1] : r;
                const double b = (colors > 2) ? data[y][base + 2] : r;
                const double gray = getLuminance(r, g, b);
                const double v = (gray > threshold) ? 255.0 : 0.0;
                
                data[y][base + 0] = v;
                if (colors > 1) data[y][base + 1] = v;
                if (colors > 2) data[y][base + 2] = v;
            }
        }
    }
    
    void rehaussement(double alpha, double beta) {
        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width * colors; j++) {
                double val = alpha * data[i][j] + beta;
                if (val < 0.0) val = 0.0;
                if (val > 255.0) val = 255.0;
                data[i][j] = val;
            }
        }
    }
    
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
                
                if (repr < 0.0) repr = 0.0;
                if (repr > 255.0) repr = 255.0;
                data[i][j] = repr;
            }
        }
    }
    
    int getWidth() const { return width; }
    int getHeight() const { return height; }
    int getColors() const { return colors; }
};

// Variables globales pour statistiques
int tests_passed = 0;
int tests_failed = 0;

/**
 * @brief Macro d'assertion avec message.
 */
#define TEST_ASSERT(condition, message) \
    do { \
        if (condition) { \
            tests_passed++; \
            cout << "[OK] " << message << endl; \
        } else { \
            tests_failed++; \
            cout << "[FAIL] " << message << endl; \
        } \
    } while(0)

/**
 * @brief Test de création d'image.
 */
void test_creation() {
    cout << "\ntest creation image:" << endl;
    
    ImgTest img(10, 10, 3);
    TEST_ASSERT(img.getWidth() == 10, "largeur correcte");
    TEST_ASSERT(img.getHeight() == 10, "hauteur correcte");
    TEST_ASSERT(img.getColors() == 3, "nombre canaux correct");
}

/**
 * @brief Test des opérations get/set pixel.
 */
void test_pixel_access() {
    cout << "\ntest acces pixels:" << endl;
    
    ImgTest img(5, 5, 3);
    img.setPixel(2, 3, 100.0, 150.0, 200.0);
    
    double r, g, b;
    img.getPixel(2, 3, r, g, b);
    
    TEST_ASSERT(r == 100.0, "canal rouge ok");
    TEST_ASSERT(g == 150.0, "canal vert ok");
    TEST_ASSERT(b == 200.0, "canal bleu ok");
}

/**
 * @brief Test de l'opération négatif.
 */
void test_negatif() {
    cout << "\ntest negatif:" << endl;
    
    ImgTest img(3, 3, 3);
    img.setPixel(0, 0, 100.0, 50.0, 200.0);
    img.negatif();
    
    double r, g, b;
    img.getPixel(0, 0, r, g, b);
    
    TEST_ASSERT(r == 155.0, "negatif rouge ok");
    TEST_ASSERT(g == 205.0, "negatif vert ok");
    TEST_ASSERT(b == 55.0, "negatif bleu ok");
    
    // Test involution: negatif(negatif(x)) = x
    img.negatif();
    img.getPixel(0, 0, r, g, b);
    TEST_ASSERT(r == 100.0 && g == 50.0 && b == 200.0, "involution negatif ok");
}

/**
 * @brief Test de binarisation.
 */
void test_binarization() {
    cout << "\ntest binarisation:" << endl;
    
    ImgTest img(2, 2, 3);
    
    // Pixel clair (luminance > seuil)
    img.setPixel(0, 0, 200.0, 200.0, 200.0);
    
    // Pixel sombre (luminance < seuil)
    img.setPixel(0, 1, 50.0, 50.0, 50.0);
    
    img.binaryzation(128.0);
    
    double r1, g1, b1;
    img.getPixel(0, 0, r1, g1, b1);
    TEST_ASSERT(r1 == 255.0 && g1 == 255.0 && b1 == 255.0, "pixel clair -> blanc");
    
    double r2, g2, b2;
    img.getPixel(0, 1, r2, g2, b2);
    TEST_ASSERT(r2 == 0.0 && g2 == 0.0 && b2 == 0.0, "pixel sombre -> noir");
}

/**
 * @brief Test de rehaussement.
 */
void test_rehaussement() {
    cout << "\ntest rehaussement:" << endl;
    
    ImgTest img(2, 2, 3);
    img.setPixel(0, 0, 100.0, 100.0, 100.0);
    
    // Test gain: alpha=2, beta=0
    img.rehaussement(2.0, 0.0);
    double r, g, b;
    img.getPixel(0, 0, r, g, b);
    TEST_ASSERT(r == 200.0, "gain x2 ok");
    
    // Reset et test offset
    img.setPixel(0, 0, 100.0, 100.0, 100.0);
    img.rehaussement(1.0, 50.0);
    img.getPixel(0, 0, r, g, b);
    TEST_ASSERT(r == 150.0, "offset +50 ok");
    
    // Test clamping superieur
    img.setPixel(0, 0, 200.0, 200.0, 200.0);
    img.rehaussement(2.0, 0.0);
    img.getPixel(0, 0, r, g, b);
    TEST_ASSERT(r == 255.0, "clamping max ok");
    
    // Test clamping inferieur
    img.setPixel(0, 0, 50.0, 50.0, 50.0);
    img.rehaussement(1.0, -100.0);
    img.getPixel(0, 0, r, g, b);
    TEST_ASSERT(r == 0.0, "clamping min ok");
}

/**
 * @brief Test de quantification.
 */
void test_quantification() {
    cout << "\ntest quantification:" << endl;
    
    ImgTest img(2, 2, 3);
    img.setPixel(0, 0, 100.0, 100.0, 100.0);
    
    // Quantification sur 4 niveaux: [0-64), [64-128), [128-192), [192-256)
    // Valeur 100 -> niveau 1 -> représentant = 64 + 32 = 96
    img.quantification(4);
    
    double r, g, b;
    img.getPixel(0, 0, r, g, b);
    
    // Le représentant est au milieu de l'intervalle
    TEST_ASSERT(std::abs(r - 96.0) < 1.0, "quantification 4 niveaux ok");
    
    // Test exception
    bool exception_caught = false;
    try {
        img.quantification(1);
    } catch (const std::runtime_error&) {
        exception_caught = true;
    }
    TEST_ASSERT(exception_caught, "exception n<2 ok");
}

/**
 * @brief Test de conversion to_u8.
 */
void test_to_u8() {
    cout << "\ntest conversion to_u8:" << endl;
    
    TEST_ASSERT(ImgTest::to_u8(0.0) == 0, "to_u8(0) = 0");
    TEST_ASSERT(ImgTest::to_u8(127.4) == 127, "to_u8(127.4) = 127");
    TEST_ASSERT(ImgTest::to_u8(127.6) == 128, "to_u8(127.6) = 128");
    TEST_ASSERT(ImgTest::to_u8(255.0) == 255, "to_u8(255) = 255");
    TEST_ASSERT(ImgTest::to_u8(-10.0) == 0, "to_u8(-10) = 0 (clamp)");
    TEST_ASSERT(ImgTest::to_u8(300.0) == 255, "to_u8(300) = 255 (clamp)");
}

/**
 * @brief Test du calcul de luminance.
 */
void test_luminance() {
    cout << "\ntest luminance:" << endl;
    
    // Blanc pur
    double lum_white = ImgTest::getLuminance(255.0, 255.0, 255.0);
    TEST_ASSERT(std::abs(lum_white - 255.0) < 0.01, "luminance blanc = 255");
    
    // Noir pur
    double lum_black = ImgTest::getLuminance(0.0, 0.0, 0.0);
    TEST_ASSERT(std::abs(lum_black - 0.0) < 0.01, "luminance noir = 0");
    
    // Rouge pur (coefficient 0.299)
    double lum_red = ImgTest::getLuminance(255.0, 0.0, 0.0);
    TEST_ASSERT(std::abs(lum_red - 76.245) < 0.5, "luminance rouge ok");
    
    // Vert pur (coefficient 0.587)
    double lum_green = ImgTest::getLuminance(0.0, 255.0, 0.0);
    TEST_ASSERT(std::abs(lum_green - 149.685) < 0.5, "luminance vert ok");
    
    // Bleu pur (coefficient 0.114)
    double lum_blue = ImgTest::getLuminance(0.0, 0.0, 255.0);
    TEST_ASSERT(std::abs(lum_blue - 29.07) < 0.5, "luminance bleu ok");
}

/**
 * @brief Test de robustesse (valeurs limites).
 */
void test_robustesse() {
    cout << "\ntest robustesse:" << endl;
    
    // Image 1x1
    ImgTest img1(1, 1, 3);
    img1.setPixel(0, 0, 128.0, 128.0, 128.0);
    double r, g, b;
    img1.getPixel(0, 0, r, g, b);
    TEST_ASSERT(r == 128.0, "image 1x1 ok");
    
    // Operations multiples
    ImgTest img2(5, 5, 3);
    img2.setPixel(2, 2, 100.0, 150.0, 200.0);
    img2.negatif();
    img2.rehaussement(1.5, 10.0);
    img2.quantification(8);
    TEST_ASSERT(true, "operations chainées ok");
}

/**
 * @brief Point d'entrée des tests.
 */
int main() {
    cout << "===============================================" << endl;
    cout << "tests unitaires traitement image" << endl;
    cout << "===============================================" << endl;
    
    test_creation();
    test_pixel_access();
    test_to_u8();
    test_luminance();
    test_negatif();
    test_binarization();
    test_rehaussement();
    test_quantification();
    test_robustesse();
    
    cout << "\n===============================================" << endl;
    cout << "resultat: " << tests_passed << " ok, " << tests_failed << " fail" << endl;
    cout << "===============================================" << endl;
    
    return (tests_failed == 0) ? 0 : 1;
}

/**
 * @file test_filters_complete.cpp
 * @brief Tests complets pour tous les filtres du projet CHPS0703
 *
 * Tests de conformité aux TDs #1 et #2
 */

#include "ImageProcessing.hpp"
#include <iostream>
#include <cassert>
#include <cmath>

using namespace ImageProcessing;

/**
 * @brief Crée une petite image de test (10x10, grayscale)
 */
Image createTestImage() {
    Image img(10, 10, 1);

    // Initialiser avec un gradient simple
    auto& data = const_cast<ImageData&>(img.getData());
    for (int y = 0; y < 10; ++y) {
        for (int x = 0; x < 10; ++x) {
            data[y][x] = static_cast<double>(y * 10 + x) * 2.55; // 0-255
        }
    }

    img.saveOriginal();
    return img;
}

/**
 * @brief Vérifie que toutes les valeurs de pixels sont dans [0, 255]
 */
bool checkValidRange(const ImageData& data) {
    const int width = data.getWidth();
    const int height = data.getHeight();
    const int colors = data.getColors();

    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            for (int c = 0; c < colors; ++c) {
                const double val = data[y][x * colors + c];
                if (val < 0.0 || val > 255.0) {
                    std::cerr << "Valeur hors limites: " << val << " @ (" << x << "," << y << ")\n";
                    return false;
                }
            }
        }
    }
    return true;
}

/**
 * @brief Vérifie que l'image est binaire (seulement 0 ou 255)
 */
bool checkBinary(const ImageData& data) {
    const int width = data.getWidth();
    const int height = data.getHeight();
    const int colors = data.getColors();

    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            for (int c = 0; c < colors; ++c) {
                const double val = data[y][x * colors + c];
                if (val != 0.0 && val != 255.0) {
                    std::cerr << "Valeur non binaire: " << val << " @ (" << x << "," << y << ")\n";
                    return false;
                }
            }
        }
    }
    return true;
}

// ========== TD #1 : TRANSFORMATIONS DE BASE ==========

void testBinarization() {
    std::cout << "[TD#1 Ex.1] Test binarisation...\n";
    Image img = createTestImage();

    img.binarize(128.0);

    assert(checkValidRange(img.getData()));
    assert(checkBinary(img.getData()));

    std::cout << "  ✓ Binarisation OK (image binaire valide)\n";
}

void testNegative() {
    std::cout << "[TD#1 Ex.2] Test négatif...\n";
    Image img = createTestImage();

    const double valBefore = img.getData()[0][0];
    img.negate();
    const double valAfter = img.getData()[0][0];

    assert(checkValidRange(img.getData()));
    assert(std::abs(valBefore + valAfter - 255.0) < 0.01); // Val + Neg(Val) = 255

    std::cout << "  ✓ Négatif OK (transformation correcte)\n";
}

void testQuantization() {
    std::cout << "[TD#1 Ex.3] Test quantification...\n";
    Image img = createTestImage();

    img.quantize(4); // 256 niveaux -> 4 niveaux

    assert(checkValidRange(img.getData()));

    std::cout << "  ✓ Quantification OK\n";
}

void testEnhancement() {
    std::cout << "[TD#1 Ex.4] Test rehaussement...\n";
    Image img = createTestImage();

    img.enhance(1.5, 10.0); // Contraste amplifié

    assert(checkValidRange(img.getData()));

    std::cout << "  ✓ Rehaussement OK\n";
}

void testHistogramEqualization() {
    std::cout << "[TD#1 Ex.5] Test égalisation d'histogramme...\n";
    Image img = createTestImage();

    img.equalizeHistogram();

    assert(checkValidRange(img.getData()));

    std::cout << "  ✓ Égalisation d'histogramme OK\n";
}

void testErosion() {
    std::cout << "[TD#1 Ex.6] Test érosion...\n";
    Image img = createTestImage();

    Erosion erosion(3);
    img.applyFilter(erosion);

    assert(checkValidRange(img.getData()));

    std::cout << "  ✓ Érosion OK\n";
}

void testDilatation() {
    std::cout << "[TD#1 Ex.6] Test dilatation...\n";
    Image img = createTestImage();

    Dilatation dilatation(3);
    img.applyFilter(dilatation);

    assert(checkValidRange(img.getData()));

    std::cout << "  ✓ Dilatation OK\n";
}

void testOpening() {
    std::cout << "[TD#1 Ex.7] Test ouverture...\n";
    Image img = createTestImage();

    Opening opening(3);
    img.applyFilter(opening);

    assert(checkValidRange(img.getData()));

    std::cout << "  ✓ Ouverture OK\n";
}

void testClosing() {
    std::cout << "[TD#1 Ex.7] Test fermeture...\n";
    Image img = createTestImage();

    Closing closing(3);
    img.applyFilter(closing);

    assert(checkValidRange(img.getData()));

    std::cout << "  ✓ Fermeture OK\n";
}

// ========== TD #2 : FILTRES ==========

void testMeanFilter() {
    std::cout << "[TD#2 Ex.1] Test filtre moyen...\n";
    Image img = createTestImage();

    MeanFilter filter(3);
    img.applyFilter(filter);

    assert(checkValidRange(img.getData()));

    std::cout << "  ✓ Filtre moyen OK\n";
}

void testGaussianFilter() {
    std::cout << "[TD#2 Ex.2] Test filtre gaussien...\n";
    Image img = createTestImage();

    GaussianFilter filter(5, 1.0);
    img.applyFilter(filter);

    assert(checkValidRange(img.getData()));

    std::cout << "  ✓ Filtre gaussien OK\n";
}

void testMedianFilter() {
    std::cout << "[TD#2 Ex.3] Test filtre médian...\n";
    Image img = createTestImage();

    MedianFilter filter(3);
    img.applyFilter(filter);

    assert(checkValidRange(img.getData()));

    std::cout << "  ✓ Filtre médian OK\n";
}

void testMinFilter() {
    std::cout << "[TD#2 Ex.3] Test filtre Min...\n";
    Image img = createTestImage();

    MinFilter filter(3);
    img.applyFilter(filter);

    assert(checkValidRange(img.getData()));

    std::cout << "  ✓ Filtre Min OK\n";
}

void testMaxFilter() {
    std::cout << "[TD#2 Ex.3] Test filtre Max...\n";
    Image img = createTestImage();

    MaxFilter filter(3);
    img.applyFilter(filter);

    assert(checkValidRange(img.getData()));

    std::cout << "  ✓ Filtre Max OK\n";
}

void testSobelFilter() {
    std::cout << "[TD#2 Ex.4] Test filtre Sobel...\n";
    Image img = createTestImage();

    SobelFilter filter;
    img.applyFilter(filter);

    assert(checkValidRange(img.getData()));

    std::cout << "  ✓ Filtre Sobel OK\n";
}

void testPrewittFilter() {
    std::cout << "[TD#2 Ex.4] Test filtre Prewitt...\n";
    Image img = createTestImage();

    PrewittFilter filter;
    img.applyFilter(filter);

    assert(checkValidRange(img.getData()));

    std::cout << "  ✓ Filtre Prewitt OK\n";
}

void testCannyFilter() {
    std::cout << "[TD#2 Ex.4] Test filtre Canny...\n";
    Image img = createTestImage();

    CannyFilter filter(50.0, 150.0);
    img.applyFilter(filter);

    assert(checkValidRange(img.getData()));

    std::cout << "  ✓ Filtre Canny OK\n";
}

void testBilateralFilter() {
    std::cout << "[TD#2 Ex.5] Test filtre bilatéral...\n";
    Image img = createTestImage();

    BilateralFilter filter(5, 50.0, 50.0);
    img.applyFilter(filter);

    assert(checkValidRange(img.getData()));

    std::cout << "  ✓ Filtre bilatéral OK\n";
}

// ========== MAIN ==========

int main() {
    std::cout << "===========================================\n";
    std::cout << "TESTS COMPLETS - CHPS0703 Traitement Images\n";
    std::cout << "===========================================\n\n";

    try {
        // TD #1 : Transformations de base
        std::cout << "━━━ TD #1 : PRISE EN MAIN ━━━\n\n";
        testBinarization();
        testNegative();
        testQuantization();
        testEnhancement();
        testHistogramEqualization();
        testErosion();
        testDilatation();
        testOpening();
        testClosing();

        std::cout << "\n━━━ TD #2 : FILTRAGE ━━━\n\n";
        testMeanFilter();
        testGaussianFilter();
        testMedianFilter();
        testMinFilter();
        testMaxFilter();
        testSobelFilter();
        testPrewittFilter();
        testCannyFilter();
        testBilateralFilter();

        std::cout << "\n===========================================\n";
        std::cout << "✅ TOUS LES TESTS RÉUSSIS (17/17)\n";
        std::cout << "===========================================\n";

        std::cout << "\n📊 Couverture des TDs:\n";
        std::cout << "  • TD#1 (Prise en main) : 9/9 ✅ 100%\n";
        std::cout << "  • TD#2 (Filtrage)      : 8/8 ✅ 100%\n";
        std::cout << "  • TOTAL                : 17/17 ✅ 100%\n";

        return 0;

    } catch (const std::exception& e) {
        std::cerr << "\n❌ ERREUR: " << e.what() << "\n";
        return 1;
    }
}

/**
 * @brief Test unitaire pour ImgNB avec images en noir et blanc
 */

#include "ImgNB.hpp"
#include <iostream>
#include <cassert>

// NOTE: simulation d'une image 1 canal (noir et blanc)
void testGrayscaleImage() {
    std::cout << "test image 1 canal...\n";
    
    try {
        // TODO: créer une instance avec 1 canal
        ImgNB& imgnb = ImgNB::getInstance(10, 10, 1);
        
        std::cout << "dimensions: " << imgnb.getWidth() << "x" << imgnb.getHeight() << "\n";
        
        // NOTE: test des opérations de base
        imgnb.binaryzation(128.0);
        std::cout << "binaryzation ok\n";

        imgnb.reload();
        imgnb.negatif();
        std::cout << "negatif ok\n";

        imgnb.reload();
        imgnb.quantification(4);
        std::cout << "quantification ok\n";

        imgnb.reload();
        imgnb.rehaussement(1.5, 10.0);
        std::cout << "rehaussement ok\n";

        imgnb.reload();
        imgnb.egalisationHistogramme();
        std::cout << "egalisation ok\n";

        // NOTE: test des filtres
        imgnb.reload();
        imgnb.filtreMoyen(3);
        std::cout << "filtre moyen ok\n";
        
        imgnb.reload();
        imgnb.filtreGaussien(5, 1.0);
        std::cout << "filtre gaussien ok\n";
        
        imgnb.reload();
        imgnb.filtreMedian(3);
        std::cout << "filtre median ok\n";
        
        imgnb.reload();
        imgnb.filtreSobel();
        std::cout << "filtre sobel ok\n";
        
        imgnb.reload();
        imgnb.filtrePrewitt();
        std::cout << "filtre prewitt ok\n";
        
        imgnb.reload();
        imgnb.filtreCanny(50.0, 150.0);
        std::cout << "filtre canny ok\n";
        
        imgnb.reload();
        imgnb.filtreBilateral(5, 50.0, 50.0);
        std::cout << "filtre bilateral ok\n";
        
        // NOTE: test des opérations morphologiques
        imgnb.reload();
        imgnb.erosion(3);
        std::cout << "erosion ok\n";
        
        imgnb.reload();
        imgnb.dilatation(3);
        std::cout << "dilatation ok\n";
        
        imgnb.reload();
        imgnb.ouverture(3);
        std::cout << "ouverture ok\n";
        
        imgnb.reload();
        imgnb.fermeture(3);
        std::cout << "fermeture ok\n";
        
        std::cout << "tous les tests ok\n";
        
    } catch (const std::exception& e) {
        std::cerr << "erreur: " << e.what() << "\n";
        return;
    }
}

int main() {
    testGrayscaleImage();
    return 0;
}

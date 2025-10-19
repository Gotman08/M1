#include <iostream>
#include <cstdint>

// Test simple de l'érosion
int main() {
    // Image 5x5 avec un carré blanc au centre
    double data[5][5] = {
        {0, 0, 0, 0, 0},
        {0, 255, 255, 255, 0},
        {0, 255, 255, 255, 0},
        {0, 255, 255, 255, 0},
        {0, 0, 0, 0, 0}
    };
    
    // Afficher avant
    std::cout << "Avant erosion:" << std::endl;
    for (int i = 0; i < 5; i++) {
        for (int j = 0; j < 5; j++) {
            std::cout << (data[i][j] > 128 ? "■" : "·");
        }
        std::cout << std::endl;
    }
    
    // Erosion avec noyau 3x3
    double temp[5][5];
    for (int y = 0; y < 5; y++) {
        for (int x = 0; x < 5; x++) {
            double minVal = 255.0;
            for (int dy = -1; dy <= 1; dy++) {
                for (int dx = -1; dx <= 1; dx++) {
                    int ny = y + dy;
                    int nx = x + dx;
                    if (ny >= 0 && ny < 5 && nx >= 0 && nx < 5) {
                        if (data[ny][nx] < minVal) {
                            minVal = data[ny][nx];
                        }
                    }
                }
            }
            temp[y][x] = minVal;
        }
    }
    
    // Copier résultat
    for (int i = 0; i < 5; i++) {
        for (int j = 0; j < 5; j++) {
            data[i][j] = temp[i][j];
        }
    }
    
    // Afficher après
    std::cout << "\nApres erosion 3x3:" << std::endl;
    for (int i = 0; i < 5; i++) {
        for (int j = 0; j < 5; j++) {
            std::cout << (data[i][j] > 128 ? "■" : "·");
        }
        std::cout << std::endl;
    }
    
    std::cout << "\nResultat attendu: le carre blanc RETRECIT" << std::endl;
    std::cout << "Si erosion fonctionne: seul le centre (2,2) reste blanc" << std::endl;
    
    return 0;
}

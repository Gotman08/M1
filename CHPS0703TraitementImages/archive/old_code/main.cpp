#include "../include/TP1App.hpp"

int main() {
    try {
        Img& img = Img::getInstance(0, 0, 0);
        
        while (true) {
            int choice = afficherMenu();

            if (choice == 0) {
                cout << "au revoir" << endl;
                break;
            }

            bool handled = false;

            if (choice == 21) {
                handled = handleGrayscaleOperation(img, choice);
            } else if (choice > 0) {
                handled = handleRgbOperation(img, choice);
            }

            if (!handled) {
                cout << "choix invalide" << endl;
            }
        }

        Img::destroyInstance();
        return 0;
        
    } catch (const std::exception& e) {
        std::cerr << "erreur fatale" << endl;
        Img::destroyInstance();
        return 1;
    }
}

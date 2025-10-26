/**
 * @file main.cpp
 * @brief Programme principal - Système de traitement d'images (Architecture POO)
 *
 * Ce programme illustre l'utilisation de l'architecture moderne
 * de traitement d'images basée sur les principes de POO.
 */

#include "../include/ImageProcessing.hpp"
#include "../include/ui/Menu.hpp"
#include "../include/image_buffer.hpp"  // Pour IMG, W, H
#include <memory>
#include <iostream>

using namespace ImageProcessing;

/**
 * @brief Traite les opérations de base de l'image
 *
 * @param img Image à traiter
 * @param choice Choix de l'utilisateur
 * @return bool true si traité avec succès, false sinon
 */
bool handleBasicOperations(Image& img, int choice) {
    try {
        switch (choice) {
            case 1: // Afficher aperçu
                DisplayManager::printPreview(img.getData());
                return true;

            case 2: { // Binariser
                double threshold;
                if (!Menu::readDouble("Seuil (0-255): ", threshold)) return true;
                if (threshold < 0.0 || threshold > 255.0) {
                    Menu::showError("Seuil doit etre entre 0 et 255");
                    return true;
                }
                img.binarize(threshold);
                DisplayManager::printPreview(img.getData());
                Menu::showInfo("Binarisation appliquee");
                return true;
            }

            case 3: // Négatif
                img.negate();
                DisplayManager::printPreview(img.getData());
                Menu::showInfo("Negatif applique");
                return true;

            case 4: { // Quantification
                int levels;
                if (!Menu::readInt("Nombre de niveaux (2-256): ", levels)) return true;
                img.quantize(levels);
                DisplayManager::printPreview(img.getData());
                Menu::showInfo("Quantification appliquee");
                return true;
            }

            case 5: { // Rehaussement
                double alpha, beta;
                if (!Menu::readDouble("Alpha (gain): ", alpha)) return true;
                if (!Menu::readDouble("Beta (offset): ", beta)) return true;
                img.enhance(alpha, beta);
                DisplayManager::printPreview(img.getData());
                Menu::showInfo("Rehaussement applique");
                return true;
            }

            case 6: { // Afficher ROI
                int y0, y1, x0, x1, step, channel;
                if (!Menu::readInt("y0: ", y0)) return true;
                if (!Menu::readInt("y1: ", y1)) return true;
                if (!Menu::readInt("x0: ", x0)) return true;
                if (!Menu::readInt("x1: ", x1)) return true;
                if (!Menu::readInt("step: ", step)) return true;
                if (!Menu::readInt("channel (-1=RGB, 0=R, 1=G, 2=B): ", channel)) return true;
                DisplayManager::printROI(img.getData(), y0, y1, x0, x1, step, channel);
                return true;
            }

            case 7: // Restaurer original
                img.restoreOriginal();
                DisplayManager::printPreview(img.getData());
                Menu::showInfo("Image restauree");
                return true;

            case 8: // Recharger
                img.loadFromBuffer(IMG, W, H);
                DisplayManager::printPreview(img.getData());
                Menu::showInfo("Image rechargee");
                return true;

            case 13: // Égalisation histogramme
                img.equalizeHistogram();
                DisplayManager::printPreview(img.getData());
                Menu::showInfo("Egalisation appliquee");
                return true;

            case 19: // Conversion grayscale
                img.toGrayscale(ColorConversion::Method::REC601);
                DisplayManager::printPreview(img.getData());
                Menu::showInfo("Conversion grayscale appliquee");
                return true;

            default:
                return false;
        }
    } catch (const std::exception& e) {
        Menu::showError(e.what());
        return true;
    }
}

/**
 * @brief Traite les opérations morphologiques
 *
 * @param img Image à traiter
 * @param choice Choix de l'utilisateur
 * @return bool true si traité avec succès, false sinon
 */
bool handleMorphologicalOperations(Image& img, int choice) {
    try {
        int kernelSize;
        if (!Menu::readInt("Taille du noyau (impair, ex: 3, 5, 7): ", kernelSize)) {
            return true;
        }

        std::unique_ptr<ImageFilter> operation;

        switch (choice) {
            case 9:  // Érosion
                Menu::showInfo("Erosion fonctionne mieux sur images binaires");
                operation = std::make_unique<Erosion>(kernelSize);
                break;

            case 10: // Dilatation
                Menu::showInfo("Dilatation etend les regions blanches");
                operation = std::make_unique<Dilatation>(kernelSize);
                break;

            case 11: // Ouverture
                Menu::showInfo("Ouverture = Erosion + Dilatation");
                operation = std::make_unique<Opening>(kernelSize);
                break;

            case 12: // Fermeture
                Menu::showInfo("Fermeture = Dilatation + Erosion");
                operation = std::make_unique<Closing>(kernelSize);
                break;

            default:
                return false;
        }

        if (operation) {
            img.applyFilter(*operation);
            DisplayManager::printPreview(img.getData());
            Menu::showInfo("Operation morphologique appliquee");
        }

        return true;

    } catch (const std::exception& e) {
        Menu::showError(e.what());
        return true;
    }
}

/**
 * @brief Traite les filtres
 *
 * @param img Image à traiter
 * @param choice Choix de l'utilisateur
 * @return bool true si traité avec succès, false sinon
 */
bool handleFilters(Image& img, int choice) {
    try {
        std::unique_ptr<ImageFilter> filter;

        switch (choice) {
            case 14: { // Filtre moyen
                int kernelSize;
                if (!Menu::readInt("Taille du noyau (impair, ex: 3, 5): ", kernelSize)) {
                    return true;
                }
                filter = std::make_unique<MeanFilter>(kernelSize);
                break;
            }

            case 15: { // Filtre gaussien
                int kernelSize;
                double sigma;
                if (!Menu::readInt("Taille du noyau (impair, ex: 5, 7): ", kernelSize)) {
                    return true;
                }
                if (!Menu::readDouble("Sigma (ex: 1.0, 1.4, 2.0): ", sigma)) {
                    return true;
                }
                filter = std::make_unique<GaussianFilter>(kernelSize, sigma);
                Menu::showInfo("Filtre gaussien lisse tout en preservant les contours");
                break;
            }

            case 16: { // Filtre médian
                int kernelSize;
                if (!Menu::readInt("Taille du noyau (impair, ex: 3, 5): ", kernelSize)) {
                    return true;
                }
                filter = std::make_unique<MedianFilter>(kernelSize);
                Menu::showInfo("Filtre median excellent pour bruit poivre et sel");
                break;
            }

            case 17: // Filtre Sobel
                filter = std::make_unique<SobelFilter>();
                Menu::showInfo("Sobel detecte contours horizontaux et verticaux");
                break;

            case 18: // Filtre Prewitt
                filter = std::make_unique<PrewittFilter>();
                Menu::showInfo("Prewitt detecte contours avec ponderation uniforme");
                break;

            default:
                return false;
        }

        if (filter) {
            img.applyFilter(*filter);
            DisplayManager::printPreview(img.getData());
            Menu::showInfo("Filtre applique avec succes");
        }

        return true;

    } catch (const std::exception& e) {
        Menu::showError(e.what());
        return true;
    }
}

/**
 * @brief Fonction principale
 *
 * @return int Code de retour (0 = succès, 1 = erreur)
 */
int main() {
    try {
        // Chargement de l'image depuis le buffer global (image.hpp)
        Image img;
        img.loadFromBuffer(IMG, W, H);

        Menu::showInfo("Image chargee avec succes");
        DisplayManager::printInfo(img.getData());

        // Boucle principale
        while (true) {
            int choice = Menu::displayMainMenu();

            if (choice == 0) {
                Menu::showInfo("Au revoir!");
                break;
            }

            if (choice == -1) {
                Menu::showError("Choix invalide");
                continue;
            }

            // Traitement du choix
            bool handled = handleBasicOperations(img, choice);
            if (!handled) {
                handled = handleMorphologicalOperations(img, choice);
            }
            if (!handled) {
                handled = handleFilters(img, choice);
            }

            if (!handled) {
                Menu::showError("Choix invalide");
            }
        }

        return 0;

    } catch (const std::exception& e) {
        Menu::showError(std::string("Erreur fatale: ") + e.what());
        return 1;
    }
}

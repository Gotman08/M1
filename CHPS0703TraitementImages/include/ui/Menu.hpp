#pragma once

#include <iostream>
#include <limits>
#include <string>

/**
 * @file Menu.hpp
 * @brief Classe pour gérer les menus interactifs
 */
namespace ImageProcessing {

/**
 * @brief Classe pour gérer l'affichage et la saisie des menus
 *
 * Fournit des méthodes statiques pour afficher des menus formatés
 * et lire les entrées utilisateur de manière sécurisée.
 */
class Menu {
public:
    /**
     * @brief Affiche le menu principal et récupère le choix utilisateur
     *
     * @return int Choix de l'utilisateur (0-21), ou -1 en cas d'erreur
     *
     * @example
     * int choice = Menu::displayMainMenu();
     * if (choice == 1) {
     *     // Traiter le choix...
     * }
     */
    static int displayMainMenu() {
        std::cout << "\n=== TRAITEMENT D'IMAGE ===" << std::endl;
        std::cout << "[1]  Afficher apercu" << std::endl;
        std::cout << "[2]  Binariser" << std::endl;
        std::cout << "[3]  Negatif" << std::endl;
        std::cout << "[4]  Quantifier" << std::endl;
        std::cout << "[5]  Rehausser contraste" << std::endl;
        std::cout << "[6]  Afficher ROI" << std::endl;
        std::cout << "[7]  Restaurer original" << std::endl;
        std::cout << "[8]  Recharger image" << std::endl;
        std::cout << "[9]  Erosion" << std::endl;
        std::cout << "[10] Dilatation" << std::endl;
        std::cout << "[11] Ouverture" << std::endl;
        std::cout << "[12] Fermeture" << std::endl;
        std::cout << "[13] Egalisation histogramme" << std::endl;
        std::cout << "[14] Filtre moyen" << std::endl;
        std::cout << "[15] Filtre gaussien" << std::endl;
        std::cout << "[16] Filtre median" << std::endl;
        std::cout << "[17] Filtre Sobel" << std::endl;
        std::cout << "[18] Filtre Prewitt" << std::endl;
        std::cout << "[19] Convertir en grayscale" << std::endl;
        std::cout << "[0]  Quitter" << std::endl;
        std::cout << "Choix: ";

        int choice;
        std::cin >> choice;

        // Validation de l'entrée
        if (std::cin.fail()) {
            clearInputError();
            std::cout << "[ERREUR] Entree invalide" << std::endl;
            return -1;
        }

        // Validation des bornes [0-19]
        if (choice < 0 || choice > 19) {
            std::cout << "[ERREUR] Choix invalide. Veuillez entrer un nombre entre 0 et 19" << std::endl;
            return -1;
        }

        return choice;
    }

    /**
     * @brief Lit un entier avec validation
     *
     * @param prompt Message d'invite
     * @param value Référence vers la variable recevant la valeur
     * @return bool true si succès, false si erreur
     *
     * @example
     * int kernelSize;
     * if (Menu::readInt("Taille du noyau: ", kernelSize)) {
     *     // Utiliser kernelSize...
     * }
     */
    static bool readInt(const std::string& prompt, int& value) {
        std::cout << prompt;
        std::cin >> value;

        if (std::cin.fail()) {
            clearInputError();
            std::cout << "Valeur invalide" << std::endl;
            return false;
        }

        return true;
    }

    /**
     * @brief Lit un nombre à virgule flottante avec validation
     *
     * @param prompt Message d'invite
     * @param value Référence vers la variable recevant la valeur
     * @return bool true si succès, false si erreur
     *
     * @example
     * double threshold;
     * if (Menu::readDouble("Seuil: ", threshold)) {
     *     // Utiliser threshold...
     * }
     */
    static bool readDouble(const std::string& prompt, double& value) {
        std::cout << prompt;
        std::cin >> value;

        if (std::cin.fail()) {
            clearInputError();
            std::cout << "Valeur invalide" << std::endl;
            return false;
        }

        return true;
    }

    /**
     * @brief Affiche un message d'erreur formaté
     *
     * @param message Message d'erreur à afficher
     *
     * @example
     * Menu::showError("Dimensions invalides");
     */
    static void showError(const std::string& message) {
        std::cerr << "[ERREUR] " << message << std::endl;
    }

    /**
     * @brief Affiche un message d'information formaté
     *
     * @param message Message d'information à afficher
     *
     * @example
     * Menu::showInfo("Filtre applique avec succes");
     */
    static void showInfo(const std::string& message) {
        std::cout << "[INFO] " << message << std::endl;
    }

    /**
     * @brief Demande confirmation à l'utilisateur (o/n)
     *
     * @param prompt Message de confirmation
     * @return bool true si 'o' ou 'O', false sinon
     *
     * @example
     * if (Menu::confirm("Voulez-vous continuer?")) {
     *     // Continuer...
     * }
     */
    static bool confirm(const std::string& prompt) {
        std::cout << prompt << " (o/n): ";
        char response;
        std::cin >> response;

        if (std::cin.fail()) {
            clearInputError();
            return false;
        }

        return (response == 'o' || response == 'O');
    }

private:
    /**
     * @brief Nettoie l'état d'erreur du flux d'entrée
     *
     * Appelé automatiquement après une erreur de saisie.
     */
    static void clearInputError() {
        std::cin.clear();
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    }

    // Constructeur privé pour empêcher l'instanciation
    Menu() = delete;
    ~Menu() = delete;
    Menu(const Menu&) = delete;
    Menu& operator=(const Menu&) = delete;
};

} // namespace ImageProcessing

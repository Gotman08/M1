#pragma once
#include <iostream>
#include <limits>


/**
 * @brief Affiche le menu principal de l'application de traitement d'image et récupère le choix de l'utilisateur.
 * 
 * Cette fonction affiche un menu formaté avec différentes options de traitement d'image disponibles
 * et demande à l'utilisateur de saisir son choix. Le menu présente les options suivantes :
 * - Affichage d'image
 * - Binarisation
 * - Négatif
 * - Quantification
 * - Rehaussement
 * - Affichage de région d'intérêt (ROI)
 * - Restauration
 * - Érosion
 * - Dilatation
 * - Ouverture morphologique
 * - Fermeture morphologique
 * - Quitter l'application
 * 
 * @return int Le choix de l'utilisateur (0-11), ou -1 en cas d'entrée invalide
 * 
 * @note En cas d'erreur de saisie (entrée non numérique), la fonction nettoie le buffer
 *       d'entrée et retourne -1
 */
inline int afficherMenu() {
    std::cout << "\ntraitement image" << std::endl;
    std::cout << "[1]  afficher" << std::endl;
    std::cout << "[2]  binariser" << std::endl;
    std::cout << "[3]  negatif" << std::endl;
    std::cout << "[4]  quantifier" << std::endl;
    std::cout << "[5]  rehausser" << std::endl;
    std::cout << "[6]  afficher roi" << std::endl;
    std::cout << "[7]  restaurer" << std::endl;
    std::cout << "[8]  recharger" << std::endl;
    std::cout << "[9]  erosion" << std::endl;
    std::cout << "[10] dilatation" << std::endl;
    std::cout << "[11] ouverture" << std::endl;
    std::cout << "[12] fermeture" << std::endl;
    std::cout << "[13] egalisation histo" << std::endl;
    std::cout << "[14] filtre moyen" << std::endl;
    std::cout << "[15] filtre gaussien" << std::endl;
    std::cout << "[16] filtre median" << std::endl;
    std::cout << "[17] filtre sobel" << std::endl;
    std::cout << "[18] filtre prewitt" << std::endl;
    std::cout << "[19] filtre canny" << std::endl;
    std::cout << "[20] filtre bilateral" << std::endl;
    std::cout << "[0]  quitter" << std::endl;
    std::cout << "choix: ";

    int choice;
    std::cin >> choice;

    if (std::cin.fail()) {
        std::cin.clear();
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
        return -1;
    }

    return choice;
}


/**
 * @brief Gère les erreurs de saisie sur le flux d'entrée standard.
 * 
 * Cette fonction vérifie si le dernier flux d'entrée a échoué. Si c'est le cas,
 * elle efface le drapeau d'erreur, vide le tampon d'entrée et affiche un message
 * d'erreur à l'utilisateur.
 * 
 * @return true si une erreur de saisie a été détectée et traitée, false sinon.
 */
inline bool handleInputError() {
    if (std::cin.fail()) {
        std::cin.clear();
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
        std::cout << "valeur invalide" << std::endl;
        return true;
    }
    return false;
}

/**
 * @brief Lit un entier depuis l'entrée standard avec un message d'invite.
 * 
 * Cette fonction affiche un message d'invite à l'utilisateur, lit une valeur entière
 * depuis l'entrée standard (std::cin) et la stocke dans la variable fournie.
 * 
 * @param prompt Message d'invite à afficher avant la saisie
 * @param value Référence vers la variable qui recevra la valeur entière saisie
 * @return true si la lecture s'est effectuée correctement, false en cas d'erreur de saisie
 * 
 * @note La fonction utilise handleInputError() pour détecter et gérer les erreurs de saisie
 */
inline bool readInt(const char* prompt, int& value) {
    std::cout << prompt;
    std::cin >> value;
    return !handleInputError();
}


/**
 * @brief Lit une valeur de type double depuis l'entrée standard.
 * 
 * Cette fonction affiche une invite à l'utilisateur, lit une valeur double
 * depuis std::cin et gère les erreurs de saisie via handleInputError().
 * 
 * @param prompt Le message d'invite à afficher à l'utilisateur
 * @param value Référence vers la variable où stocker la valeur lue
 * @return true si la lecture s'est déroulée sans erreur, false sinon
 */
inline bool readDouble(const char* prompt, double& value) {
    std::cout << prompt;
    std::cin >> value;
    return !handleInputError();
}

#pragma once
#include <iostream>
#include <stdexcept>
#include "menu.hpp"

/**
 * @brief Applique une opération morphologique sur une image avec un noyau de taille spécifiée.
 * 
 * Cette fonction template permet d'appliquer différentes opérations morphologiques
 * (érosion, dilatation, ouverture, fermeture, etc.) sur une image en demandant
 * à l'utilisateur de saisir la taille du noyau structurant.
 * 
 * @tparam ImgType Type de l'image sur laquelle l'opération est appliquée
 * @tparam OpFunc Type de la fonction d'opération morphologique (functor ou lambda)
 * 
 * @param img Référence vers l'image sur laquelle appliquer l'opération
 * @param operation Fonction/functor qui prend en paramètre la taille du noyau
 *                  et effectue l'opération morphologique sur l'image
 * @param opName Nom de l'opération (utilisé pour l'affichage des messages d'erreur)
 * 
 * @note La taille du noyau doit être un nombre impair
 * @note En cas d'erreur de lecture ou d'exécution, un message d'erreur est affiché
 * @note Après l'opération, un aperçu de l'image est affiché via printPreview()
 * 
 * @throws Aucune exception n'est propagée - les std::runtime_error sont capturées
 *         et un message d'erreur est affiché
 */
template<typename ImgType, typename OpFunc>
inline void applyMorphologicalOperation(ImgType& img, OpFunc operation, const char* opName) {
    int kernelSize;
    if (!readInt("taille noyau (impair): ", kernelSize)) return;

    try {
        operation(kernelSize);
        img.printPreview();
    } catch (const std::runtime_error&) {
        std::cout << "erreur " << opName << std::endl;
    }
}

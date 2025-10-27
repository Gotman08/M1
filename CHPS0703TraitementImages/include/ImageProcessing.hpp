#pragma once

/**
 * @file ImageProcessing.hpp
 * @brief En-tête principal regroupant toutes les classes de traitement d'image
 *
 * Incluez ce fichier unique pour accéder à toutes les fonctionnalités :
 * - Classes de base (Image, ImageData, ImageFilter)
 * - Utilitaires (ImageUtils, ColorConversion)
 * - Filtres (GaussianFilter, SobelFilter, MedianFilter, etc.)
 * - Opérations morphologiques (Erosion, Dilatation, Opening, Closing)
 * - Affichage (DisplayManager)
 *
 * @example
 * #include "ImageProcessing.hpp"
 * using namespace ImageProcessing;
 *
 * Image img(640, 480, 3);
 * GaussianFilter gauss(5, 1.4);
 * img.applyFilter(gauss);
 * DisplayManager::printPreview(img.getData());
 */

// Classes de base
#include "core/ImageData.hpp"
#include "core/ImageFilter.hpp"
#include "core/Image.hpp"

// Utilitaires
#include "utils/ImageUtils.hpp"
#include "utils/ColorConversion.hpp"

// Filtres de lissage
#include "filters/GaussianFilter.hpp"
#include "filters/MeanFilter.hpp"
#include "filters/MedianFilter.hpp"
#include "filters/BilateralFilter.hpp"

// Filtres différentiels
#include "filters/SobelFilter.hpp"
#include "filters/PrewittFilter.hpp"
#include "filters/CannyFilter.hpp"

// Filtres de rang
#include "filters/RankFilters.hpp"

// Opérations morphologiques
#include "operations/MorphologicalOperation.hpp"

// Affichage
#include "display/DisplayManager.hpp"

/**
 * @namespace ImageProcessing
 * @brief Espace de noms principal pour toutes les classes de traitement d'image
 *
 * Contient toutes les classes, fonctions et énumérations nécessaires
 * au traitement d'images selon les principes de POO en C++.
 *
 * @note Toutes les classes utilisent RAII (std::vector, smart pointers)
 * @note Pas de gestion manuelle de la mémoire (pas de new/delete)
 * @note Architecture modulaire avec séparation des responsabilités
 */

/**
 * @mainpage Documentation du Système de Traitement d'Images
 *
 * @section intro_sec Introduction
 *
 * Ce système fournit une bibliothèque complète pour le traitement d'images
 * en C++, implémentée selon les principes de la Programmation Orientée Objet.
 *
 * @section features_sec Fonctionnalités
 *
 * - **Gestion d'images** : Classe Image avec gestion automatique de la mémoire (RAII)
 * - **Filtres de lissage** : Gaussien, Moyen, Médian, Bilatéral
 * - **Filtres différentiels** : Sobel, Prewitt, Canny
 * - **Filtres de rang** : Min, Max (non-linéaires)
 * - **Morphologie** : Érosion, dilatation, ouverture, fermeture
 * - **Transformations** : Conversion grayscale, binarisation, quantification, rehaussement, égalisation
 * - **Affichage** : Prévisualisation en couleur dans le terminal
 *
 * @section arch_sec Architecture
 *
 * Le système est organisé en modules :
 * - core/ : Classes de base (Image, ImageData, ImageFilter)
 * - utils/ : Utilitaires (ImageUtils, ColorConversion)
 * - filters/ : Implémentations concrètes de filtres
 * - operations/ : Opérations morphologiques
 * - display/ : Gestion de l'affichage
 *
 * @section usage_sec Utilisation
 *
 * @code
 * #include "ImageProcessing.hpp"
 * using namespace ImageProcessing;
 *
 * // Création d'une image
 * Image img(640, 480, 3);
 *
 * // Application d'un filtre gaussien
 * GaussianFilter gauss(5, 1.4);
 * img.applyFilter(gauss);
 *
 * // Affichage
 * DisplayManager::printPreview(img.getData());
 * @endcode
 *
 * @section principles_sec Principes POO Appliqués
 *
 * - **Encapsulation** : Données privées avec accesseurs publics
 * - **Héritage** : Hiérarchie ImageFilter avec filtres concrets
 * - **Polymorphisme** : Méthodes virtuelles pour comportements spécialisés
 * - **Abstraction** : Interfaces abstraites (ImageFilter)
 * - **RAII** : Gestion automatique de la mémoire (std::vector)
 * - **Single Responsibility** : Chaque classe a une responsabilité unique
 * - **Open/Closed** : Extensible sans modification (nouveaux filtres)
 *
 * @author Système de Traitement d'Images
 * @version 2.0
 * @date 2025
 */

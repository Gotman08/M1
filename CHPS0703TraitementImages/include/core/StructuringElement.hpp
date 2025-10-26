#pragma once

#include <vector>
#include <utility>

/**
 * @file StructuringElement.hpp
 * @brief Élément structurant pour opérations morphologiques
 *
 * Implémente la discrétisation de Gauss selon le cours d'imagerie discrète:
 * Pour un objet continu X ⊂ R^n, le discrétisé de Gauss est:
 * ∆(X) = X ∩ Z^n = {p ∈ Z^n | p ∈ X}
 *
 * Pour un disque de rayon ρ:
 * Dρ = {(x,y) ∈ R² | x² + y² ≤ ρ²}     (continu)
 * ∆(Dρ) = {(x,y) ∈ Z² | x² + y² ≤ ρ²}  (discret)
 *
 * @see Cours d'imagerie discrète - Géométrie discrète
 */
namespace ImageProcessing {

/**
 * @brief Élément structurant basé sur la discrétisation de Gauss
 *
 * Représente un ensemble de positions relatives (dx, dy) définissant
 * la forme d'un élément structurant pour les opérations morphologiques.
 *
 * Contrairement aux kernels carrés classiques, cette classe permet de
 * définir des formes géométriques exactes (disques, croix, etc.) selon
 * la discrétisation de Gauss.
 *
 * @example
 * // Créer un disque discret de rayon 2.5
 * auto disk = StructuringElement::createDisk(2.5);
 *
 * // Utiliser avec une opération morphologique
 * Erosion erosion(disk);
 * erosion.apply(imageData);
 */
class StructuringElement {
private:
    std::vector<std::pair<int, int>> offsets;  ///< Positions relatives (dx, dy)
    int radius;                                 ///< Rayon de l'élément structurant

public:
    /**
     * @brief Constructeur par défaut (élément vide)
     */
    StructuringElement() : radius(0) {}

    /**
     * @brief Constructeur avec liste d'offsets
     *
     * @param positions Liste de positions relatives (dx, dy)
     * @param r Rayon de l'élément (pour information)
     */
    StructuringElement(const std::vector<std::pair<int, int>>& positions, int r)
        : offsets(positions), radius(r) {}

    /**
     * @brief Crée un disque discret selon la discrétisation de Gauss
     *
     * Implémente la formule du cours:
     * ∆(Dρ) = {(x,y) ∈ Z² | x² + y² ≤ ρ²}
     *
     * Le disque discret est l'ensemble des points entiers vérifiant
     * l'équation du disque continu, c'est-à-dire l'intersection du
     * disque continu avec la grille entière Z².
     *
     * @param rho Rayon du disque (ρ ≥ 0)
     * @return StructuringElement Disque discret de rayon ρ
     *
     * @note Pour ρ = 0: un seul point (0,0)
     * @note Pour ρ = 1: croix à 5 points
     * @note Pour ρ = √2 ≈ 1.41: croix + diagonales = 9 points
     * @note Pour ρ = 2: 13 points
     *
     * @example
     * auto disk1 = StructuringElement::createDisk(1.0);   // 5 points
     * auto disk2 = StructuringElement::createDisk(1.5);   // 9 points
     * auto disk3 = StructuringElement::createDisk(2.0);   // 13 points
     *
     * @see Cours: Notions d'imagerie discrète - Géométrie discrète
     * @see Exemple: Disques discrets, équation x² + y² ≤ ρ²
     */
    static StructuringElement createDisk(double rho) {
        std::vector<std::pair<int, int>> positions;
        const double rhoSquared = rho * rho;
        const int radiusInt = static_cast<int>(rho) + 1;  // Borne supérieure

        // Parcours de tous les points entiers dans le carré englobant
        // et sélection de ceux vérifiant x² + y² ≤ ρ²
        for (int dy = -radiusInt; dy <= radiusInt; ++dy) {
            for (int dx = -radiusInt; dx <= radiusInt; ++dx) {
                const double distSquared = dx * dx + dy * dy;

                // Condition de Gauss: appartient au disque discret si
                // le point entier est dans le disque continu
                if (distSquared <= rhoSquared) {
                    positions.push_back({dx, dy});
                }
            }
        }

        return StructuringElement(positions, radiusInt);
    }

    /**
     * @brief Crée un carré classique (pour compatibilité)
     *
     * Génère un kernel carré (2*radius+1) × (2*radius+1)
     * Tous les points du carré [-radius, radius]² sont inclus.
     *
     * @param radius Rayon du carré
     * @return StructuringElement Carré de côté (2*radius+1)
     *
     * @note Non conforme à la discrétisation de Gauss
     * @note Fourni pour compatibilité avec code existant
     */
    static StructuringElement createSquare(int radius) {
        std::vector<std::pair<int, int>> positions;

        for (int dy = -radius; dy <= radius; ++dy) {
            for (int dx = -radius; dx <= radius; ++dx) {
                positions.push_back({dx, dy});
            }
        }

        return StructuringElement(positions, radius);
    }

    /**
     * @brief Crée une croix (voisinage 4-connexe)
     *
     * Génère les 4 voisins directs + le centre:
     * {(0,0), (1,0), (-1,0), (0,1), (0,-1)}
     *
     * @return StructuringElement Croix 5 points
     */
    static StructuringElement createCross() {
        std::vector<std::pair<int, int>> positions = {
            {0, 0},   // Centre
            {1, 0},   // Droite
            {-1, 0},  // Gauche
            {0, 1},   // Bas
            {0, -1}   // Haut
        };
        return StructuringElement(positions, 1);
    }

    /**
     * @brief Obtient les positions relatives de l'élément structurant
     *
     * @return const std::vector<std::pair<int,int>>& Liste des offsets (dx, dy)
     */
    const std::vector<std::pair<int, int>>& getOffsets() const {
        return offsets;
    }

    /**
     * @brief Obtient le rayon de l'élément structurant
     *
     * @return int Rayon
     */
    int getRadius() const {
        return radius;
    }

    /**
     * @brief Obtient le nombre de pixels dans l'élément structurant
     *
     * @return int Cardinalité de l'élément
     */
    int size() const {
        return offsets.size();
    }

    /**
     * @brief Affiche l'élément structurant pour debug
     *
     * @param label Label descriptif
     *
     * @example
     * auto disk = StructuringElement::createDisk(1.5);
     * disk.print("Disque de rayon 1.5");
     * // Affiche les positions relatives et visualisation
     */
    void print(const char* label = "Element structurant") const;
};

} // namespace ImageProcessing

/**
 * Exercice 2 - Ensemble de Mandelbrot
 * Parallélisation avec OpenMP
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <omp.h>

// Taille maximale de l'image
#define MAXX 1024
#define MAXY 1024

// Variables globales pour la zone du plan
double xmin, ymin;      // point de départ
double cotex, cotey;    // largeur

// Pour l'image
int largeur, hauteur;
int iteration[MAXX][MAXY];  // les résultats

// Pour le traitement
int maxiter;            // nb max d'iterations
double pasx, pasy;      // pour obtenir les coord

/**
 * Calcule le nombre d'itérations pour un pixel
 */
void calculPoint(int px, int py) {
    double xc, yc;          // coord ds l'espace utilisateur
    double x = 0, y = 0, sx;
    double module = 0;      // pour l'arret premature
    int nbiter = 0;
    
    xc = xmin + pasx * px;
    yc = ymin + pasy * py;
    
    while (module < 2 && nbiter < maxiter) {
        sx = x;
        x = x*x - y*y + xc;
        y = 2*sx*y + yc;
        module = sqrt(x*x + y*y);
        nbiter++;
    }
    
    iteration[px][py] = nbiter;
}

/**
 * Version séquentielle (référence)
 */
void calculImage_seq() {
    int i, j;
    for (i = 0; i < hauteur; i++)
        for (j = 0; j < largeur; j++)
            calculPoint(i, j);
}

/**
 * Version 1: Boucle for parallèle (simple)
 * NOTE: ordonnancement dynamic recommandé car charge irrégulière
 */
void calculImage_for_parallel() {
    int i, j;
    
    #pragma omp parallel for private(j) schedule(dynamic)
    for (i = 0; i < hauteur; i++)
        for (j = 0; j < largeur; j++)
            calculPoint(i, j);
}

/**
 * Version 2: Région parallèle avec gestion explicite des lignes
 * NOTE: chaque thread calcule ses lignes explicitement
 */
void calculImage_region_parallel() {
    int i, j;
    int num_threads, thread_id;
    int lignes_par_thread, debut, fin;
    
    #pragma omp parallel private(i, j, thread_id, debut, fin)
    {
        thread_id = omp_get_thread_num();
        num_threads = omp_get_num_threads();
        
        lignes_par_thread = hauteur / num_threads;
        debut = thread_id * lignes_par_thread;
        fin = (thread_id == num_threads - 1) ? hauteur : debut + lignes_par_thread;
        
        for (i = debut; i < fin; i++)
            for (j = 0; j < largeur; j++)
                calculPoint(i, j);
    }
}

/**
 * Version 3: Section critique avec répartition dynamique ligne par ligne
 * NOTE: permet équilibrage charge optimal mais overhead synchronisation
 */
void calculImage_critical() {
    int i, j;
    int ligne_courante = 0;
    int ma_ligne;
    
    #pragma omp parallel private(ma_ligne, j)
    {
        while (1) {
            #pragma omp critical
            {
                ma_ligne = ligne_courante;
                ligne_courante++;
            }
            
            if (ma_ligne >= hauteur)
                break;
            
            for (j = 0; j < largeur; j++)
                calculPoint(ma_ligne, j);
        }
    }
}

/**
 * Version optimale: for parallèle avec schedule guided
 * NOTE: équilibre entre dynamic (overhead) et static (déséquilibre)
 */
void calculImage_guided() {
    int i, j;
    
    #pragma omp parallel for private(j) schedule(guided)
    for (i = 0; i < hauteur; i++)
        for (j = 0; j < largeur; j++)
            calculPoint(i, j);
}

/**
 * Initialise les paramètres pour la zone classique de Mandelbrot
 */
void initParametres(int larg, int haut, int maxIt) {
    largeur = larg;
    hauteur = haut;
    maxiter = maxIt;
    
    // Zone classique: [-2, 0.5] x [-1.25, 1.25]
    xmin = -2.0;
    ymin = -1.25;
    cotex = 2.5;
    cotey = 2.5;
    
    pasx = cotex / largeur;
    pasy = cotey / hauteur;
}

/**
 * Sauvegarde l'image au format PGM
 */
void sauvegarderImage(const char* filename) {
    FILE* f = fopen(filename, "w");
    if (!f) {
        printf("error open file %s\n", filename);
        return;
    }
    
    fprintf(f, "P2\n%d %d\n%d\n", largeur, hauteur, maxiter);
    
    for (int i = 0; i < hauteur; i++) {
        for (int j = 0; j < largeur; j++) {
            fprintf(f, "%d ", iteration[j][i]);
        }
        fprintf(f, "\n");
    }
    
    fclose(f);
    printf("image save %s\n", filename);
}

int main(int argc, char *argv[]) {
    int larg = 512, haut = 512, maxIt = 256;
    double debut, fin;
    
    if (argc > 1) larg = atoi(argv[1]);
    if (argc > 2) haut = atoi(argv[2]);
    if (argc > 3) maxIt = atoi(argv[3]);
    
    initParametres(larg, haut, maxIt);
    
    printf("mandelbrot %dx%d maxiter %d\n\n", largeur, hauteur, maxiter);
    
    // Version séquentielle
    debut = omp_get_wtime();
    calculImage_seq();
    fin = omp_get_wtime();
    printf("seq temps %.4f s\n", fin - debut);
    sauvegarderImage("mandelbrot_seq.pgm");
    
    // Version for parallèle
    debut = omp_get_wtime();
    calculImage_for_parallel();
    fin = omp_get_wtime();
    printf("for parallel dynamic temps %.4f s\n", fin - debut);
    
    // Version région parallèle
    debut = omp_get_wtime();
    calculImage_region_parallel();
    fin = omp_get_wtime();
    printf("region parallel temps %.4f s\n", fin - debut);
    
    // Version section critique
    debut = omp_get_wtime();
    calculImage_critical();
    fin = omp_get_wtime();
    printf("critical temps %.4f s\n", fin - debut);
    
    // Version guided (optimal)
    debut = omp_get_wtime();
    calculImage_guided();
    fin = omp_get_wtime();
    printf("guided optimal temps %.4f s\n", fin - debut);
    sauvegarderImage("mandelbrot_parallel.pgm");
    
    printf("\nconclusion schedule guided optimal\n");
    printf("equilibre charge irreguliere overhead reduit\n");
    
    return 0;
}

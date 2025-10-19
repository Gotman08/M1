/**
 * Exercice 1 - Calcul de Pi par la méthode de Monte Carlo
 * Parallélisation avec OpenMP
 */

#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <time.h>

/**
 * Génère un nombre aléatoire entre 0 et 1
 */
double alea() {
    return (double)rand() / RAND_MAX;
}

/**
 * Version séquentielle (référence)
 */
double monte_carlo_seq(int nb) {
    int dedans = 0, i;
    double x, y;
    
    for (i = 0; i < nb; i++) {
        x = alea();
        y = alea();
        if (x*x + y*y < 1) 
            dedans++;
    }
    
    return 4.0 * (double)dedans / nb;
}

/**
 * Version parallèle avec section critique
 * NOTE: moins efficace à cause de la sérialisation
 */
double monte_carlo_critical(int nb) {
    int dedans = 0, i;
    double x, y;
    
    #pragma omp parallel private(x, y, i)
    {
        #pragma omp for
        for (i = 0; i < nb; i++) {
            x = alea();
            y = alea();
            if (x*x + y*y < 1) {
                #pragma omp critical
                dedans++;
            }
        }
    }
    
    return 4.0 * (double)dedans / nb;
}

/**
 * Version parallèle avec réduction
 * NOTE: solution optimale, évite la sérialisation
 */
double monte_carlo_reduction(int nb) {
    int dedans = 0, i;
    double x, y;
    
    #pragma omp parallel for private(x, y) reduction(+:dedans)
    for (i = 0; i < nb; i++) {
        x = alea();
        y = alea();
        if (x*x + y*y < 1) 
            dedans++;
    }
    
    return 4.0 * (double)dedans / nb;
}

/**
 * Question 2: Ordonnancement
 * - STATIC: bonne charge équilibrée car chaque itération a le même coût
 * - DYNAMIC/GUIDED: inutiles ici (overhead sans bénéfice)
 */
double monte_carlo_schedule(int nb, char* schedule_type) {
    int dedans = 0, i;
    double x, y;
    
    if (strcmp(schedule_type, "static") == 0) {
        #pragma omp parallel for private(x, y) reduction(+:dedans) schedule(static)
        for (i = 0; i < nb; i++) {
            x = alea();
            y = alea();
            if (x*x + y*y < 1) 
                dedans++;
        }
    } else if (strcmp(schedule_type, "dynamic") == 0) {
        #pragma omp parallel for private(x, y) reduction(+:dedans) schedule(dynamic)
        for (i = 0; i < nb; i++) {
            x = alea();
            y = alea();
            if (x*x + y*y < 1) 
                dedans++;
        }
    } else if (strcmp(schedule_type, "guided") == 0) {
        #pragma omp parallel for private(x, y) reduction(+:dedans) schedule(guided)
        for (i = 0; i < nb; i++) {
            x = alea();
            y = alea();
            if (x*x + y*y < 1) 
                dedans++;
        }
    }
    
    return 4.0 * (double)dedans / nb;
}

int main(int argc, char *argv[]) {
    int nb = 10000000;
    double resultat;
    double debut, fin;
    
    if (argc > 1) {
        nb = atoi(argv[1]);
    }
    
    srand(time(NULL));
    
    printf("calcul pi monte carlo nb points %d\n\n", nb);
    
    // Version séquentielle
    debut = omp_get_wtime();
    resultat = monte_carlo_seq(nb);
    fin = omp_get_wtime();
    printf("seq approx %.6f temps %.4f s\n", resultat, fin - debut);
    
    // Version avec section critique
    debut = omp_get_wtime();
    resultat = monte_carlo_critical(nb);
    fin = omp_get_wtime();
    printf("critical approx %.6f temps %.4f s\n", resultat, fin - debut);
    
    // Version avec réduction
    debut = omp_get_wtime();
    resultat = monte_carlo_reduction(nb);
    fin = omp_get_wtime();
    printf("reduction approx %.6f temps %.4f s\n", resultat, fin - debut);
    
    // Test des ordonnancements
    debut = omp_get_wtime();
    resultat = monte_carlo_schedule(nb, "static");
    fin = omp_get_wtime();
    printf("static approx %.6f temps %.4f s\n", resultat, fin - debut);
    
    debut = omp_get_wtime();
    resultat = monte_carlo_schedule(nb, "dynamic");
    fin = omp_get_wtime();
    printf("dynamic approx %.6f temps %.4f s\n", resultat, fin - debut);
    
    printf("\nreponse question 2 ordonnancement static optimal\n");
    printf("iterations independantes cout egal\n");
    
    return 0;
}

#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

/*
Ce code calcule une approximation de Pi en utilisant la méthode de Monte Carlo.
*/


double alea() {
    return (double)rand()/(double)RAND_MAX;
}

int main(int argc, char *argv[]) {
    int nb = 1000000;
    int dedans = 0, i;
    double x, y;

    unsigned seed = 1234567u
                  ^ (unsigned int)omp_get_thread_num()
                  ^ (unsigned int)omp_get_wtime();

    #pragma omp parallel for private(x, y,i) reduction(+:dedans)
    for (i = 0; i < nb; i++) {
        x = alea();
        y = alea();
        if (x*x + y*y < 1) {
            dedans++;
        }
    }
    
    printf("approximation obtenue : %f\n", (double)dedans / nb);
    return 0;
}

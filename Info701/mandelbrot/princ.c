/* princ.c 
 */

#include <stdlib.h>
#include <stdio.h>
#include <sys/timeb.h>
#include "mandelbrot.h"

int main(void){
	/* pour le temps */
	struct timeb tav, tap;
	double te;

	initialise();  /* initialisation des parametres */

	ftime(&tav);
	calculImage(); /* calcul de l'image */
	ftime(&tap);
	te = (double) ( (1000 * tap.time + tap.millitm) - (1000 * tav.time + tav.millitm) ) / 1000;
	printf("Temps 		: %f\n",  te);

	sauvegarde();  /* creation de l'image au format tga */
	return 0;
}

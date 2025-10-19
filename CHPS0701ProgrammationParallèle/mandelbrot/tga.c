/* tga.c 
 */

#include <stdio.h>
#include "tga.h"

void sauvegardeTga(char rouge[], char vert[], char bleu[], 
					int hauteur, int largeur, char* nom) {
	FILE* sortie = fopen(nom, "w");
	int i,j,k;
		
	/* ecriture de l'en-tete */
	for (i=0; i<12; i++) 
		if (i==2) 
			fprintf(sortie, "%c", (char) 2);
		else
			fprintf(sortie, "%c", (char) 0);
		
	/* ecriture des dimensions de l'image */
	fprintf(sortie, "%c%c", (char) (largeur & 0xff), (char) ((largeur >> 8) & 0xff) );
	fprintf(sortie, "%c%c", (char) (hauteur & 0xff), (char) ((hauteur >> 8) & 0xff) );
	fprintf(sortie, "%c%c", (char) (24), 			   (char) (0x20) );

	/* les pixels */
	for (i=0 ; i < hauteur ; i++) 
		for (j=0 ; j < largeur ; j++) {
		/* le repere est inverse en y */
			k = i * largeur + j;
			fprintf(sortie, "%c", bleu [k]);  
			fprintf(sortie, "%c", vert [k]);  
			fprintf(sortie, "%c", rouge[k]);  
		}

	fflush(sortie);
	fclose(sortie);
	fprintf(stderr, "Fichier %s cree.\n", nom);
}

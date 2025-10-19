#include <stdio.h>
#include <openmp.h>
/* --------------------------------*/
/* taille maximale de l'image */
#define MAXX 1024
#define MAXY 1024
/* --------------------------------*/
/* variables, globales */
/* pour la zone du plan */

double xmin, ymin,		/* point de départ */
	cotex, cotey;		/* largeur */

    /* pour l'image */
int largeur, hauteur,		/* dim effectives */
	iteration[MAXX][MAXY];	/* les résultats */

    /* pour le traitement */
int maxiter;			/* nb max d'iterations */
double pasx, pasy;		/* pour obtenir les coord. dans la zone a partir de celles du pixel */


/*
...
pasx = (double) cotex / largeur;
pasy = (double) cotey / hauteur;
...
*/

/* --------------------------------*/
/* les deux principales méthodes
 * (version séquentielle) 
*/

void calculPoint(int px, int py){
	double xc, yc,		/* coord. ds l'esp. uitilisateur */
		x=0, y=0, sx,	/* pr les termes de la suite */
		module=0;	/* pour l'arret premature */
	int nbiter=0;		/* pr conclure apres l'arret */
	xc = (double) xmin + pasx * px;
	yc = (double) ymin + pasy * py;
    
	while ( module<2  &&  nbiter<maxiter ) {
		sx = x; 
		x = x*x - y*y + xc;
		y = 2*sx*y + yc;
		module = sqrt(x*x + y*y);
		nbiter++;
	}
	iteration[px][py] = nbiter;
}

void calculImage(){
	int i,j;
	for (i=0 ; i<hauteur ; i++)
		for (j=0 ; j<largeur ; j++)
			calculPoint(i,j);
}
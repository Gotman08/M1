/* mandelbrot.c 
 */

#include <strings.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include "mandelbrot.h"
#include "tga.h"

/*****************************************************************************/
/* Les differentes variables pour le calcul de l'ensemble		     */
/*****************************************************************************/

#define MAXX	1024
#define MAXY	1024

int maxiter, 
    iteration[MAXX][MAXY],
    hauteur, largeur; /* pour l'image */

double xmin, ymin, cotex, cotey;

double	pasx, pasy;

char chemin[150], /* le repertoire courant */
     nom[200]; /* le nom du fichier de sortie */

/*****************************************************************************/
/* Fonctions locales (pour les palettes de couleurs)			     */
/*****************************************************************************/
int rougeRGB(int i, int mi) {
  int b = mi / 8;
  double d = 256.0 / b;
  
  if (i==mi)
    return (0);
  else if (i < b)
    return ((int)(d*i));
  else if (i < 2*b)
    return (255 - (int)((i-b)*d));
  else if (i < 3*b)
    return (0x00);
  else if (i < 4*b)
    return ((int)((i-3*b)*d));
  else if (i < 7*b)
    return (255);
  else return (255 - (int)((i-7*b)*d));
}

int vertRGB(int i, int mi) {
  int b = mi / 8;
  double d = 256.0 / b;

  if (i==mi)
    return (0);
  else if (i < b)
    return (0x00);
  else if (i < 2*b)
    return ((int)((i-b)*d));
  else if (i < 3*b)
    return (255 - (int)((i-2*b)*d));
  else if (i < 4*b)
    return ((int) ((i-3*b)*d));
  else if (i < 6*b)
    return (255 - (int)((i-5*b)*d/2));
  else return (0);
}

int bleuRGB(int i, int mi) {
  int b = mi / 8;
  double d = 256.0 / b;

  if (i==mi)
    return (0);
  else if (i < b)
    return (255-(int)(i*d));
  else if (i < 2*b)
    return (0x00);
  else if (i < 3*b)
    return ((int)((i- 2*b)*d));
  else if (i < 4*b)
    return (255 -(int)((i-3*b)*d));
  else if (i < 6*b)
    return (0);
  else if (i < 7*b)
    return ((int)((i-6*b)*d));
  else return (255);
}

/*****************************************************************************/
/* fonctions rouge, vert et bleu : valeurs au point (x,y)	              	 */
/*****************************************************************************/

int rouge(int x, int y)	{
  static int c, r;
  c = iteration[x][y]; 
  
  r = rougeRGB(c, maxiter);
  return r;
}

int vert(int x, int y) {
  static int c, r;
  c =  iteration[x][y];
  
  r = vertRGB(c, maxiter);
  return r;
}

int bleu(int x, int y) {
  static int c, r;
  c = iteration[x][y];
  
  r = bleuRGB(c, maxiter);
  return r;
}

/*****************************************************************************/
/* fonction initialise : demande a l'utilisateur les parametres necessaires  */
/* pour determiner l'ensemble de Mandelbrot		       		     */
/*****************************************************************************/

void initialise() {
  fprintf(stderr, "Quelle l'abscisse du point en bas a gauche ?");
  scanf("%lf", &xmin);
  fprintf(stderr, "Quelle l'ordonnee du point en bas a gauche ?");
  scanf("%lf", &ymin);
  fprintf(stderr, "Quelle est la longueur sur l'axe des x du rectangle  ?");
  scanf("%lf", &cotex);
  fprintf(stderr, "Quelle est la longueur sur l'axe des y du rectangle  ?");
  scanf("%lf", &cotey);
  fprintf(stderr, "Quelle est la hauteur de l'image  ?");
  scanf("%d", &hauteur);
  fprintf(stderr, "Quelle est la largeur de l'image  ?");
  scanf("%d", &largeur);
  fprintf(stderr, "Nombre d'iterations autorisees  ?");
  scanf("%d", &maxiter);

/* 
  xmin=-2;
  ymin=-1.25;
  cotex=0.5;
  cotey=1.25;
  hauteur=1000;
  largeur=1000;
  maxiter=100;
*/

  pasx = (double) cotex / largeur;
  pasy = (double) cotey / hauteur;
	
  fprintf(stderr, "Calcul de l'ensemble de Mandelbrot \n");
  fprintf(stderr, "----------------------------------\n");

  printf("image 		: %d x %d\n", hauteur, largeur);
  printf("abscisses	: %g .. %g => %g\n", xmin, xmin+cotex, cotex);
  printf("ordonnees	: %g .. %g => %g\n", ymin, ymin+cotex, cotey);
  printf("max iterations	: %d\n", maxiter);
}

/*****************************************************************************/
/* fonction calculPoint : calcul le nombre d'iterations necessaires pour     */
/* determiner si le point ecran (cx, cy) appartient a l'ensemble de          */
/* Mandelbrot                                                                */
/*****************************************************************************/

void calculPoint(int cx,int cy) {
  double sx, x=0, rx , y=0, ry , m=0;
  int 	 n=0;

  /* les coordonnees dans l'espace utilisateur */
  rx = (double) xmin + pasx * cx; 
  ry = (double) ymin + pasy * cy;

  while( (m<2) && (n<maxiter)) {
    sx = x; /* pour le calcul de y */
    x = x*x - y*y + rx;
    y = 2*sx*y + ry;
    m = sqrt(x*x+y*y);
    n++;
  } 
  iteration[cx][cy] = n;
}

/*****************************************************************************/
/* fonction calculImage : calcul pour chaque point P de l'ecran, le nombre   */
/* d'iterations necessaires pour determiner si P appartient a l'ensemble de  */
/* Mandelbrot                                                                */
/*****************************************************************************/

void calculImage() {
   int i,j;
   for(i=0 ; i<hauteur ; i++)
     for(j=0 ; j<largeur ; j++) 
        calculPoint(j,i);
}

/*****************************************************************************/
/* fonction sauvegarde : cree un fichier image tga representant l'ensemble   */
/*  de mandelbrot calcule                                                    */
/*****************************************************************************/

void sauvegarde() {
  int	i, j;
  char  nom[50];

  char 	r[MAXX*MAXY], 
		v[MAXX*MAXY], 
		b[MAXX*MAXY];

  for (i=0; i<hauteur; i++) 
    for (j=0; j<largeur; j++) {
      r[j + (hauteur-i-1) * largeur] = rouge(j, i);
      v[j + (hauteur-i-1) * largeur] = vert(j, i);
      b[j + (hauteur-i-1) * largeur] = bleu(j, i);
    }
/* printf("Quel est le nom du fichier tga a creer ? ");
  scanf("%s", &nom);
*/
  strcpy(nom,"mandelbrot.tga");
  sauvegardeTga(r, v, b, hauteur, largeur, nom);
}

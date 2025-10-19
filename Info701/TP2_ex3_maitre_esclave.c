/**
 * Exercice 3 - Equilibre de charge dynamique maître-esclave
 * Tâches irrégulières avec file d'attente centralisée
 */

#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <unistd.h>
#include <time.h>

#define NB_TACHES 100
#define TEMPS_MAX 2  // secondes max par tache

// Données globales
int taches[NB_TACHES];
double resultats[NB_TACHES];
int nb_taches_total = NB_TACHES;

/**
 * Simule un traitement avec temps variable
 * @param valeur Caractéristique de la tâche
 * @return Résultat du traitement
 */
double traitement(int valeur) {
    // Temps aléatoire de traitement
    int temps_us = (rand() % (TEMPS_MAX * 1000000));
    usleep(temps_us);
    
    // Retourne valeur aléatoire dans un intervalle
    return (double)(rand() % 100) - 50.0;
}

/**
 * Version 1: Avec sections critiques
 * NOTE: section critique pour accès file, calcul en parallèle
 */
void maitre_esclave_critical() {
    int tache_courante = 0;
    double somme = 0.0;
    int nb_positifs = 0;
    
    printf("\n=== version critical ===\n");
    
    #pragma omp parallel
    {
        int thread_id = omp_get_thread_num();
        
        if (thread_id == 0) {
            // Maître: attend résultats et calcule moyenne
            int taches_terminees = 0;
            
            while (taches_terminees < nb_taches_total) {
                #pragma omp critical(resultats_queue)
                {
                    // Récupère résultats disponibles
                    for (int i = 0; i < nb_taches_total; i++) {
                        if (resultats[i] != -999.0) {  // marqueur "traité"
                            if (resultats[i] > 0) {
                                somme += resultats[i];
                                nb_positifs++;
                            }
                            resultats[i] = -999.0;
                            taches_terminees++;
                        }
                    }
                }
                usleep(1000);  // petite pause
            }
            
            double moyenne = (nb_positifs > 0) ? somme / nb_positifs : 0.0;
            printf("maitre moyenne positifs %.2f nb %d\n", moyenne, nb_positifs);
            
        } else {
            // Esclaves: récupèrent et traitent tâches
            while (1) {
                int ma_tache = -1;
                
                #pragma omp critical(taches_queue)
                {
                    if (tache_courante < nb_taches_total) {
                        ma_tache = tache_courante;
                        tache_courante++;
                    }
                }
                
                if (ma_tache == -1)
                    break;
                
                // Traitement (hors section critique)
                double resultat = traitement(taches[ma_tache]);
                
                // Stockage résultat
                #pragma omp critical(resultats_queue)
                {
                    resultats[ma_tache] = resultat;
                }
                
                printf("esclave %d tache %d resultat %.2f\n", 
                       thread_id, ma_tache, resultat);
            }
        }
    }
}

/**
 * Version 2: Avec sections critiques nommées
 * NOTE: permet accès concurrent file tâches et file résultats
 * Intéressant quand: plusieurs ressources partagées indépendantes
 */
void maitre_esclave_critical_named() {
    int tache_courante = 0;
    int resultat_courant = 0;
    double somme = 0.0;
    int nb_positifs = 0;
    
    printf("\n=== version critical named ===\n");
    
    #pragma omp parallel
    {
        int thread_id = omp_get_thread_num();
        
        if (thread_id == 0) {
            // Maître
            while (resultat_courant < nb_taches_total) {
                #pragma omp critical(lecture_resultats)
                {
                    if (resultat_courant < nb_taches_total && 
                        resultats[resultat_courant] != -999.0) {
                        double res = resultats[resultat_courant];
                        if (res > 0) {
                            somme += res;
                            nb_positifs++;
                        }
                        resultat_courant++;
                    }
                }
                usleep(1000);
            }
            
            double moyenne = (nb_positifs > 0) ? somme / nb_positifs : 0.0;
            printf("maitre moyenne positifs %.2f nb %d\n", moyenne, nb_positifs);
            
        } else {
            // Esclaves
            while (1) {
                int ma_tache = -1;
                
                #pragma omp critical(attribution_taches)
                {
                    if (tache_courante < nb_taches_total) {
                        ma_tache = tache_courante;
                        tache_courante++;
                    }
                }
                
                if (ma_tache == -1)
                    break;
                
                double resultat = traitement(taches[ma_tache]);
                resultats[ma_tache] = resultat;
                
                printf("esclave %d tache %d resultat %.2f\n", 
                       thread_id, ma_tache, resultat);
            }
        }
    }
}

/**
 * Version 3: Avec verrous explicites
 * NOTE: plus de contrôle, permet test_lock pour éviter attente
 */
void maitre_esclave_locks() {
    omp_lock_t lock_taches;
    omp_lock_t lock_resultats;
    
    omp_init_lock(&lock_taches);
    omp_init_lock(&lock_resultats);
    
    int tache_courante = 0;
    double somme = 0.0;
    int nb_positifs = 0;
    int taches_terminees = 0;
    
    printf("\n=== version locks ===\n");
    
    #pragma omp parallel
    {
        int thread_id = omp_get_thread_num();
        
        if (thread_id == 0) {
            // Maître
            while (taches_terminees < nb_taches_total) {
                omp_set_lock(&lock_resultats);
                
                for (int i = 0; i < nb_taches_total; i++) {
                    if (resultats[i] != -999.0) {
                        if (resultats[i] > 0) {
                            somme += resultats[i];
                            nb_positifs++;
                        }
                        resultats[i] = -999.0;
                        taches_terminees++;
                    }
                }
                
                omp_unset_lock(&lock_resultats);
                usleep(1000);
            }
            
            double moyenne = (nb_positifs > 0) ? somme / nb_positifs : 0.0;
            printf("maitre moyenne positifs %.2f nb %d\n", moyenne, nb_positifs);
            
        } else {
            // Esclaves
            while (1) {
                int ma_tache = -1;
                
                omp_set_lock(&lock_taches);
                if (tache_courante < nb_taches_total) {
                    ma_tache = tache_courante;
                    tache_courante++;
                }
                omp_unset_lock(&lock_taches);
                
                if (ma_tache == -1)
                    break;
                
                double resultat = traitement(taches[ma_tache]);
                
                omp_set_lock(&lock_resultats);
                resultats[ma_tache] = resultat;
                omp_unset_lock(&lock_resultats);
                
                printf("esclave %d tache %d resultat %.2f\n", 
                       thread_id, ma_tache, resultat);
            }
        }
    }
    
    omp_destroy_lock(&lock_taches);
    omp_destroy_lock(&lock_resultats);
}

/**
 * Initialise les tâches
 */
void init_taches() {
    for (int i = 0; i < NB_TACHES; i++) {
        taches[i] = i + 1;
        resultats[i] = -999.0;  // marqueur "non traité"
    }
}

int main(int argc, char *argv[]) {
    double debut, fin;
    
    srand(time(NULL));
    
    printf("maitre esclave taches %d\n", NB_TACHES);
    printf("threads %d\n", omp_get_max_threads());
    
    // Version avec sections critiques
    init_taches();
    debut = omp_get_wtime();
    maitre_esclave_critical();
    fin = omp_get_wtime();
    printf("temps %.4f s\n", fin - debut);
    
    // Version avec sections critiques nommées
    init_taches();
    debut = omp_get_wtime();
    maitre_esclave_critical_named();
    fin = omp_get_wtime();
    printf("temps %.4f s\n", fin - debut);
    
    // Version avec verrous
    init_taches();
    debut = omp_get_wtime();
    maitre_esclave_locks();
    fin = omp_get_wtime();
    printf("temps %.4f s\n", fin - debut);
    
    printf("\navantages locks controle fin test_lock\n");
    printf("avantages critical named parallelisme accru\n");
    
    return 0;
}

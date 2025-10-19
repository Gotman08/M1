# TP2 OpenMP - Réponses aux questions

## Exercice 1 - Monte Carlo

### Question 1: Parallélisation

**Version avec section critique:**
```c
#pragma omp parallel for
for (i = 0; i < nb; i++) {
    x = alea();
    y = alea();
    if (x*x + y*y < 1) {
        #pragma omp critical
        dedans++;
    }
}
```
- **Avantage**: simple à comprendre
- **Inconvénient**: sérialisation à chaque incrémentation → overhead important

**Version avec réduction:**
```c
#pragma omp parallel for reduction(+:dedans)
for (i = 0; i < nb; i++) {
    x = alea();
    y = alea();
    if (x*x + y*y < 1) 
        dedans++;
}
```
- **Avantage**: optimal, pas de sérialisation, chaque thread a sa copie privée
- **Solution recommandée**

### Question 2: Ordonnancement

**STATIC (recommandé)**
- Charge équilibrée: chaque itération a le même coût (2 alea + 1 test)
- Pas d'overhead de synchronisation
- Distribution équitable des itérations

**DYNAMIC/GUIDED (inutiles)**
- Overhead de synchronisation sans bénéfice
- Utile seulement si charge irrégulière entre itérations

---

## Exercice 2 - Mandelbrot

### Parallélisation de `calculImage()`

**1. Boucle for parallèle:**
```c
#pragma omp parallel for private(j) schedule(dynamic)
for (i = 0; i < hauteur; i++)
    for (j = 0; j < largeur; j++)
        calculPoint(i, j);
```
- Simple et efficace
- Schedule dynamic recommandé car charge irrégulière

**2. Région parallèle avec gestion explicite:**
```c
#pragma omp parallel private(i, j, debut, fin)
{
    int tid = omp_get_thread_num();
    int nthreads = omp_get_num_threads();
    debut = tid * (hauteur / nthreads);
    fin = (tid == nthreads-1) ? hauteur : debut + (hauteur/nthreads);
    
    for (i = debut; i < fin; i++)
        for (j = 0; j < largeur; j++)
            calculPoint(i, j);
}
```
- Contrôle explicite de la répartition
- Risque de déséquilibre si convergence variable

**3. Section critique ligne par ligne:**
```c
int ligne_courante = 0;
#pragma omp parallel private(ma_ligne, j)
{
    while (1) {
        #pragma omp critical
        {
            ma_ligne = ligne_courante++;
        }
        if (ma_ligne >= hauteur) break;
        
        for (j = 0; j < largeur; j++)
            calculPoint(ma_ligne, j);
    }
}
```
- Équilibrage optimal
- Overhead de synchronisation élevé

**4. Solution optimale - schedule(guided):**
```c
#pragma omp parallel for schedule(guided)
for (i = 0; i < hauteur; i++)
    for (j = 0; j < largeur; j++)
        calculPoint(i, j);
```
- Compromis entre dynamic et static
- Blocs décroissants → bon équilibrage + overhead réduit

**Conclusion**: Pour Mandelbrot, **schedule(guided)** est optimal car:
- Charge très irrégulière (bord vs centre)
- Équilibrage dynamique nécessaire
- Overhead limité par blocs décroissants

---

## Exercice 3 - Maître-Esclave

### Question 1: Schéma des communications

```
       MAÎTRE
         |
    File tâches [T1, T2, ..., Tn]
         |
    +----|----+----+
    |    |    |    |
  ESC1 ESC2 ESC3 ESCn
    |    |    |    |
    +----+----+----+
         |
    File résultats
         |
       MAÎTRE (agrégation)
```

**Flux**:
1. Maître initialise file tâches
2. Esclaves prennent tâches (accès exclusif)
3. Esclaves calculent
4. Esclaves déposent résultats (accès exclusif)
5. Maître récupère et agrège résultats

### Question 2: Structure globale

```c
int taches[NB_TACHES];
double resultats[NB_TACHES];

#pragma omp parallel
{
    int tid = omp_get_thread_num();
    
    if (tid == 0) {
        maitre();
    } else {
        esclave();
    }
}
```

### Question 3: Solution avec sections critiques

**Sections critiques nommées intéressantes quand:**
- Plusieurs ressources partagées **indépendantes**
- Permet accès concurrent à file tâches ET file résultats
- Réduit contention vs. une seule section critique globale

```c
#pragma omp critical(taches_queue)
{ /* attribution tâche */ }

#pragma omp critical(resultats_queue)
{ /* dépôt résultat */ }
```

**Avantage**: thread peut prendre tâche pendant qu'un autre dépose résultat

### Question 4: Implémentation avec verrous

**Avantages des verrous:**
- Contrôle plus fin (test_lock, trylock)
- Possibilité de polling non-bloquant
- Meilleure visibilité du code

```c
omp_lock_t lock_taches, lock_resultats;
omp_init_lock(&lock_taches);
omp_init_lock(&lock_resultats);

// Esclave
omp_set_lock(&lock_taches);
ma_tache = recuperer_tache();
omp_unset_lock(&lock_taches);

// ... calcul ...

omp_set_lock(&lock_resultats);
deposer_resultat();
omp_unset_lock(&lock_resultats);

omp_destroy_lock(&lock_taches);
```

---

## Synthèse des choix d'ordonnancement

| Cas | Schedule | Raison |
|-----|----------|--------|
| Monte Carlo | STATIC | Charge équilibrée, coût uniforme |
| Mandelbrot | GUIDED | Charge irrégulière, bon compromis |
| Maître-Esclave | DYNAMIC (implicit) | Tâches hétérogènes en temps |

**Règle générale:**
- Charge régulière → STATIC
- Charge irrégulière + petites tâches → DYNAMIC
- Charge irrégulière + grosses tâches → GUIDED

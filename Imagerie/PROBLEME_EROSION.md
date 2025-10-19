# ⚠️ IMPORTANT : Pourquoi l'érosion ne change rien ?

## 🔍 Problème constaté

Vous appliquez **érosion** ou **dilatation** mais l'image reste identique (toute blanche).

## ✅ Solution

Les opérations morphologiques sont **conçues pour les images binaires** (noir et blanc pur).

### 📋 Séquence correcte

```
1. [8] recharger          ← Charger l'image originale
2. [2] binariser          ← Créer du contraste !
   seuil: 128             ← Entrer une valeur
3. [1] afficher           ← Vérifier qu'il y a du noir ET blanc
4. [9] erosion            ← Maintenant ça va fonctionner !
   taille: 3
```

## 🎯 Exemple complet

### Image toute blanche (AVANT binarisation)
```
■■■■■■■■
■■■■■■■■    ← Érosion ne change RIEN
■■■■■■■■       (déjà tout blanc = minimum = blanc)
■■■■■■■■
```

### Image binaire (APRÈS binarisation avec seuil 128)
```
■■■····■       
■■■····■    ← Zones noires ET blanches
···■■■■■    
····■■■■    
```

### Après érosion 3×3
```
■······■       
········■    ← Les zones BLANCHES rétrécissent !
·········       (érosion = prend le minimum)
·········    
```

### Après dilatation 3×3
```
■■■■■■■■       
■■■■■■■■    ← Les zones BLANCHES s'agrandissent !
■■■■■■■■       (dilatation = prend le maximum)
■■■■■■■■    
```

## 🧪 Test rapide

Dans votre terminal, tapez cette séquence exacte :

```bash
./Tp1

# Menu apparaît
8          # recharger
2          # binariser
80         # seuil BAS = plus de contraste noir/blanc
1          # afficher → vous DEVEZ voir noir ET blanc
9          # erosion
3          # noyau 3x3
           # → l'image devient PLUS SOMBRE
```

## 📊 Comprendre les opérations

| Opération | Effet | Quand utiliser |
|-----------|-------|----------------|
| **Érosion** | Réduit les zones **blanches** | Supprimer bruit blanc, séparer objets |
| **Dilatation** | Agrandit les zones **blanches** | Combler trous, connecter objets |
| **Ouverture** | Érosion → Dilatation | Lisser contours, supprimer petits points blancs |
| **Fermeture** | Dilatation → Érosion | Combler petits trous noirs, connecter zones proches |

## ⚡ Règle d'or

> **TOUJOURS binariser AVANT les opérations morphologiques !**

Sans binarisation, votre image en niveaux de gris (0-255) ne montre pas d'effet visible.

## 🔬 Pourquoi ça ne marchait pas ?

Votre image source `dog32.hpp` ou `Img.jpg` contient probablement :
- Beaucoup de pixels clairs (> 200)
- Peu de pixels sombres (< 50)

Résultat :
- Sans binarisation → tout reste gris clair → érosion imperceptible
- Avec binarisation (seuil 100-150) → contraste noir/blanc → érosion VISIBLE

## 💡 Essayez maintenant !

```
[8] recharger
[2] binariser 100
[9] erosion 5     ← Vous verrez BEAUCOUP de noir !
```

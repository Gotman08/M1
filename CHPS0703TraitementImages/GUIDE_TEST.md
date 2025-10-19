# Guide de test des opérations morphologiques

## 🎯 Séquence de test recommandée

### Test 1: Binarisation d'abord
```
[8] recharger          # Image originale
[2] binariser          # Seuil: 128
    → Vous devriez voir du noir ET du blanc
```

### Test 2: Érosion sur image binaire
```
[9] erosion            # Taille: 3
    → Les zones blanches RÉTRÉCISSENT
    → Les zones noires S'AGRANDISSENT
```

### Test 3: Recharger et dilater
```
[8] recharger
[2] binariser          # Seuil: 128
[10] dilatation        # Taille: 3
    → Les zones blanches S'AGRANDISSENT
    → Les zones noires RÉTRÉCISSENT
```

### Test 4: Ouverture (supprime petits éléments blancs)
```
[8] recharger
[2] binariser          # Seuil: 128
[11] ouverture         # Taille: 5
    → Lisse les contours
    → Supprime les petits points blancs isolés
```

### Test 5: Fermeture (comble petits trous noirs)
```
[8] recharger
[2] binariser          # Seuil: 128
[12] fermeture         # Taille: 5
    → Comble les petits trous noirs
    → Connecte les zones blanches proches
```

## 🔬 Pourquoi l'image devient blanche?

### Cas 1: Image déjà uniforme
- Si l'image de départ est presque toute blanche (comme `dog32.hpp`)
- Les opérations morphologiques préservent l'uniformité
- **Solution**: Binariser d'abord avec un seuil adapté

### Cas 2: Noyau trop grand
- Un noyau 7×7 ou plus sur une petite image
- Uniformise rapidement les valeurs
- **Solution**: Utiliser noyau 3×3 ou 5×5

## 📊 Séquence complète de test

```
1. [8]  recharger
2. [1]  afficher          # Voir image originale
3. [2]  binariser 128     # Créer contraste noir/blanc
4. [1]  afficher          # Vérifier binarisation
5. [9]  erosion 3         # Eroder (réduit blanc)
6. [1]  afficher          # Voir effet érosion
7. [8]  recharger         # Reset
8. [2]  binariser 128     # Re-binariser
9. [10] dilatation 3      # Dilater (agrandit blanc)
10. [1] afficher          # Voir effet dilatation
```

## ✅ Résultat attendu

- **Érosion** : Image plus sombre (blanc → gris → noir)
- **Dilatation** : Image plus claire (noir → gris → blanc)
- **Ouverture** : Contours lissés, petits détails blancs supprimés
- **Fermeture** : Trous comblés, zones blanches connectées

## 🚨 Si tout reste blanc

Cela signifie que:
1. L'image source est déjà très claire
2. Les opérations fonctionnent correctement
3. Il faut **binariser avec un seuil plus bas** (ex: 100 ou 80)
   pour créer plus de contraste noir/blanc

## 💡 Astuce

Pour bien voir les effets morphologiques :
```
[8]  recharger
[2]  binariser 100    # Seuil BAS = plus de noir
[9]  erosion 3        # Vous verrez BEAUCOUP de noir
[8]  recharger
[2]  binariser 100
[10] dilatation 3     # Vous verrez plus de blanc
```

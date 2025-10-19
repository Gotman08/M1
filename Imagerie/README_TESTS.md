# Tests Unitaires - Traitement d'Image

## 📋 Vue d'ensemble

Le fichier `test.cpp` contient une suite de tests unitaires pour valider toutes les opérations de traitement d'image.

## 🚀 Compilation et exécution

### Windows (PowerShell ou CMD)
```powershell
g++ -std=c++17 -Wall -Wextra -O2 test.cpp -o test.exe
.\test.exe
```

### Linux / WSL / macOS
```bash
make test
# ou
g++ -std=c++17 -Wall -Wextra -O2 test.cpp -o test
./test
```

## 🧪 Tests implémentés

### ✅ Test 1: Création d'image
- Vérifie l'initialisation correcte (largeur, hauteur, canaux)

### ✅ Test 2: Accès aux pixels
- Vérifie les opérations `setPixel()` et `getPixel()`
- Teste la cohérence des 3 canaux RGB

### ✅ Test 3: Conversion to_u8
- Conversion double → uint8_t
- Arrondi à 0.5 près
- Clamping dans [0, 255]
- Cas limites: valeurs négatives et > 255

### ✅ Test 4: Calcul de luminance
- Formule Rec. 601: Y = 0.299R + 0.587G + 0.114B
- Cas de référence: blanc, noir, couleurs pures

### ✅ Test 5: Opérateur négatif
- Transformation I'(x) = 255 - I(x)
- Test d'involution: négatif(négatif(x)) = x

### ✅ Test 6: Binarisation
- Seuillage spectral
- Pixel clair → blanc (255)
- Pixel sombre → noir (0)

### ✅ Test 7: Rehaussement
- Transformation affine: I'(x) = α×I(x) + β
- Test gain multiplicatif (α)
- Test offset additif (β)
- Clamping valeurs hors [0, 255]

### ✅ Test 8: Quantification
- Réduction niveaux de gris
- Calcul représentant d'intervalle
- Exception pour n < 2

### ✅ Test 9: Robustesse
- Image 1×1
- Chaînage d'opérations multiples

## 📊 Sortie attendue

```
===============================================
tests unitaires traitement image
===============================================

test creation image:
[OK] largeur correcte
[OK] hauteur correcte
[OK] nombre canaux correct

test acces pixels:
[OK] canal rouge ok
[OK] canal vert ok
[OK] canal bleu ok

...

===============================================
resultat: XX ok, 0 fail
===============================================
```

## 🔧 Structure du code de test

### Classe `ImgTest`
Version simplifiée de `Img` sans Singleton pour faciliter les tests:
- Allocation/libération mémoire
- Opérations de base (négatif, binarisation, rehaussement, quantification)
- Méthodes statiques (to_u8, getLuminance)

### Macro `TEST_ASSERT`
```cpp
TEST_ASSERT(condition, message)
```
- Affiche `[OK]` si condition vraie
- Affiche `[FAIL]` si condition fausse
- Incrémente compteurs globaux

## ✨ Ajout de nouveaux tests

Pour ajouter un test:

```cpp
void test_ma_fonction() {
    cout << "\ntest ma fonction:" << endl;
    
    ImgTest img(5, 5, 3);
    // ... configuration
    
    TEST_ASSERT(condition, "description");
}

// Dans main():
int main() {
    // ...
    test_ma_fonction();
    // ...
}
```

## 🎯 Code retour

- `0` : Tous les tests réussis
- `1` : Au moins un test échoué

Utilisable dans scripts CI/CD :
```bash
./test && echo "ok" || echo "fail"
```

## 📝 Notes

- Les tests sont **indépendants** (pas de dépendance au Singleton)
- Pas besoin du buffer `IMG` global
- Tests rapides (< 1 seconde)
- Couvrent les cas nominaux + limites

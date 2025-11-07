# Exercice 1 : Calculs Analytiques

## Énoncé

Pour la solution exacte :
```
u(x,y) = 1 + sin(πx/2) + x(x-4)cos(πy/2)
```

Calculer :
1. Le second membre **f(x,y)** tel que -Δu = f
2. Les conditions de Dirichlet **uE** sur Γ_D
3. Vérifier la compatibilité avec la condition de Neumann ∇u·n = 0 sur Γ_N

---

## 1. Calcul du Second Membre f(x,y)

### Dérivées Premières

**∂u/∂x** :
```
∂u/∂x = 0 + (π/2)cos(πx/2) + (2x-4)cos(πy/2)
      = (π/2)cos(πx/2) + (2x-4)cos(πy/2)
```

**∂u/∂y** :
```
∂u/∂y = 0 + 0 + x(x-4)·(−π/2)sin(πy/2)
      = −(π/2)x(x-4)sin(πy/2)
```

### Dérivées Secondes

**∂²u/∂x²** :
```
∂²u/∂x² = −(π/2)·(π/2)sin(πx/2) + 2cos(πy/2)
        = −(π²/4)sin(πx/2) + 2cos(πy/2)
```

**∂²u/∂y²** :
```
∂²u/∂y² = −(π/2)x(x-4)·(π/2)cos(πy/2)
        = −(π²/4)x(x-4)cos(πy/2)
```

### Laplacien

```
Δu = ∂²u/∂x² + ∂²u/∂y²
   = −(π²/4)sin(πx/2) + 2cos(πy/2) − (π²/4)x(x-4)cos(πy/2)
   = −(π²/4)[sin(πx/2) + x(x-4)cos(πy/2)] + 2cos(πy/2)
```

### Second Membre

```
f(x,y) = −Δu
       = (π²/4)[sin(πx/2) + x(x-4)cos(πy/2)] − 2cos(πy/2)
```

** Résultat** :
```
f(x,y) = (π²/4)sin(πx/2) + (π²/4)x(x-4)cos(πy/2) − 2cos(πy/2)
```

---

## 2. Conditions de Dirichlet uE

Le bord de Dirichlet est Γ_D = {0,4} × [0,2], c'est-à-dire les bords verticaux x=0 et x=4.

### Sur x = 0

```
uE(0,y) = 1 + sin(0) + 0·(0-4)cos(πy/2)
        = 1 + 0 + 0
        = 1
```

### Sur x = 4

```
uE(4,y) = 1 + sin(2π) + 4·(4-4)cos(πy/2)
        = 1 + 0 + 0
        = 1
```

** Résultat** :
```
uE(x,y) = 1    pour (x,y) ∈ Γ_D = {0,4} × [0,2]
```

---

## 3. Vérification de la Condition de Neumann

Le bord de Neumann est Γ_N = ]0,4[ × {0,2}, c'est-à-dire les bords horizontaux y=0 et y=2.

La condition est : **∇u·n = 0** sur Γ_N

### Gradient de u

```
∇u = (∂u/∂x, ∂u/∂y)
   = ((π/2)cos(πx/2) + (2x-4)cos(πy/2),  −(π/2)x(x-4)sin(πy/2))
```

### Sur y = 0 (bord inférieur)

**Normale extérieure** : n = (0, −1)

```
∇u·n = ((π/2)cos(πx/2) + (2x-4)cos(0),  −(π/2)x(x-4)sin(0)) · (0, −1)
     = 0 · ((π/2)cos(πx/2) + (2x-4)) + (−1) · (−(π/2)x(x-4)·0)
     = 0 + 0
     = 0
```

** Vérifié** : sin(0) = 0

### Sur y = 2 (bord supérieur)

**Normale extérieure** : n = (0, 1)

```
∇u·n = ((π/2)cos(πx/2) + (2x-4)cos(π),  −(π/2)x(x-4)sin(π)) · (0, 1)
     = 0 + 1 · (−(π/2)x(x-4)·0)
     = 0
```

** Vérifié** : sin(π) = 0

---

## Résumé des Résultats

| Quantité | Expression |
|----------|------------|
| **Solution exacte** | u(x,y) = 1 + sin(πx/2) + x(x-4)cos(πy/2) |
| **Second membre** | f(x,y) = (π²/4)[sin(πx/2) + x(x-4)cos(πy/2)] − 2cos(πy/2) |
| **Condition Dirichlet** | uE(0,y) = uE(4,y) = 1 |
| **Condition Neumann** | ∇u·n = 0 sur y=0 et y=2  |

---

## Implémentation

Ces formules sont implémentées dans :
- **FreeFem++** : [`freefem/validation.edp`](freefem/validation.edp) et [`freefem/validation_pen.edp`](freefem/validation_pen.edp)
- **Python** : [`python/utils.py`](python/utils.py)

### Code FreeFem++

```freefem
func real f(real x, real y) {
    real pi2_4 = pi*pi / 4.0;
    return pi2_4 * (sin(pi*x/2.0) + x*(x-4.0)*cos(pi*y/2.0)) - 2.0*cos(pi*y/2.0);
}

func real uD(real x, real y) {
    return 1.0;  // Sur x=0 et x=4
}
```

### Code Python

```python
def f_rhs(x, y):
    pi2_4 = np.pi**2 / 4.0
    sin_term = np.sin(np.pi * x / 2.0)
    cos_y_term = np.cos(np.pi * y / 2.0)
    return pi2_4 * (sin_term + x * (x - 4.0) * cos_y_term) - 2.0 * cos_y_term

def u_dirichlet(x, y):
    return 1.0
```

---

## Vérification Numérique

Pour vérifier l'exactitude des calculs, on peut :

1. **Calculer Δu numériquement** avec FreeFem++
2. **Comparer** avec -f(x,y)
3. **Erreur attendue** : proche de la précision machine (≈ 10⁻¹⁵)

Cette vérification est automatiquement effectuée lors de la résolution du problème variationnel.

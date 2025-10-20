# Documentation du Projet

## Génération de la Documentation

Ce projet utilise **Doxygen** pour générer automatiquement la documentation HTML à partir des commentaires Javadoc présents dans le code source.

### Prérequis

1. **Installer Doxygen** :
   - Télécharger depuis : https://www.doxygen.nl/download.html
   - Ajouter Doxygen au PATH Windows

2. **Vérifier l'installation** :
   ```powershell
   doxygen --version
   ```

### Génération de la Documentation

#### Méthode 1 : Script automatique (recommandé)
```powershell
.\generate_doc.bat
```
Ce script :
- Vérifie la présence de Doxygen
- Génère la documentation
- Ouvre automatiquement `index.html` dans le navigateur

#### Méthode 2 : Commande manuelle
```powershell
doxygen Doxyfile
```

### Consultation de la Documentation

Après génération, ouvrir dans un navigateur :
```
docs/doxygen/html/index.html
```

### Structure de la Documentation Générée

```
docs/doxygen/
├── html/
│   ├── index.html          # Page d'accueil
│   ├── annotated.html      # Liste des classes
│   ├── files.html          # Liste des fichiers
│   ├── functions.html      # Index des fonctions
│   └── ...
└── latex/                  # (désactivé par défaut)
```

### Contenu Documenté

La documentation inclut :

#### Classe `Img` (Singleton)
- **Constructeurs et destructeurs**
- **Méthodes publiques** :
  - `getInstance()` - Obtenir l'instance unique
  - `printPreview()` - Aperçu terminal coloré
  - `printROI()` - Affichage région d'intérêt

#### Opérateurs Spectraux
- `binaryzation()` - Seuillage binaire
- `negatif()` - Inversion des couleurs
- `quantification()` - Réduction des niveaux
- `rehaussement()` - Transformation affine
- `egalisationHistogramme()` - Égalisation adaptative

#### Opérateurs Morphologiques
- `erosion()` - Infimum local (min)
- `dilatation()` - Supremum local (max)
- `ouverture()` - Érosion + dilatation
- `fermeture()` - Dilatation + érosion

#### Filtres de Lissage
- `filtreMoyen()` - Moyenne arithmétique
- `filtreGaussien()` - Lissage pondéré gaussien
- `filtreMedian()` - Filtre de rang (médiane)
- `filtreBilateral()` - Préservation des contours

#### Filtres de Détection de Contours
- `filtreSobel()` - Gradient (masques de Sobel)
- `filtrePrewitt()` - Gradient (masques de Prewitt)
- `filtreCanny()` - Détection multi-étapes optimale

#### Fonctions Auxiliaires (`Operations.hpp`)
- `applyMorphologicalOperation()` - Template générique

### Configuration Doxygen

Le fichier `Doxyfile` contient :
- **Input** : `src/` et `include/`
- **Output** : `docs/doxygen/html/`
- **Langue** : Français
- **Extraction** : Toutes les fonctions (privées incluses)
- **Source browser** : Activé
- **Tree view** : Activé pour navigation hiérarchique

### Notes

- Les commentaires utilisent le style **Javadoc** : `/** ... */`
- Tags supportés : `@brief`, `@param`, `@return`, `@throws`, `@note`, `@see`, `@tparam`
- Les formules LaTeX sont supportées : `$formula$` ou `$$block$$`
- Références mathématiques du cours incluses dans la documentation

### Personnalisation

Pour modifier la configuration :
1. Éditer `Doxyfile`
2. Relancer `generate_doc.bat`

Exemples de personnalisation :
```doxyfile
# Changer la langue
OUTPUT_LANGUAGE = English

# Activer la génération LaTeX
GENERATE_LATEX = YES

# Utiliser Graphviz pour les diagrammes
HAVE_DOT = YES
DOT_PATH = "C:/Program Files/Graphviz/bin"
```

### Dépannage

**Problème** : `doxygen: command not found`
- **Solution** : Ajouter Doxygen au PATH système

**Problème** : Encodage incorrect des caractères français
- **Solution** : Vérifier que les fichiers source sont encodés en UTF-8

**Problème** : Documentation incomplète
- **Solution** : Vérifier les patterns dans `FILE_PATTERNS` du Doxyfile

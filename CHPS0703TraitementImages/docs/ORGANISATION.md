# Organisation du Projet - Resume

## Structure Finale

```
CHPS0703TraitementImages/
├── assets/              # Ressources et images de test
│   └── Img.jpg         # Image principale
│
├── bin/                 # Executables compiles (generes)
│   ├── Tp1             # Version Linux
│   ├── Tp1.exe         # Version Windows
│   ├── Tp1_debug.exe   # Version debug
│   └── test_unit.exe   # Tests unitaires
│
├── build/               # Fichiers intermediaires (generes)
│   └── *.o             # Fichiers objets
│
├── docs/                # Documentation
│   ├── ARCHITECTURE.md # Architecture technique detaillee
│   ├── QUICKSTART.md   # Guide de demarrage rapide
│   └── ORGANISATION.md # Ce fichier
│
├── include/             # Fichiers headers (.hpp)
│   ├── dog32.hpp       # Image chien 32x32 (test)
│   ├── image.hpp       # Buffers IMG, W, H
│   ├── menu.hpp        # Interface utilisateur CLI
│   └── Operations.hpp  # Templates operations morphologiques
│
├── src/                 # Code source (.cpp)
│   └── Tp1.cpp         # Programme principal + classe Img
│
├── .gitignore           # Fichiers a ignorer par Git
├── build.bat            # Script de compilation Windows
├── Makefile             # Script de compilation Make
└── README.md            # Documentation principale

```

## Objectifs de l'Organisation

### Separation des Responsabilites
- **Headers** separés du **code source**
- **Documentation** centralisee dans `docs/`
- **Ressources** isolees dans `assets/`
- **Binaires** generes dans `bin/` et `build/`

### Avantages

1. **Clarte**: Structure immediatement comprehensible
2. **Maintenabilite**: Fichiers faciles a localiser
3. **Compilation**: Chemins bien definis (`-Iinclude`)
4. **Versionning**: `.gitignore` exclut binaires et temporaires
5. **Scalabilite**: Facile d'ajouter nouveaux modules

### Conventions

#### Nommage
- **Dossiers**: minuscules, pluriel si collection (`docs/`, `assets/`)
- **Headers**: CamelCase avec `.hpp` (`Operations.hpp`)
- **Sources**: CamelCase avec `.cpp` (`Tp1.cpp`)
- **Executables**: minuscules (`tp1`, `test_unit`)

#### Organisation du Code
```cpp
// Dans src/Tp1.cpp
#include "../include/image.hpp"    // Chemin relatif
#include "../include/menu.hpp"
#include "../include/Operations.hpp"

// Le Makefile utilise -Iinclude donc pas besoin de ../
// Lors de la compilation manuelle, preciser le chemin
```

#### Compilation
```bash
# Avec Makefile (Linux/Mac/WSL)
make                    # Compile dans bin/
make run                # Execute depuis bin/

# Avec build.bat (Windows)
build.bat               # Compile dans bin/
build.bat run           # Execute depuis bin/
```

## Migration depuis l'Ancienne Structure

### Avant (structure plate)
```
CHPS0703TraitementImages/
├── dog32.hpp
├── image.hpp
├── Makefile
├── menu.hpp
├── Operations.hpp
├── Tp1.cpp
├── Tp1                 # executable
└── test_erosion        # executable
```

### Apres (structure hierarchique)
```
CHPS0703TraitementImages/
├── include/            # Tous les .hpp
├── src/                # Tous les .cpp
├── bin/                # Tous les executables
├── docs/               # Toute la documentation
└── assets/             # Toutes les ressources
```

### Modifications Appliquees

1. **Deplacement fichiers**
   - `*.hpp` → `include/`
   - `*.cpp` → `src/`
   - executables → `bin/`
   - `Img.jpg` → `assets/`

2. **Mise a jour includes**
   ```cpp
   // Ancien
   #include "image.hpp"
   
   // Nouveau
   #include "../include/image.hpp"
   ```

3. **Nouveau Makefile**
   - Variables `SRC_DIR`, `INC_DIR`, `BIN_DIR`
   - Flag `-Iinclude` pour chemins
   - Cibles creent dossiers automatiquement

4. **Script Windows**
   - `build.bat` pour compilation native
   - Commandes: build, debug, run, clean, help

5. **Documentation**
   - `README.md`: vue d'ensemble
   - `docs/ARCHITECTURE.md`: details techniques
   - `docs/QUICKSTART.md`: guide utilisateur
   - `docs/ORGANISATION.md`: ce fichier
   - `.gitignore`: exclusions Git

## Bonnes Pratiques

### Pour Ajouter un Nouveau Module

1. **Header** dans `include/nouveau_module.hpp`
2. **Source** dans `src/nouveau_module.cpp`
3. **Include** dans code: `#include "../include/nouveau_module.hpp"`
4. **Makefile**: ajouter a `HEADERS` et `SOURCES`

### Pour Ajouter des Tests

1. Creer `src/test_nouveau.cpp`
2. Compiler vers `bin/test_nouveau`
3. Lancer avec `build.bat test` (apres ajout au script)

### Pour la Documentation

- **Code**: Javadoc dans headers
- **Architecture**: `docs/ARCHITECTURE.md`
- **Tutoriels**: `docs/` avec noms explicites
- **README**: vue d'ensemble + liens vers docs/

## Commandes Utiles

```bash
# Voir structure
tree /F /A              # Windows
tree                    # Linux/Mac

# Compilation
build.bat               # Windows
make                    # Linux/Mac

# Nettoyage
build.bat clean         # Windows
make clean              # Linux/Mac

# Aide
build.bat help          # Windows
make help               # Linux/Mac
```

## Notes Importantes

- **Ne jamais commiter** `bin/` et `build/` (dans `.gitignore`)
- **Toujours compiler** dans `bin/`, pas a la racine
- **Documenter** tout ajout dans `docs/`
- **Respecter** les conventions de nommage

## Evolution Future

### Court Terme
- [ ] Ajouter tests unitaires dans `src/`
- [ ] Completer documentation dans `docs/`
- [ ] Ajouter plus d'images dans `assets/`

### Moyen Terme
- [ ] Separer classe Img dans `include/Img.hpp` et `src/Img.cpp`
- [ ] Creer module de filtres dans fichiers separes
- [ ] Implementer systeme de plugins

### Long Terme
- [ ] Migration vers CMake pour portabilite
- [ ] Integration CI/CD
- [ ] Interface graphique (dossier `ui/`)

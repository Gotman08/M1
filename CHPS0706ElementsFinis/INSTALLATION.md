# Guide d'Installation - Linux

## Installation Rapide

### 1. Prérequis

Assurez-vous que vous êtes sur un système Linux.

```bash
# Vérifier votre système
uname -a
# Devrait afficher "Linux"
```

### 2. Installation de FreeFem++

```bash
# Mise à jour des paquets
sudo apt-get update

# Installation de FreeFem++
sudo apt-get install -y freefem++

# Vérification
freefem++ -h
# ou
FreeFem++ -h
```

### 3. Installation de Python et Dépendances

```bash
# Python 3 (souvent déjà installé)
sudo apt-get install -y python3 python3-pip

# Bibliothèques Python nécessaires
pip3 install numpy matplotlib scipy

# Ou toutes ensemble
pip3 install numpy matplotlib scipy
```

### 4. Vérification de l'Installation

```bash
# Depuis le dossier du projet
cd /chemin/vers/CHPS0706ElementsFinis

# Exécuter le script de test
bash test_installation.sh
```

Si tout est vert (), vous êtes prêt !

## Installation Détaillée

### Option A : Installation Minimale

**Uniquement les outils essentiels** :

```bash
# FreeFem++
sudo apt-get update
sudo apt-get install -y freefem++

# Python minimal
sudo apt-get install -y python3 python3-pip

# Bibliothèques Python essentielles
pip3 install --user numpy matplotlib
```

### Option B : Installation Complète

**Avec tous les outils et dépendances** :

```bash
# Mise à jour complète
sudo apt-get update
sudo apt-get upgrade -y

# FreeFem++
sudo apt-get install -y freefem++

# Python et outils de développement
sudo apt-get install -y python3 python3-pip python3-dev

# Bibliothèques scientifiques Python
pip3 install --user numpy scipy matplotlib

# Outils optionnels
sudo apt-get install -y make git
```

### Option C : Environnement Virtuel Python (Recommandé)

**Pour isoler les dépendances Python** :

```bash
# Installation de venv
sudo apt-get install -y python3-venv

# Création d'un environnement virtuel
python3 -m venv venv

# Activation
source venv/bin/activate

# Installation des dépendances dans l'environnement
pip install numpy matplotlib scipy

# Pour désactiver l'environnement
# deactivate
```

## Résolution de Problèmes

### FreeFem++ non trouvé

**Symptôme** :
```
bash: FreeFem++: command not found
```

**Solutions** :

1. Vérifier l'installation :
   ```bash
   which freefem++
   which FreeFem++
   ```

2. Réinstaller si nécessaire :
   ```bash
   sudo apt-get remove freefem++
   sudo apt-get install freefem++
   ```

3. Vérifier les repositories :
   ```bash
   sudo apt-get update
   sudo apt-cache search freefem
   ```

### Erreurs de bibliothèques Python

**Symptôme** :
```
ModuleNotFoundError: No module named 'numpy'
```

**Solutions** :

1. Installer avec pip :
   ```bash
   pip3 install numpy matplotlib scipy
   ```

2. Installer avec apt (alternative) :
   ```bash
   sudo apt-get install python3-numpy python3-matplotlib python3-scipy
   ```

3. Vérifier l'installation :
   ```bash
   python3 -c "import numpy; print(numpy.__version__)"
   python3 -c "import matplotlib; print(matplotlib.__version__)"
   ```

### Erreurs de permissions

**Symptôme** :
```
Permission denied: ./main.py
```

**Solution** :
```bash
chmod +x main.py
chmod +x test_installation.sh
```

### Erreurs de chemins

**Symptôme** : Fichiers non trouvés

**Solutions** :

1. Utiliser des chemins absolus :
   ```bash
   pwd  # Afficher le répertoire courant
   cd /chemin/vers/CHPS0706ElementsFinis
   ```

2. Vérifier le répertoire de travail :
   ```bash
   cd ~
   cd CHPS0706ElementsFinis
   pwd
   ```

### Makefile : commande non trouvée

**Symptôme** :
```
make: command not found
```

**Solution** :
```bash
sudo apt-get install -y make
```

## Vérification Post-Installation

### Test Complet

```bash
# 1. Vérifier FreeFem++
FreeFem++ -h

# 2. Vérifier Python
python3 --version

# 3. Vérifier les bibliothèques
python3 -c "import numpy, matplotlib, scipy; print('OK')"

# 4. Tester la génération de maillages (rapide)
FreeFem++ generate_meshes.edp

# 5. Vérifier que les maillages sont générés
ls -lh meshes/

# 6. Test complet
bash test_installation.sh
```

### Nettoyage après Test

```bash
# Supprimer les fichiers de test
make clean

# Ou manuellement
rm -rf meshes/*.msh results/*
```

## Performances et Optimisations

### FreeFem++ avec Optimisations

Pour de meilleures performances, compiler FreeFem++ depuis les sources avec optimisations :

```bash
# Télécharger depuis https://freefem.org/
# Suivre les instructions de compilation

# Ou utiliser la version précompilée optimisée
```

### Python avec NumPy Optimisé

```bash
# Installer NumPy avec support MKL (Intel Math Kernel Library)
pip3 install numpy --config-settings=setup-args="-Dblas=mkl"
```

## Support et Documentation

### Liens Utiles

- **FreeFem++** : https://freefem.org/
- **Documentation FreeFem++** : https://doc.freefem.org/
- **NumPy** : https://numpy.org/
- **Matplotlib** : https://matplotlib.org/

### Commandes d'Aide

```bash
# Aide FreeFem++
FreeFem++ -h

# Aide Python
python3 --help

# Aide Make
make help

# Aide du projet
cat README.md
```

## Installation Alternative (Docker)

Si vous rencontrez des difficultés, vous pouvez utiliser Docker :

```dockerfile
# Dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    freefem++ \
    python3 \
    python3-pip \
    && pip3 install numpy matplotlib scipy

WORKDIR /app
COPY . /app

CMD ["bash"]
```

```bash
# Construction
docker build -t elementsfinis .

# Exécution
docker run -it -v $(pwd):/app elementsfinis
```

## Prochaines Étapes

Une fois l'installation terminée :

1. **Lire la documentation** : `cat README.md`
2. **Comprendre les calculs** : `cat EXERCICE1_CALCULS.md`
3. **Tester** : `bash test_installation.sh`
4. **Exécuter** : `python3 main.py` ou `make all`

Bon travail ! �

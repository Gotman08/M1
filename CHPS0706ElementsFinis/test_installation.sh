#!/bin/bash
# ============================================================================
# Script de Test de l'Installation
# ============================================================================
# Vérifie que tous les prérequis sont installés et que la structure est OK
# ============================================================================

echo ""
echo "════════════════════════════════════════════════════════════"
echo "TEST DE L'INSTALLATION - Éléments Finis P1"
echo "════════════════════════════════════════════════════════════"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SUCCESS=0
WARNINGS=0
ERRORS=0

# Test 1 : FreeFem++
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 1 : FreeFem++"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v FreeFem++ &> /dev/null; then
    echo -e "${GREEN}✓${NC} FreeFem++ trouvé (FreeFem++)"
    FreeFem++ -h | head -n 1
    ((SUCCESS++))
elif command -v freefem++ &> /dev/null; then
    echo -e "${GREEN}✓${NC} FreeFem++ trouvé (freefem++)"
    freefem++ -h | head -n 1
    ((SUCCESS++))
else
    echo -e "${RED}✗${NC} FreeFem++ non trouvé"
    echo "   Installation : sudo apt-get install freefem++"
    ((ERRORS++))
fi
echo ""

# Test 2 : Python
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 2 : Python 3"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓${NC} Python 3 trouvé"
    python3 --version
    ((SUCCESS++))
else
    echo -e "${RED}✗${NC} Python 3 non trouvé"
    echo "   Installation : sudo apt-get install python3"
    ((ERRORS++))
fi
echo ""

# Test 3 : Bibliothèques Python
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 3 : Bibliothèques Python"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# NumPy
if python3 -c "import numpy" 2>/dev/null; then
    VERSION=$(python3 -c "import numpy; print(numpy.__version__)")
    echo -e "${GREEN}✓${NC} NumPy $VERSION"
    ((SUCCESS++))
else
    echo -e "${RED}✗${NC} NumPy non trouvé"
    echo "   Installation : pip3 install numpy"
    ((ERRORS++))
fi

# Matplotlib
if python3 -c "import matplotlib" 2>/dev/null; then
    VERSION=$(python3 -c "import matplotlib; print(matplotlib.__version__)")
    echo -e "${GREEN}✓${NC} Matplotlib $VERSION"
    ((SUCCESS++))
else
    echo -e "${RED}✗${NC} Matplotlib non trouvé"
    echo "   Installation : pip3 install matplotlib"
    ((ERRORS++))
fi

# SciPy (optionnel)
if python3 -c "import scipy" 2>/dev/null; then
    VERSION=$(python3 -c "import scipy; print(scipy.__version__)")
    echo -e "${GREEN}✓${NC} SciPy $VERSION"
    ((SUCCESS++))
else
    echo -e "${YELLOW}⚠${NC} SciPy non trouvé (optionnel)"
    echo "   Installation : pip3 install scipy"
    ((WARNINGS++))
fi
echo ""

# Test 4 : Structure des fichiers
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 4 : Structure des Fichiers"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

FILES=(
    "generate_meshes.edp"
    "main.py"
    "Makefile"
    "README.md"
    "freefem/validation.edp"
    "freefem/validation_pen.edp"
    "python/utils.py"
    "python/mesh_analysis.py"
    "python/convergence_analysis.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
        ((SUCCESS++))
    else
        echo -e "${RED}✗${NC} $file manquant"
        ((ERRORS++))
    fi
done
echo ""

# Test 5 : Dossiers
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 5 : Dossiers"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

DIRS=(
    "meshes"
    "freefem"
    "python"
    "results"
)

for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $dir/"
        ((SUCCESS++))
    else
        echo -e "${RED}✗${NC} $dir/ manquant"
        ((ERRORS++))
    fi
done
echo ""

# Test 6 : Permissions
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 6 : Permissions"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -x "main.py" ]; then
    echo -e "${GREEN}✓${NC} main.py est exécutable"
    ((SUCCESS++))
else
    echo -e "${YELLOW}⚠${NC} main.py n'est pas exécutable"
    echo "   Correction : chmod +x main.py"
    ((WARNINGS++))
fi
echo ""

# Test 7 : Syntaxe Python
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 7 : Syntaxe Python"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

PYTHON_FILES=(
    "python/utils.py"
    "python/mesh_analysis.py"
    "python/convergence_analysis.py"
    "main.py"
)

for file in "${PYTHON_FILES[@]}"; do
    if python3 -m py_compile "$file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $file (syntaxe OK)"
        ((SUCCESS++))
    else
        echo -e "${RED}✗${NC} $file (erreur de syntaxe)"
        ((ERRORS++))
    fi
done
echo ""

# Résumé
echo "════════════════════════════════════════════════════════════"
echo "RÉSUMÉ DES TESTS"
echo "════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}Succès    : $SUCCESS${NC}"
echo -e "${YELLOW}Avertissements : $WARNINGS${NC}"
echo -e "${RED}Erreurs   : $ERRORS${NC}"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo "════════════════════════════════════════════════════════════"
    echo -e "${GREEN}✓ INSTALLATION COMPLÈTE ET PRÊTE${NC}"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "Prochaines étapes :"
    echo "  1. Générer les maillages    : make meshes"
    echo "  2. Exécution complète       : make all"
    echo "  3. Ou avec Python           : python3 main.py"
    echo ""
    exit 0
else
    echo "════════════════════════════════════════════════════════════"
    echo -e "${RED}✗ INSTALLATION INCOMPLÈTE${NC}"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "Veuillez corriger les erreurs ci-dessus avant de continuer."
    echo ""
    exit 1
fi

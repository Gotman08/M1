# ============================================================================
# Makefile - Étude de Convergence Éléments Finis P1
# ============================================================================
# Compatible WSL (Windows Subsystem for Linux)
# ============================================================================

# Compilateurs et commandes
PYTHON := python3
FREEFEM := FreeFem++

# Vérifier si freefem++ (minuscule) est disponible
ifeq ($(shell which freefem++ 2>/dev/null),)
    FREEFEM := FreeFem++
else
    FREEFEM := freefem++
endif

# Répertoires
MESH_DIR := meshes
FREEFEM_DIR := freefem
PYTHON_DIR := python
RESULTS_DIR := results

# Fichiers
MESH_SCRIPT := generate_meshes.edp
MESHES := $(MESH_DIR)/m1.msh $(MESH_DIR)/m2.msh $(MESH_DIR)/m3.msh $(MESH_DIR)/m4.msh

VALIDATION_SCRIPT := $(FREEFEM_DIR)/validation.edp
VALIDATION_PEN_SCRIPT := $(FREEFEM_DIR)/validation_pen.edp

MESH_ANALYSIS := $(PYTHON_DIR)/mesh_analysis.py
CONVERGENCE_ANALYSIS := $(PYTHON_DIR)/convergence_analysis.py
MAIN_SCRIPT := main.py

# Cibles
.PHONY: all clean help meshes solve analyze convergence test install-deps view-results

# Cible par défaut
all: convergence
	@echo ""
	@echo "════════════════════════════════════════════════════════════"
	@echo "✓ Étude de convergence terminée avec succès"
	@echo "════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Fichiers générés :"
	@echo "  - Maillages        : $(MESH_DIR)/"
	@echo "  - Résultats        : $(RESULTS_DIR)/"
	@echo "  - Tableau          : $(RESULTS_DIR)/convergence_table_standard.txt"
	@echo "  - Graphique        : $(RESULTS_DIR)/convergence_plot_standard.png"
	@echo ""

# Aide
help:
	@echo "════════════════════════════════════════════════════════════"
	@echo "Makefile - Étude de Convergence Éléments Finis P1"
	@echo "════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Cibles disponibles :"
	@echo ""
	@echo "  make all           - Exécution complète (défaut)"
	@echo "  make meshes        - Générer les 4 maillages"
	@echo "  make analyze       - Analyser les maillages (qualité Q et pas h)"
	@echo "  make solve         - Résoudre avec FreeFem++ (standard)"
	@echo "  make solve-pen     - Résoudre avec pénalisation"
	@echo "  make convergence   - Analyse de convergence complète"
	@echo "  make test          - Tests rapides"
	@echo "  make view-results  - Afficher les résultats"
	@echo "  make clean         - Nettoyer les fichiers générés"
	@echo "  make install-deps  - Installer les dépendances Python"
	@echo "  make help          - Afficher cette aide"
	@echo ""
	@echo "Exemples :"
	@echo "  make              # Tout exécuter"
	@echo "  make meshes       # Générer uniquement les maillages"
	@echo "  make clean all    # Nettoyer puis tout refaire"
	@echo ""

# Installation des dépendances Python
install-deps:
	@echo "Installation des dépendances Python..."
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install numpy matplotlib scipy
	@echo "✓ Dépendances installées"

# Vérification de FreeFem++
check-freefem:
	@echo "Vérification de FreeFem++..."
	@which $(FREEFEM) > /dev/null || (echo "✗ FreeFem++ non trouvé. Installez-le avec : sudo apt-get install freefem++" && exit 1)
	@echo "✓ FreeFem++ trouvé : $(shell which $(FREEFEM))"

# Génération des maillages
meshes: check-freefem $(MESH_DIR)
	@echo ""
	@echo "[1/4] Génération des maillages..."
	@echo "════════════════════════════════════════════════════════════"
	$(FREEFEM) $(MESH_SCRIPT)
	@echo "✓ Maillages générés"

$(MESH_DIR):
	@mkdir -p $(MESH_DIR)

# Analyse des maillages
analyze: meshes $(RESULTS_DIR)
	@echo ""
	@echo "[2/4] Analyse des maillages (Exercice 2)..."
	@echo "════════════════════════════════════════════════════════════"
	$(PYTHON) $(MESH_ANALYSIS)
	@echo "✓ Analyse terminée"

$(RESULTS_DIR):
	@mkdir -p $(RESULTS_DIR)

# Résolution avec FreeFem++ (standard)
solve: analyze check-freefem
	@echo ""
	@echo "[3/4] Résolution FreeFem++ (Exercice 3.1 - Standard)..."
	@echo "════════════════════════════════════════════════════════════"
	@for mesh in $(MESHES); do \
		if [ -f $$mesh ]; then \
			echo "Traitement de $$mesh..."; \
			$(FREEFEM) $(VALIDATION_SCRIPT) $$mesh; \
		fi; \
	done
	@echo "✓ Résolution terminée"

# Résolution avec pénalisation
solve-pen: analyze check-freefem
	@echo ""
	@echo "[3b/4] Résolution FreeFem++ (Exercice 3.2 - Pénalisation)..."
	@echo "════════════════════════════════════════════════════════════"
	@for mesh in $(MESHES); do \
		if [ -f $$mesh ]; then \
			echo "Traitement de $$mesh..."; \
			$(FREEFEM) $(VALIDATION_PEN_SCRIPT) $$mesh; \
		fi; \
	done
	@echo "✓ Résolution avec pénalisation terminée"

# Analyse de convergence
convergence: solve
	@echo ""
	@echo "[4/4] Analyse de convergence (Exercice 4)..."
	@echo "════════════════════════════════════════════════════════════"
	$(PYTHON) $(MAIN_SCRIPT) --only-analysis
	@echo "✓ Analyse de convergence terminée"

# Tout avec pénalisation
all-with-pen: convergence solve-pen
	@echo ""
	@echo "Analyse de convergence (pénalisation)..."
	$(PYTHON) $(CONVERGENCE_ANALYSIS)

# Afficher les résultats
view-results:
	@echo ""
	@echo "════════════════════════════════════════════════════════════"
	@echo "RÉSULTATS DE L'ÉTUDE DE CONVERGENCE"
	@echo "════════════════════════════════════════════════════════════"
	@if [ -f $(RESULTS_DIR)/convergence_table_standard.txt ]; then \
		cat $(RESULTS_DIR)/convergence_table_standard.txt; \
	else \
		echo "✗ Fichier de résultats non trouvé. Exécutez 'make all' d'abord."; \
	fi
	@echo ""

# Tests rapides
test: check-freefem
	@echo ""
	@echo "Tests rapides..."
	@echo "════════════════════════════════════════════════════════════"
	@echo "Test 1 : Vérification de FreeFem++"
	@$(FREEFEM) -h > /dev/null && echo "  ✓ FreeFem++ OK" || echo "  ✗ FreeFem++ KO"
	@echo ""
	@echo "Test 2 : Vérification de Python"
	@$(PYTHON) --version && echo "  ✓ Python OK" || echo "  ✗ Python KO"
	@echo ""
	@echo "Test 3 : Imports Python"
	@$(PYTHON) -c "import numpy, matplotlib.pyplot" && echo "  ✓ Bibliothèques OK" || echo "  ✗ Bibliothèques manquantes (make install-deps)"
	@echo ""
	@echo "Test 4 : Structure des fichiers"
	@[ -f $(MESH_SCRIPT) ] && echo "  ✓ $(MESH_SCRIPT)" || echo "  ✗ $(MESH_SCRIPT) manquant"
	@[ -f $(VALIDATION_SCRIPT) ] && echo "  ✓ $(VALIDATION_SCRIPT)" || echo "  ✗ $(VALIDATION_SCRIPT) manquant"
	@[ -f $(MAIN_SCRIPT) ] && echo "  ✓ $(MAIN_SCRIPT)" || echo "  ✗ $(MAIN_SCRIPT) manquant"
	@echo "════════════════════════════════════════════════════════════"

# Nettoyage
clean:
	@echo "Nettoyage des fichiers générés..."
	rm -rf $(MESH_DIR)/*.msh
	rm -rf $(RESULTS_DIR)/*
	@echo "✓ Nettoyage terminé"

# Nettoyage complet (y compris les dossiers)
clean-all: clean
	rm -rf $(MESH_DIR) $(RESULTS_DIR)
	@echo "✓ Nettoyage complet terminé"

# Exécution rapide avec Python
quick:
	@echo "Exécution rapide avec le script principal..."
	$(PYTHON) $(MAIN_SCRIPT)

# Exécution complète avec pénalisation
full:
	@echo "Exécution complète (standard + pénalisation)..."
	$(PYTHON) $(MAIN_SCRIPT) --penalization

# ============================================================================
# Makefile - Étude de Convergence Éléments Finis P1
# ============================================================================
# Linux Makefile
# ============================================================================

# Compilateurs et commandes
PYTHON := python3
FREEFEM := FreeFem++
FREEFEM_FLAGS := -nw

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
.PHONY: all full clean help meshes solve solve-pen analyze convergence report test install-deps install-deps-full view-results

# Cible par défaut - Exécution complète avec PDF
all: full

# Exécution complète avec génération du rapport PDF
full: convergence report
	@echo ""
	@echo "════════════════════════════════════════════════════════════"
	@echo "✓ Étude de convergence terminée avec succès"
	@echo "════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Fichiers générés :"
	@echo "  - Maillages        : $(MESH_DIR)/"
	@echo "  - Résultats        : $(RESULTS_DIR)/"
	@echo "  - Tableau standard : $(RESULTS_DIR)/convergence_table_standard.txt"
	@echo "  - Tableau pénal.   : $(RESULTS_DIR)/convergence_table_penalized.txt"
	@echo "  - Graphique std    : $(RESULTS_DIR)/convergence_plot_standard.png"
	@echo "  - Graphique pénal. : $(RESULTS_DIR)/convergence_plot_penalized.png"
	@echo "  - Rapport PDF      : $(RESULTS_DIR)/RAPPORT_CONVERGENCE.pdf"
	@echo ""

# Aide
help:
	@echo "════════════════════════════════════════════════════════════"
	@echo "Makefile - Étude de Convergence Éléments Finis P1"
	@echo "════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Cibles disponibles :"
	@echo ""
	@echo "  make all               - Exécution complète avec PDF (défaut)"
	@echo "  make full              - Alias pour 'make all'"
	@echo "  make meshes            - Générer les 4 maillages"
	@echo "  make analyze           - Analyser les maillages (qualité Q et pas h)"
	@echo "  make solve             - Résoudre avec FreeFem++ (standard)"
	@echo "  make solve-pen         - Résoudre avec pénalisation"
	@echo "  make convergence       - Analyse de convergence (2 méthodes)"
	@echo "  make report            - Générer uniquement le PDF"
	@echo "  make test              - Tests rapides"
	@echo "  make view-results      - Afficher les résultats"
	@echo "  make clean             - Nettoyer les fichiers générés"
	@echo "  make install-deps      - Installer dépendances de base"
	@echo "  make install-deps-full - Installer toutes dépendances (avec PDF)"
	@echo "  make help              - Afficher cette aide"
	@echo ""
	@echo "Exemples :"
	@echo "  make              # Tout exécuter"
	@echo "  make meshes       # Générer uniquement les maillages"
	@echo "  make clean all    # Nettoyer puis tout refaire"
	@echo ""

# Installation des dépendances Python (de base)
install-deps:
	@echo "Installation des dépendances Python (de base)..."
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install numpy matplotlib scipy
	@echo "✓ Dépendances de base installées"

# Installation complète avec dépendances PDF
install-deps-full:
	@echo "Installation complète des dépendances Python (avec PDF)..."
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	@echo "✓ Toutes les dépendances installées (incluant reportlab, Pillow, pygments)"

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
	$(FREEFEM) $(MESH_SCRIPT) $(FREEFEM_FLAGS)
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
			$(FREEFEM) $(VALIDATION_SCRIPT) $$mesh $(FREEFEM_FLAGS); \
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
			$(FREEFEM) $(VALIDATION_PEN_SCRIPT) $$mesh $(FREEFEM_FLAGS); \
		fi; \
	done
	@echo "✓ Résolution avec pénalisation terminée"

# Analyse de convergence - LES 2 MÉTHODES
convergence: solve solve-pen
	@echo ""
	@echo "[4/5] Analyse de convergence (Exercice 4)..."
	@echo "════════════════════════════════════════════════════════════"
	$(PYTHON) $(MAIN_SCRIPT) --only-analysis
	@echo "✓ Analyse de convergence terminée"

# Génération du rapport PDF
report:
	@echo ""
	@echo "[5/5] Génération du rapport PDF..."
	@echo "════════════════════════════════════════════════════════════"
	$(PYTHON) generate_report.py
	@echo "✓ Rapport PDF généré"

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

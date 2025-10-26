# Makefile - Système de Traitement d'Images (Architecture POO)
# ==============================================================

# Détection OS
ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
    RM := del /Q
    RMDIR := rmdir /S /Q
    MKDIR := if not exist
    MKDIR_END := mkdir
    FIXPATH = $(subst /,\,$1)
    EXE_EXT := .exe
    RUN_PREFIX :=
    BROWSER := cmd.exe /c start
else
    DETECTED_OS := $(shell uname -s)
    RM := rm -f
    RMDIR := rm -rf
    MKDIR := mkdir -p
    MKDIR_END :=
    FIXPATH = $1
    EXE_EXT :=
    RUN_PREFIX := ./
    ifeq ($(shell command -v explorer.exe 2>/dev/null),)
        ifeq ($(DETECTED_OS),Darwin)
            BROWSER := open
        else
            BROWSER := xdg-open
        endif
    else
        BROWSER := explorer.exe
    endif
endif

# Compilateur et options
CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2
DEBUGFLAGS = -g -O0 -DDEBUG

# Dossiers
SRC_DIR = src
INC_DIR = include
BUILD_DIR = build
BIN_DIR = bin
DOCS_DIR = docs
TESTS_DIR = tests

# Fichiers source (architecture POO)
SRC_FILES = $(SRC_DIR)/main.cpp
HEADERS = $(INC_DIR)/ImageProcessing.hpp \
          $(INC_DIR)/core/*.hpp \
          $(INC_DIR)/utils/*.hpp \
          $(INC_DIR)/filters/*.hpp \
          $(INC_DIR)/operations/*.hpp \
          $(INC_DIR)/display/*.hpp \
          $(INC_DIR)/ui/*.hpp
INCLUDES = -I$(INC_DIR)

# Cibles
TARGET = $(BIN_DIR)/image_processor$(EXE_EXT)
TARGET_DEBUG = $(BIN_DIR)/image_processor_debug$(EXE_EXT)

.PHONY: all clean clean-all debug run test help dirs doc doc-rebuild

# Cible par défaut
all: dirs $(TARGET)

# Création des dossiers nécessaires
dirs:
ifeq ($(DETECTED_OS),Windows)
	@$(MKDIR) "$(call FIXPATH,$(BIN_DIR))" $(MKDIR_END)
	@$(MKDIR) "$(call FIXPATH,$(BUILD_DIR))" $(MKDIR_END)
else
	@$(MKDIR) $(BIN_DIR)
	@$(MKDIR) $(BUILD_DIR)
endif

# Compilation version release
$(TARGET): $(SRC_FILES) $(HEADERS) | dirs
	@echo "Compilation version release..."
	$(CXX) $(CXXFLAGS) $(INCLUDES) $(SRC_FILES) -o $(TARGET)
	@echo "Compilation reussie: $(TARGET)"

# Compilation version debug
debug: CXXFLAGS += $(DEBUGFLAGS)
debug: dirs $(TARGET_DEBUG)

$(TARGET_DEBUG): $(SRC_FILES) $(HEADERS) | dirs
	@echo "Compilation version debug..."
	$(CXX) $(CXXFLAGS) $(INCLUDES) $(SRC_FILES) -o $(TARGET_DEBUG)
	@echo "Compilation reussie: $(TARGET_DEBUG)"

# Exécution
run: $(TARGET)
	@echo "Execution du programme..."
	@cd $(BIN_DIR) && $(RUN_PREFIX)image_processor$(EXE_EXT)

# Tests
test:
	@echo "Execution des tests..."
ifeq ($(DETECTED_OS),Windows)
	@if exist "$(TESTS_DIR)\test_image.cpp" ( \
		$(CXX) $(CXXFLAGS) $(INCLUDES) $(TESTS_DIR)/test_image.cpp -o $(BIN_DIR)/test_image$(EXE_EXT) && \
		cd $(BIN_DIR) && $(RUN_PREFIX)test_image$(EXE_EXT) \
	) else ( \
		echo "Aucun test disponible" \
	)
else
	@if [ -f "$(TESTS_DIR)/test_image.cpp" ]; then \
		$(CXX) $(CXXFLAGS) $(INCLUDES) $(TESTS_DIR)/test_image.cpp -o $(BIN_DIR)/test_image$(EXE_EXT); \
		cd $(BIN_DIR) && $(RUN_PREFIX)test_image$(EXE_EXT); \
	else \
		echo "Aucun test disponible"; \
	fi
endif

# Documentation Doxygen
doc:
	@echo "Generation documentation..."
ifeq ($(DETECTED_OS),Windows)
	@if not exist "$(DOCS_DIR)\doxygen\html" ( \
		doxygen Doxyfile \
	) else ( \
		echo Documentation existe deja (utilisez: make doc-rebuild) \
	)
	@if exist "$(DOCS_DIR)\doxygen\html\index.html" ( \
		$(BROWSER) $(DOCS_DIR)\doxygen\html\index.html \
	)
else
	@if [ ! -d "$(DOCS_DIR)/doxygen/html" ]; then \
		doxygen Doxyfile; \
	else \
		echo "Documentation existe deja (utilisez: make doc-rebuild)"; \
	fi
	@if [ -f "$(DOCS_DIR)/doxygen/html/index.html" ]; then \
		$(BROWSER) $(DOCS_DIR)/doxygen/html/index.html 2>/dev/null || \
		echo "Documentation disponible: $(DOCS_DIR)/doxygen/html/index.html"; \
	fi
endif

doc-rebuild:
	@echo "Regeneration documentation..."
ifeq ($(DETECTED_OS),Windows)
	@if exist "$(DOCS_DIR)\doxygen" $(RMDIR) "$(DOCS_DIR)\doxygen" 2>nul
	@doxygen Doxyfile
	@$(BROWSER) $(DOCS_DIR)\doxygen\html\index.html
else
	@$(RMDIR) $(DOCS_DIR)/doxygen 2>/dev/null || true
	@doxygen Doxyfile
	@$(BROWSER) $(DOCS_DIR)/doxygen/html/index.html 2>/dev/null || \
		echo "Documentation generee: $(DOCS_DIR)/doxygen/html/index.html"
endif

# Nettoyage
clean:
	@echo "Nettoyage executables et objets..."
ifeq ($(DETECTED_OS),Windows)
	@if exist "$(call FIXPATH,$(BIN_DIR))\*" $(RM) "$(call FIXPATH,$(BIN_DIR))\*" 2>nul
	@if exist "$(call FIXPATH,$(BUILD_DIR))\*.o" $(RM) "$(call FIXPATH,$(BUILD_DIR))\*.o" 2>nul
	@if exist "*.o" $(RM) *.o 2>nul
	@if exist "*.exe" $(RM) *.exe 2>nul
else
	-@$(RM) $(BIN_DIR)/* 2>/dev/null
	-@$(RM) $(BUILD_DIR)/*.o 2>/dev/null
	-@$(RM) *.o *.exe 2>/dev/null
endif
	@echo "Nettoyage termine"

clean-all: clean
	@echo "Nettoyage complet..."
ifeq ($(DETECTED_OS),Windows)
	@if exist "$(DOCS_DIR)\doxygen" $(RMDIR) "$(DOCS_DIR)\doxygen" 2>nul
	@if exist "*.tga" $(RM) *.tga 2>nul
	@if exist "*.TGA" $(RM) *.TGA 2>nul
else
	@$(RMDIR) $(DOCS_DIR)/doxygen 2>/dev/null || true
	@$(RM) *.tga *.TGA 2>/dev/null || true
endif
	@echo "Nettoyage complet termine"

# Aide
help:
	@echo "=========================================="
	@echo "  Systeme de Traitement d'Images (POO)  "
	@echo "=========================================="
	@echo ""
	@echo "OS detecte: $(DETECTED_OS)"
	@echo ""
	@echo "Commandes disponibles:"
	@echo "  make             - Compile le programme (version release)"
	@echo "  make run         - Compile et execute le programme"
	@echo "  make debug       - Compile en mode debug"
	@echo "  make test        - Execute les tests unitaires"
	@echo "  make doc         - Genere la documentation Doxygen"
	@echo "  make doc-rebuild - Regenere la documentation (force)"
	@echo "  make clean       - Nettoie executables et fichiers objets"
	@echo "  make clean-all   - Nettoie tout (doc, images, etc.)"
	@echo "  make help        - Affiche cette aide"
	@echo ""
	@echo "Structure du projet:"
	@echo "  src/             - Code source (.cpp)"
	@echo "  include/         - Fichiers d'en-tete (.hpp)"
	@echo "  bin/             - Executables compiles"
	@echo "  docs/            - Documentation"
	@echo "  tests/           - Tests unitaires"
	@echo "  archive/         - Ancien code (reference)"
	@echo ""
	@echo "Pour plus d'informations, consultez: docs/README_REFACTORING.md"
	@echo ""

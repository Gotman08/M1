# Makefile - Traitement d'Images
# ================================

# Detection OS
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

# Compilateur
CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2
DEBUGFLAGS = -g -O0 -DDEBUG

# Dossiers
SRC_DIR = src
INC_DIR = include
BUILD_DIR = build
BIN_DIR = bin

# Fichiers
SRC_FILES = $(SRC_DIR)/Tp1.cpp
TEST_FILES = $(SRC_DIR)/test.cpp
HEADERS = $(INC_DIR)/image.hpp $(INC_DIR)/dog32.hpp $(INC_DIR)/menu.hpp $(INC_DIR)/Operations.hpp
INCLUDES = -I$(INC_DIR)

# Cibles
TARGET = $(BIN_DIR)/Tp1$(EXE_EXT)
TARGET_DEBUG = $(BIN_DIR)/Tp1_debug$(EXE_EXT)
TARGET_TEST = $(BIN_DIR)/test_unit$(EXE_EXT)

.PHONY: all clean clean-all debug run test help dirs valgrind memcheck doc doc-rebuild

all: dirs $(TARGET)

dirs:
ifeq ($(DETECTED_OS),Windows)
	@$(MKDIR) "$(call FIXPATH,$(BIN_DIR))" $(MKDIR_END)
	@$(MKDIR) "$(call FIXPATH,$(BUILD_DIR))" $(MKDIR_END)
else
	@$(MKDIR) $(BIN_DIR) $(MKDIR_END)
	@$(MKDIR) $(BUILD_DIR) $(MKDIR_END)
endif

$(TARGET): $(SRC_FILES) $(HEADERS) | dirs
	$(CXX) $(CXXFLAGS) $(INCLUDES) $(SRC_FILES) -o $(TARGET)

debug: CXXFLAGS += $(DEBUGFLAGS)
debug: dirs $(TARGET_DEBUG)

$(TARGET_DEBUG): $(SRC_FILES) $(HEADERS) | dirs
	$(CXX) $(CXXFLAGS) $(INCLUDES) $(SRC_FILES) -o $(TARGET_DEBUG)

run: $(TARGET)
	@cd $(BIN_DIR) && $(RUN_PREFIX)Tp1$(EXE_EXT)

test: $(TARGET_TEST)
	@echo "execution tests..."
	@cd $(BIN_DIR) && $(RUN_PREFIX)test_unit$(EXE_EXT)

$(TARGET_TEST): $(TEST_FILES) $(HEADERS) | dirs
	$(CXX) $(CXXFLAGS) $(INCLUDES) $(TEST_FILES) -o $(TARGET_TEST)

valgrind: debug
ifeq ($(DETECTED_OS),Windows)
	@echo "valgrind non disponible sur windows"
	@echo "utilisez: make memcheck ou wsl"
else
	valgrind --leak-check=full --show-leak-kinds=all $(RUN_PREFIX)$(TARGET_DEBUG)
endif

memcheck: debug
	@echo "verification memoire..."
ifeq ($(DETECTED_OS),Windows)
	@echo "drmemory non implemente"
	@echo "utilisez wsl ou installez drmemory"
else
	@if command -v valgrind >/dev/null 2>&1; then \
		valgrind --leak-check=full $(RUN_PREFIX)$(TARGET_DEBUG); \
	else \
		echo "valgrind non installe"; \
		echo "installez: sudo apt-get install valgrind"; \
	fi
endif

doc:
	@echo "generation documentation..."
ifeq ($(DETECTED_OS),Windows)
	@if not exist "docs\doxygen\html" ( \
		doxygen Doxyfile \
	) else ( \
		echo doc existe deja (utilisez: make doc-rebuild) \
	)
	@echo "ouverture documentation..."
	@if exist "docs\doxygen\html\index.html" ( \
		$(BROWSER) docs\doxygen\html\index.html \
	) else ( \
		echo erreur: doc non trouvee \
	)
else
	@if [ ! -d "docs/doxygen/html" ]; then \
		doxygen Doxyfile; \
	else \
		echo "doc existe deja (utilisez: make doc-rebuild)"; \
	fi
	@echo "ouverture documentation..."
	@if [ -f "docs/doxygen/html/index.html" ]; then \
		$(BROWSER) docs/doxygen/html/index.html 2>/dev/null || \
		echo "doc disponible: docs/doxygen/html/index.html"; \
	else \
		echo "erreur: doc non trouvee"; \
	fi
endif

doc-rebuild:
	@echo "regeneration documentation..."
ifeq ($(DETECTED_OS),Windows)
	@if exist "docs\doxygen" $(RMDIR) "docs\doxygen" 2>nul
	@doxygen Doxyfile
	@echo "ouverture documentation..."
	@$(BROWSER) docs\doxygen\html\index.html
else
	@$(RMDIR) docs/doxygen 2>/dev/null || true
	@doxygen Doxyfile
	@echo "ouverture documentation..."
	@$(BROWSER) docs/doxygen/html/index.html 2>/dev/null || \
		echo "doc generee: docs/doxygen/html/index.html"
endif

clean:
	@echo "nettoyage executables et objets..."
ifeq ($(DETECTED_OS),Windows)
	@if exist "$(call FIXPATH,$(BIN_DIR))\*" $(RM) "$(call FIXPATH,$(BIN_DIR))\*" 2>nul
	@if exist "$(call FIXPATH,$(BUILD_DIR))\*.o" $(RM) "$(call FIXPATH,$(BUILD_DIR))\*.o" 2>nul
	@if exist "*.o" $(RM) *.o 2>nul
	@if exist "*.exe" $(RM) *.exe 2>nul
else
	@$(RM) $(BIN_DIR)/* $(BUILD_DIR)/*.o *.o *.exe 2>/dev/null || true
endif
	@echo "nettoye"

clean-all: clean
	@echo "nettoyage complet..."
ifeq ($(DETECTED_OS),Windows)
	@if exist "docs\doxygen" $(RMDIR) "docs\doxygen" 2>nul
	@if exist "*.tga" $(RM) *.tga 2>nul
	@if exist "*.TGA" $(RM) *.TGA 2>nul
else
	@$(RMDIR) docs/doxygen 2>/dev/null || true
	@$(RM) *.tga *.TGA 2>/dev/null || true
endif
	@echo "nettoyage complet termine"

help:
	@echo "Makefile - Traitement d'Images"
	@echo "================================"
	@echo ""
	@echo "OS detecte: $(DETECTED_OS)"
	@echo ""
	@echo "Cibles disponibles:"
	@echo "  make             - compile version release"
	@echo "  make debug       - compile version debug"
	@echo "  make run         - compile et execute"
	@echo "  make test        - execute tests unitaires"
	@echo "  make doc         - ouvre doc (genere si necessaire)"
	@echo "  make doc-rebuild - force regeneration documentation"
	@echo "  make valgrind    - analyse memoire (valgrind)"
	@echo "  make clean       - nettoie executables et objets"
	@echo "  make clean-all   - nettoie tout (doc, images, etc)"
	@echo "  make help        - affiche aide"

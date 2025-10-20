# Makefile - Traitement d'ImagesCXX = g++

# ================================CXXFLAGS = -std=c++17 -Wall -Wextra -O2

DEBUGFLAGS = -g -O0 -DDEBUG

CXX = g++

CXXFLAGS = -std=c++17 -Wall -Wextra -O2TARGET = Tp1

DEBUGFLAGS = -g -O0 -DDEBUGTARGET_DEBUG = Tp1_debug

TARGET_TEST = test_unit

# Dossiers

SRC_DIR = srcSOURCES = Tp1.cpp

INC_DIR = includeTEST_SOURCES = test.cpp

BUILD_DIR = buildOBJECTS = $(SOURCES:.cpp=.o)

BIN_DIR = binHEADERS = image.hpp dog32.hpp menu.hpp Operations.hpp



# Fichiers.PHONY: all clean debug run valgrind memcheck test help

TARGET = $(BIN_DIR)/Tp1

TARGET_DEBUG = $(BIN_DIR)/Tp1_debugall: $(TARGET)

TARGET_TEST = $(BIN_DIR)/test_unit

$(TARGET): $(SOURCES) $(HEADERS)

SOURCES = $(SRC_DIR)/Tp1.cpp	$(CXX) $(CXXFLAGS) $(SOURCES) -o $(TARGET)

HEADERS = $(INC_DIR)/image.hpp $(INC_DIR)/dog32.hpp $(INC_DIR)/menu.hpp $(INC_DIR)/Operations.hpp

debug: CXXFLAGS += $(DEBUGFLAGS)

INCLUDES = -I$(INC_DIR)debug: $(TARGET_DEBUG)



.PHONY: all clean debug run test help dirs$(TARGET_DEBUG): $(SOURCES) $(HEADERS)

	$(CXX) $(CXXFLAGS) $(SOURCES) -o $(TARGET_DEBUG)

all: dirs $(TARGET)

run: $(TARGET)

dirs:	./$(TARGET)

	@if not exist "$(BIN_DIR)" mkdir "$(BIN_DIR)"

	@if not exist "$(BUILD_DIR)" mkdir "$(BUILD_DIR)"test: $(TARGET_TEST)

	@echo "execution tests..."

$(TARGET): $(SOURCES) $(HEADERS) | dirs	./$(TARGET_TEST)

	$(CXX) $(CXXFLAGS) $(INCLUDES) $(SOURCES) -o $(TARGET)

$(TARGET_TEST): $(TEST_SOURCES) $(HEADERS)

debug: CXXFLAGS += $(DEBUGFLAGS)	$(CXX) $(CXXFLAGS) $(TEST_SOURCES) -o $(TARGET_TEST)

debug: dirs $(TARGET_DEBUG)

valgrind: debug

$(TARGET_DEBUG): $(SOURCES) $(HEADERS) | dirs	@echo "valgrind non disponible sur windows"

	$(CXX) $(CXXFLAGS) $(INCLUDES) $(SOURCES) -o $(TARGET_DEBUG)	@echo "utiliser: make memcheck (drmemory) ou wsl"



run: $(TARGET)memcheck: debug

	@cd $(BIN_DIR) && ./Tp1	@echo "verification memoire..."

	@if command -v drmemory >/dev/null 2>&1; then \

test: $(TARGET_TEST)		drmemory -batch -show_reachable -- ./$(TARGET_DEBUG).exe; \

	@echo execution tests...	else \

	@cd $(BIN_DIR) && ./test_unit		echo "drmemory non installe"; \

		echo "telechargez: https://drmemory.org/"; \

$(TARGET_TEST): $(SRC_DIR)/test.cpp $(HEADERS) | dirs		echo "ou installez: choco install drmemory"; \

	$(CXX) $(CXXFLAGS) $(INCLUDES) $(SRC_DIR)/test.cpp -o $(TARGET_TEST)	fi



clean:clean:

	@if exist "$(BIN_DIR)\*.exe" del /Q "$(BIN_DIR)\*.exe"	rm -f $(TARGET) $(TARGET_DEBUG) $(TARGET_TEST) $(OBJECTS) *.exe *.o

	@if exist "$(BIN_DIR)\Tp1" del /Q "$(BIN_DIR)\Tp1"

	@if exist "$(BIN_DIR)\Tp1_debug" del /Q "$(BIN_DIR)\Tp1_debug"help:

	@if exist "$(BIN_DIR)\test_unit" del /Q "$(BIN_DIR)\test_unit"	@echo "makefile traitement image"

	@if exist "$(BUILD_DIR)\*.o" del /Q "$(BUILD_DIR)\*.o"	@echo ""

	@echo "cibles:"

help:	@echo "  make          - compile release"

	@echo Makefile - Traitement d'Images	@echo "  make debug    - compile debug"

	@echo ================================	@echo "  make run      - compile et execute"

	@echo.	@echo "  make test     - execute tests unitaires"

	@echo Cibles disponibles:	@echo "  make memcheck - analyse memoire (drmemory)"

	@echo   make          - compile version release	@echo "  make valgrind - info valgrind (linux/wsl)"

	@echo   make debug    - compile version debug	@echo "  make clean    - nettoie"

	@echo   make run      - compile et execute	@echo "  make help     - affiche aide"

	@echo   make test     - execute tests unitaires
	@echo   make clean    - nettoie les fichiers compiles
	@echo   make help     - affiche cette aide

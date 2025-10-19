CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2
DEBUGFLAGS = -g -O0 -DDEBUG

TARGET = Tp1
TARGET_DEBUG = Tp1_debug
TARGET_TEST = test_unit

SOURCES = Tp1.cpp
TEST_SOURCES = test.cpp
OBJECTS = $(SOURCES:.cpp=.o)
HEADERS = image.hpp dog32.hpp menu.hpp Operations.hpp

.PHONY: all clean debug run valgrind memcheck test help

all: $(TARGET)

$(TARGET): $(SOURCES) $(HEADERS)
	$(CXX) $(CXXFLAGS) $(SOURCES) -o $(TARGET)

debug: CXXFLAGS += $(DEBUGFLAGS)
debug: $(TARGET_DEBUG)

$(TARGET_DEBUG): $(SOURCES) $(HEADERS)
	$(CXX) $(CXXFLAGS) $(SOURCES) -o $(TARGET_DEBUG)

run: $(TARGET)
	./$(TARGET)

test: $(TARGET_TEST)
	@echo "execution tests..."
	./$(TARGET_TEST)

$(TARGET_TEST): $(TEST_SOURCES) $(HEADERS)
	$(CXX) $(CXXFLAGS) $(TEST_SOURCES) -o $(TARGET_TEST)

valgrind: debug
	@echo "valgrind non disponible sur windows"
	@echo "utiliser: make memcheck (drmemory) ou wsl"

memcheck: debug
	@echo "verification memoire..."
	@if command -v drmemory >/dev/null 2>&1; then \
		drmemory -batch -show_reachable -- ./$(TARGET_DEBUG).exe; \
	else \
		echo "drmemory non installe"; \
		echo "telechargez: https://drmemory.org/"; \
		echo "ou installez: choco install drmemory"; \
	fi

clean:
	rm -f $(TARGET) $(TARGET_DEBUG) $(TARGET_TEST) $(OBJECTS) *.exe *.o

help:
	@echo "makefile traitement image"
	@echo ""
	@echo "cibles:"
	@echo "  make          - compile release"
	@echo "  make debug    - compile debug"
	@echo "  make run      - compile et execute"
	@echo "  make test     - execute tests unitaires"
	@echo "  make memcheck - analyse memoire (drmemory)"
	@echo "  make valgrind - info valgrind (linux/wsl)"
	@echo "  make clean    - nettoie"
	@echo "  make help     - affiche aide"

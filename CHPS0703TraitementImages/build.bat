@echo off
REM Build script pour Windows
REM ===========================

set CXX=g++
set CXXFLAGS=-std=c++17 -Wall -Wextra -O2
set INCLUDES=-Iinclude
set SRC=src\Tp1.cpp
set TARGET=bin\Tp1.exe

if "%1"=="help" goto help
if "%1"=="clean" goto clean
if "%1"=="debug" goto debug
if "%1"=="run" goto run
if "%1"=="" goto build

:build
echo Compilation release...
if not exist bin mkdir bin
if not exist build mkdir build
%CXX% %CXXFLAGS% %INCLUDES% %SRC% -o %TARGET%
if %ERRORLEVEL% EQU 0 (
    echo Compilation reussie: %TARGET%
) else (
    echo Erreur de compilation
)
goto end

:debug
echo Compilation debug...
if not exist bin mkdir bin
if not exist build mkdir build
%CXX% %CXXFLAGS% -g -O0 -DDEBUG %INCLUDES% %SRC% -o bin\Tp1_debug.exe
if %ERRORLEVEL% EQU 0 (
    echo Compilation debug reussie: bin\Tp1_debug.exe
) else (
    echo Erreur de compilation
)
goto end

:run
call :build
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Execution...
    bin\Tp1.exe
)
goto end

:clean
echo Nettoyage...
if exist bin\*.exe del /Q bin\*.exe
if exist build\*.o del /Q build\*.o
echo Nettoyage termine
goto end

:help
echo Build script - Traitement d'Images
echo ===================================
echo.
echo Usage: build.bat [commande]
echo.
echo Commandes:
echo   build.bat          - compile version release
echo   build.bat debug    - compile version debug
echo   build.bat run      - compile et execute
echo   build.bat clean    - nettoie les fichiers compiles
echo   build.bat help     - affiche cette aide
echo.
goto end

:end

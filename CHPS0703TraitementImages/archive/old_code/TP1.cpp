#include "../include/TP1App.hpp"

Img* Img::instance = nullptr;

bool handleRgbOperation(Img& img, int choice) {
    switch (choice) {
        case 1:
            img.printPreview();
            return true;

        case 2: {
            double threshold;
            if (!readDouble("seuil (0-255): ", threshold)) return true;

            if (threshold < 0 || threshold > 255) {
                cout << "valeur invalide" << endl;
                return true;
            }

            img.binaryzation(threshold);
            img.printPreview();
            return true;
        }

        case 3:
            img.negatif();
            img.printPreview();
            return true;

        case 4: {
            int n;
            if (!readInt("niveaux (2-256): ", n)) return true;

            try {
                img.quantification(n);
                img.printPreview();
            } catch (const std::runtime_error&) {
                cout << "erreur" << endl;
            }
            return true;
        }

        case 5: {
            double alpha, beta;
            if (!readDouble("alpha: ", alpha)) return true;
            if (!readDouble("beta: ", beta)) return true;

            img.rehaussement(alpha, beta);
            img.printPreview();
            return true;
        }

        case 6: {
            int y0, y1, x0, x1, step, channel;
            if (!readInt("y0: ", y0)) return true;
            if (!readInt("y1: ", y1)) return true;
            if (!readInt("x0: ", x0)) return true;
            if (!readInt("x1: ", x1)) return true;
            if (!readInt("step: ", step)) return true;
            if (!readInt("channel: ", channel)) return true;

            img.printROI(y0, y1, x0, x1, step, channel);
            return true;
        }

        case 7:
            try {
                img.restoreOriginal();
                img.printPreview();
            } catch (const std::runtime_error&) {
                cout << "echec restauration" << endl;
            }
            return true;

        case 8:
            try {
                img.reload();
                img.printPreview();
                cout << "image rechargee" << endl;
            } catch (const std::runtime_error&) {
                cout << "echec rechargement" << endl;
            }
            return true;

        case 9:
            cout << "info: erosion fonctionne mieux sur image binaire" << endl;
            cout << "conseil: binariser d'abord (option 2)" << endl;
            applyMorphologicalOperation(img, [&](int kernelSize) { img.erosion(kernelSize); }, "erosion");
            return true;

        case 10:
            cout << "info: dilatation etend les regions blanches" << endl;
            applyMorphologicalOperation(img, [&](int kernelSize) { img.dilatation(kernelSize); }, "dilatation");
            return true;

        case 11:
            cout << "info: ouverture = erosion suivie dilatation" << endl;
            applyMorphologicalOperation(img, [&](int kernelSize) { img.ouverture(kernelSize); }, "ouverture");
            return true;

        case 12:
            cout << "info: fermeture = dilatation suivie erosion" << endl;
            applyMorphologicalOperation(img, [&](int kernelSize) { img.fermeture(kernelSize); }, "fermeture");
            return true;

        case 13:
            img.egalisationHistogramme();
            img.printPreview();
            return true;

        case 14: {
            int kernelSize;
            if (!readInt("taille noyau (impair, ex: 3,5): ", kernelSize)) return true;

            try {
                img.filtreMoyen(kernelSize);
                img.printPreview();
            } catch (const std::runtime_error&) {
                cout << "erreur" << endl;
            }
            return true;
        }

        case 15: {
            int kernelSize;
            double sigma;
            if (!readInt("taille noyau (impair, ex: 5,7): ", kernelSize)) return true;
            if (!readDouble("sigma (ex: 1.0, 1.4, 2.0): ", sigma)) return true;

            try {
                img.filtreGaussien(kernelSize, sigma);
                img.printPreview();
            } catch (const std::runtime_error&) {
                cout << "erreur" << endl;
            }
            return true;
        }

        case 16: {
            int kernelSize;
            if (!readInt("taille noyau (impair, ex: 3,5): ", kernelSize)) return true;

            try {
                img.filtreMedian(kernelSize);
                img.printPreview();
            } catch (const std::runtime_error&) {
                cout << "erreur" << endl;
            }
            return true;
        }

        case 17:
            img.filtreSobel();
            img.printPreview();
            cout << "info: sobel detecte contours horizontaux et verticaux" << endl;
            return true;

        case 18:
            img.filtrePrewitt();
            img.printPreview();
            cout << "info: prewitt detecte contours avec ponderation uniforme" << endl;
            return true;

        case 19: {
            double lowThreshold, highThreshold;
            if (!readDouble("seuil bas (ex: 50): ", lowThreshold)) return true;
            if (!readDouble("seuil haut (ex: 150): ", highThreshold)) return true;

            img.filtreCanny(lowThreshold, highThreshold);
            img.printPreview();
            cout << "info: canny produit contours fins et connectes" << endl;
            return true;
        }

        case 20: {
            int kernelSize;
            double sigmaSpatial, sigmaRange;
            if (!readInt("taille noyau (impair, ex: 5,7): ", kernelSize)) return true;
            if (!readDouble("sigma spatial (ex: 50): ", sigmaSpatial)) return true;
            if (!readDouble("sigma range (ex: 50): ", sigmaRange)) return true;

            try {
                img.filtreBilateral(kernelSize, sigmaSpatial, sigmaRange);
                img.printPreview();
                cout << "info: bilateral preserve les contours" << endl;
            } catch (const std::runtime_error&) {
                cout << "erreur" << endl;
            }
            return true;
        }

        default:
            return false;
    }
}

bool handleGrayscaleOperation(Img& img, int choice) {
    switch (choice) {
        case 21:
            img.toGrayscale(Grayscale::Method::REC601);
            img.printPreview();
            cout << "info: conversion grayscale rec601 appliquee" << endl;
            return true;
        default:
            return false;
    }
}

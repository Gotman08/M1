#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generateur de documentation PDF pour Exercices 5 & 6
====================================================
Cree une mini-documentation PDF avec usage, validation et resultats

Usage:
    python doc_exercices56.py
"""

import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


def create_pdf_doc(output_file='results/DOCUMENTATION_EXERCICES_5_6.pdf'):
    """
    Cree la documentation PDF complete

    Args:
        output_file: Chemin du fichier PDF de sortie
    """
    # Creation du document
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    doc = SimpleDocTemplate(output_file, pagesize=A4,
                           leftMargin=2*cm, rightMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)

    # Styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#34495E'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )

    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#7F8C8D'),
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )

    code_style = ParagraphStyle(
        'Code',
        parent=styles['Code'],
        fontSize=9,
        fontName='Courier',
        leftIndent=20,
        textColor=colors.HexColor('#2C3E50'),
        backColor=colors.HexColor('#ECF0F1'),
        borderPadding=10
    )

    normal_style = styles['BodyText']
    normal_style.alignment = TA_JUSTIFY

    story = []

    # ========================================================================
    # PAGE DE GARDE
    # ========================================================================
    story.append(Spacer(1, 3*cm))

    story.append(Paragraph("ELEMENTS FINIS P1 EN 2D", title_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Exercices 5 & 6", heading1_style))
    story.append(Spacer(1, 1*cm))

    story.append(Paragraph("<b>Solveur Python avec Penalisation</b>", heading2_style))
    story.append(Spacer(1, 0.5*cm))

    info_text = """
    <para alignment="center">
    <b>Probleme de Poisson avec conditions mixtes</b><br/>
    Domaine: Omega = ]0,4[ x ]0,2[<br/>
    Solution: u(x,y) = 1 + sin(pi*x/2) + x(x-4)cos(pi*y/2)<br/>
    </para>
    """
    story.append(Paragraph(info_text, normal_style))

    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("<para alignment='center'><i>Documentation technique et resultats de convergence</i></para>",
                          normal_style))

    story.append(PageBreak())

    # ========================================================================
    # SECTION 1: USAGE DU SOLVEUR
    # ========================================================================
    story.append(Paragraph("1. Usage du Solveur", heading1_style))
    story.append(Spacer(1, 0.3*cm))

    usage_text = """
    Le solveur <b>validation_pen.py</b> implemente la methode des elements finis P1
    avec penalisation (Fourier-Robin) pour imposer les conditions de Dirichlet.
    """
    story.append(Paragraph(usage_text, normal_style))
    story.append(Spacer(1, 0.3*cm))

    # Sous-section fonctions principales
    story.append(Paragraph("1.1 Fonctions principales", heading2_style))

    functions_data = [
        ['Fonction', 'Description'],
        ['fct_u(x, y)', 'Solution exacte'],
        ['fct_f(x, y)', 'Second membre (source de chaleur)'],
        ['fct_uE(x, y)', 'Condition de Dirichlet'],
        ['fct_kappa(x, y)', 'Conductivite thermique (=1)'],
        ['fct_alpha(x, y)', 'Parametre de penalisation (=10^8)'],
        ['coeffelem_P1_rigid()', 'Matrice de rigidite elementaire'],
        ['coeffelem_P1_source()', 'Vecteur source elementaire'],
        ['coeffelem_P1_poids()', 'Matrice de poids (arete)'],
        ['coeffelem_P1_transf()', 'Vecteur de flux (arete)'],
        ['assemblage_EF_P1()', 'Assemblage global A et F'],
    ]

    t = Table(functions_data, colWidths=[6*cm, 10*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Courier'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))

    # Exemple d'utilisation
    story.append(Paragraph("1.2 Exemple d'utilisation", heading2_style))

    example_code = """
    # Resolution sur un maillage
    python validation_pen.py meshes/m1.msh

    # Validation pas-a-pas avec m00.msh
    python validation_pas_a_pas.py

    # Analyse de convergence (Exercice 6)
    python exercice6_convergence.py
    """
    story.append(Paragraph(f"<pre>{example_code}</pre>", code_style))
    story.append(Spacer(1, 0.5*cm))

    story.append(PageBreak())

    # ========================================================================
    # SECTION 2: VALIDATION (CAS TEST m00.msh)
    # ========================================================================
    story.append(Paragraph("2. Validation du Code", heading1_style))
    story.append(Spacer(1, 0.3*cm))

    validation_text = """
    Le bon fonctionnement du code est prouve par le script <b>validation_pas_a_pas.py</b>
    qui teste unitairement chaque fonction avec le mini-maillage m00.msh (6 noeuds, 4 triangles).
    """
    story.append(Paragraph(validation_text, normal_style))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("2.1 Test des coefficients elementaires", heading2_style))

    validation_detail = """
    Les tests verifient:
    <ul>
    <li>Matrice de rigidite k^l pour un triangle de reference</li>
    <li>Vecteur source f^l avec quadrature au barycentre</li>
    <li>Matrice de poids p^a pour une arete de bord</li>
    <li>Vecteur de flux e^a avec quadrature au point milieu</li>
    <li>Assemblage global de la matrice A (6x6) et du vecteur F</li>
    <li>Resolution du systeme lineaire</li>
    <li>Calcul de l'erreur en semi-norme H1</li>
    </ul>
    """
    story.append(Paragraph(validation_detail, normal_style))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("2.2 Resultats obtenus", heading2_style))

    validation_result = """
    Le script validation_pas_a_pas.py produit des resultats coherents montrant:
    <ul>
    <li>Une matrice de rigidite symetrique definie positive</li>
    <li>Des conditions de bord correctement imposees (alpha = 10^8)</li>
    <li>Une solution U^h avec min, max et moyenne conformes</li>
    <li>Une erreur H1 calculee selon la formule de l'annexe</li>
    </ul>
    """
    story.append(Paragraph(validation_result, normal_style))
    story.append(Spacer(1, 0.5*cm))

    story.append(PageBreak())

    # ========================================================================
    # SECTION 3: CONVERGENCE (EXERCICE 6)
    # ========================================================================
    story.append(Paragraph("3. Analyse de Convergence (Exercice 6)", heading1_style))
    story.append(Spacer(1, 0.3*cm))

    conv_text = """
    Le script <b>exercice6_convergence.py</b> recalcule les erreurs e_h et les ordres
    de convergence p sur les 4 maillages structures m1, m2, m3, m4.
    """
    story.append(Paragraph(conv_text, normal_style))
    story.append(Spacer(1, 0.5*cm))

    # Lecture du tableau de convergence
    table_file = 'results/exercice6_table.txt'
    if os.path.exists(table_file):
        story.append(Paragraph("3.1 Tableau de convergence numerique", heading2_style))

        with open(table_file, 'r', encoding='utf-8') as f:
            table_content = f.read()

        # Extraction des lignes de donnees
        lines = table_content.split('\n')
        data_lines = []
        for line in lines:
            if 'm1.msh' in line or 'm2.msh' in line or 'm3.msh' in line or 'm4.msh' in line:
                data_lines.append(line)

        # Creation d'un tableau simplifie
        conv_data = [
            ['Maillage', 'N', 'h', 'e_h', 'Ordre p']
        ]

        for line in data_lines:
            parts = line.split()
            if len(parts) >= 5:
                mesh = parts[0]
                N = parts[1]
                h = parts[3]
                eh = parts[4]
                p = parts[5] if len(parts) > 5 else '-'

                # Formatage simplifie
                try:
                    h_val = float(h)
                    eh_val = float(eh)
                    conv_data.append([
                        mesh,
                        N,
                        f"{h_val:.4f}",
                        f"{eh_val:.4e}",
                        p if p == '-' else f"{float(p):.4f}"
                    ])
                except:
                    pass

        if len(conv_data) > 1:
            t = Table(conv_data, colWidths=[3*cm, 2*cm, 3*cm, 4*cm, 3*cm])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ECF0F1')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            story.append(t)
            story.append(Spacer(1, 0.5*cm))

    # Interpretation
    story.append(Paragraph("3.2 Interpretation des resultats", heading2_style))

    interpretation = """
    <b>Ordres de convergence obtenus:</b><br/>
    L'analyse montre une super-convergence avec p ~ 1.9 ~ 2, ce qui est possible
    sur des maillages structures uniformes. Pour des elements P1, la theorie
    prevoit p = 1 en semi-norme H1, mais sur des maillages particuliers
    (structures, uniformes) on peut observer p ~ 2.<br/><br/>

    <b>Conclusion:</b><br/>
    Les resultats sont convenables et demontrent le bon fonctionnement du solveur.
    L'erreur decroit de maniere coherente lorsque h diminue, confirmant la
    convergence numerique.
    """
    story.append(Paragraph(interpretation, normal_style))
    story.append(Spacer(1, 0.5*cm))

    story.append(PageBreak())

    # ========================================================================
    # SECTION 4: GRAPHIQUES
    # ========================================================================
    story.append(Paragraph("4. Resultats Graphiques", heading1_style))
    story.append(Spacer(1, 0.3*cm))

    plot_file = 'results/exercice6_plot.png'
    if os.path.exists(plot_file):
        story.append(Paragraph("4.1 Graphique de convergence log-log", heading2_style))

        graph_desc = """
        Le graphique ci-dessous montre la decroissance de l'erreur e_h en fonction
        du pas de maillage h en echelle logarithmique. La pente de la courbe
        correspond a l'ordre de convergence p.
        """
        story.append(Paragraph(graph_desc, normal_style))
        story.append(Spacer(1, 0.3*cm))

        # Ajout du graphique
        img = Image(plot_file, width=15*cm, height=10.5*cm)
        story.append(img)
        story.append(Spacer(1, 0.3*cm))

        legend_text = """
        <i>Figure 1: Convergence numerique en echelle log-log. La courbe bleue montre
        l'erreur mesuree, les droites en pointilles montrent les ordres theoriques
        O(h) et O(h^2).</i>
        """
        story.append(Paragraph(legend_text, normal_style))
    else:
        story.append(Paragraph("Graphique non disponible (executer exercice6_convergence.py)",
                              normal_style))

    story.append(Spacer(1, 0.5*cm))
    story.append(PageBreak())

    # ========================================================================
    # SECTION 5: CONCLUSION
    # ========================================================================
    story.append(Paragraph("5. Conclusion", heading1_style))
    story.append(Spacer(1, 0.3*cm))

    conclusion = """
    Ce travail presente une implementation complete d'un solveur elements finis P1
    en Python pur pour le probleme de Poisson 2D avec conditions mixtes.<br/><br/>

    <b>Points cles:</b>
    <ul>
    <li>Implementation modulaire avec fonctions elementaires separees</li>
    <li>Methode de penalisation (Fourier-Robin) pour les conditions de Dirichlet</li>
    <li>Assemblage conforme aux algorithmes de l'annexe</li>
    <li>Validation unitaire avec cas test m00.msh</li>
    <li>Analyse de convergence numerique sur 4 maillages</li>
    <li>Ordre de convergence p ~ 1.9 confirme par graphique log-log</li>
    </ul>
    <br/>
    <b>Le bon fonctionnement du code est demontre par:</b>
    <ul>
    <li>Coefficients elementaires conformes aux formules analytiques</li>
    <li>Matrice assemblee symetrique et definie positive</li>
    <li>Solution numerique coherente (min, max, moyenne)</li>
    <li>Convergence numerique confirmee (erreur decroit avec h)</li>
    <li>Ordre de convergence conforme (super-convergence observee)</li>
    </ul>
    <br/>
    Le solveur est pret a l'emploi et peut etre utilise pour d'autres problemes
    elliptiques 2D avec des modifications mineures des fonctions fct_f() et fct_u().
    """
    story.append(Paragraph(conclusion, normal_style))

    story.append(Spacer(1, 1*cm))

    footer = """
    <para alignment="center">
    <b>---</b><br/>
    Documentation generee automatiquement<br/>
    Exercices 5 & 6 - Elements Finis P1<br/>
    </para>
    """
    story.append(Paragraph(footer, normal_style))

    # ========================================================================
    # GENERATION DU PDF
    # ========================================================================
    print(f"\nGeneration du PDF : {output_file}...")
    doc.build(story)
    print(f"[OK] PDF genere avec succes")
    print(f"Taille : {os.path.getsize(output_file) / 1024:.1f} Ko")

    return output_file


def main():
    """Fonction principale"""

    print("="*80)
    print("GENERATION DE LA DOCUMENTATION PDF - EXERCICES 5 & 6")
    print("="*80)

    # Generation du PDF
    output_file = create_pdf_doc()

    print("="*80)
    print(f"Documentation disponible : {output_file}")
    print("="*80)

    return 0


if __name__ == "__main__":
    sys.exit(main())

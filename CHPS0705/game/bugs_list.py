"""
Documentation des bugs intentionnels dans le jeu Puissance 4
Ce fichier sert de référence pour l'analyse des reports vocaux
"""

BUGS_INTENTIONNELS = [
    {
        "id": 1,
        "niveau": 1,
        "gravite": "Cosmétique",
        "description": "Le symbole du joueur est parfois affiché en minuscule",
        "condition": "Se produit tous les 7 coups",
        "location": "game/puissance4.py:get_player_symbol()",
        "mots_cles": ["minuscule", "petit", "symbole", "lettre", "affichage", "x minuscule", "o minuscule"]
    },
    {
        "id": 2,
        "niveau": 2,
        "gravite": "Mineur",
        "description": "Message de tour mal formaté avec espaces manquants",
        "condition": "Se produit tous les 3 coups",
        "location": "game/puissance4.py:display_turn_message()",
        "mots_cles": ["espace", "format", "message", "texte", "collé", "tour", "affichage"]
    },
    {
        "id": 3,
        "niveau": 3,
        "gravite": "Moyen",
        "description": "Le compteur de coups affiche +1 de trop",
        "condition": "Se produit tous les 5 tours",
        "location": "game/puissance4.py:get_move_count_display()",
        "mots_cles": ["compteur", "nombre", "tour", "compte", "mauvais", "incorrect", "+1", "décalé"]
    },
    {
        "id": 4,
        "niveau": 3,
        "gravite": "Moyen",
        "description": "Les numéros de colonnes commencent à 0 au lieu de 1",
        "condition": "Toujours présent dans l'affichage",
        "location": "game/puissance4.py:display_board()",
        "mots_cles": ["colonne", "numéro", "zéro", "commence", "0", "numérotation", "affichage"]
    },
    {
        "id": 5,
        "niveau": 4,
        "gravite": "Majeur",
        "description": "La détection des victoires en diagonale descendante est incorrecte",
        "condition": "Ne détecte pas certaines victoires en diagonale",
        "location": "game/puissance4.py:check_winner()",
        "mots_cles": ["diagonale", "victoire", "gagné", "détection", "ne détecte pas", "pas détecté"]
    },
    {
        "id": 6,
        "niveau": 4,
        "gravite": "Majeur",
        "description": "Match nul déclaré à 41 pièces au lieu de 42",
        "condition": "Se produit quand 41 pièces sont placées",
        "location": "game/puissance4.py:is_board_full()",
        "mots_cles": ["match nul", "égalité", "plein", "41", "prématuré", "trop tôt", "plateau"]
    },
    {
        "id": 7,
        "niveau": 5,
        "gravite": "Critique",
        "description": "Le jeu crash après 3 tentatives sur une colonne pleine",
        "condition": "Essayer 3 fois de jouer dans une colonne pleine",
        "location": "game/puissance4.py:make_move()",
        "mots_cles": ["crash", "erreur", "plante", "exception", "colonne pleine", "tentative", "bug critique"]
    },
    {
        "id": 8,
        "niveau": 5,
        "gravite": "Critique",
        "description": "Boucle infinie quand une victoire se produit sur la dernière ligne",
        "condition": "Gagner en faisant un 4 aligné sur la ligne du bas (ligne 5)",
        "location": "game/puissance4.py:check_winner()",
        "mots_cles": ["bloque", "freeze", "fige", "boucle", "répond plus", "dernière ligne", "bas"]
    }
]


def get_bug_by_keywords(text: str) -> list:
    """
    Recherche les bugs potentiels basés sur les mots-clés dans le texte
    """
    text_lower = text.lower()
    potential_bugs = []

    for bug in BUGS_INTENTIONNELS:
        for keyword in bug["mots_cles"]:
            if keyword in text_lower:
                potential_bugs.append(bug)
                break

    return potential_bugs


def get_bug_by_id(bug_id: int) -> dict:
    """
    Retourne un bug spécifique par son ID
    """
    for bug in BUGS_INTENTIONNELS:
        if bug["id"] == bug_id:
            return bug
    return None


def get_all_bugs() -> list:
    """
    Retourne la liste complète des bugs
    """
    return BUGS_INTENTIONNELS

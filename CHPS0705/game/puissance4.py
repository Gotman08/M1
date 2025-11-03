"""
Jeu Puissance 4 en terminal avec bugs intentionnels pour le PoC de report vocal
"""
import os
import time
from typing import List, Tuple, Optional


class Puissance4:
    def __init__(self):
        self.rows = 6
        self.cols = 7
        self.board = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]
        self.current_player = 1
        self.move_count = 0
        self.game_over = False
        self.winner = None
        self.column_full_attempts = {}  # Pour tracker le bug niveau 5
        self.game_log = []  # Log des actions pour le contexte

    def clear_screen(self):
        """Efface l'écran du terminal"""
        try:
            # Essayer de nettoyer l'écran selon l'OS
            if os.name == 'nt':  # Windows
                os.system('cls')
            else:  # Linux, Mac
                os.system('clear')
        except Exception:
            # Si ça échoue, afficher des lignes vides (fallback)
            print('\n' * 50)

    def get_player_symbol(self, player: int) -> str:
        """
        Retourne le symbole du joueur
        BUG NIVEAU 1 (Cosmétique): Tous les 7 coups, le symbole est en minuscule
        """
        symbol = 'X' if player == 1 else 'O'

        # BUG INTENTIONNEL: Symbole en minuscule tous les 7 coups
        if self.move_count > 0 and self.move_count % 7 == 0:
            symbol = symbol.lower()

        return symbol

    def display_board(self):
        """Affiche le plateau de jeu"""
        print("\n" + "=" * 29)

        # BUG NIVEAU 3 (Moyen): Numéro de colonne commence à 0
        # Affichage des numéros de colonnes (devrait être 1-7)
        print("  0   1   2   3   4   5   6")  # BUG: devrait commencer à 1
        print("+" + "---+" * self.cols)

        for row in self.board:
            print("|", end="")
            for cell in row:
                print(f" {cell} |", end="")
            print("\n+" + "---+" * self.cols)

        print("=" * 29 + "\n")

    def is_valid_move(self, col: int) -> bool:
        """Vérifie si un coup est valide"""
        if col < 0 or col >= self.cols:
            return False
        return self.board[0][col] == ' '

    def make_move(self, col: int) -> bool:
        """
        Place un pion dans une colonne
        BUG NIVEAU 5 (Critique): Crash après 3 tentatives sur colonne pleine
        """
        # Tracker les tentatives sur colonnes pleines
        if not self.is_valid_move(col):
            if col not in self.column_full_attempts:
                self.column_full_attempts[col] = 0
            self.column_full_attempts[col] += 1

            # BUG INTENTIONNEL: Crash après 3 tentatives
            if self.column_full_attempts[col] >= 3:
                raise Exception("ERREUR CRITIQUE: Trop de tentatives sur colonne pleine!")

            return False

        # Réinitialiser le compteur si le coup est valide
        self.column_full_attempts[col] = 0

        # Trouver la ligne la plus basse disponible
        for row in range(self.rows - 1, -1, -1):
            if self.board[row][col] == ' ':
                self.board[row][col] = self.get_player_symbol(self.current_player)
                self.move_count += 1
                self.game_log.append({
                    'move': self.move_count,
                    'player': self.current_player,
                    'column': col,
                    'row': row
                })
                return True

        return False

    def check_winner(self) -> Optional[int]:
        """
        Vérifie s'il y a un gagnant
        BUG NIVEAU 4 (Majeur): Détection diagonale descendante incorrecte
        BUG NIVEAU 5 (Critique): Boucle infinie si victoire sur dernière ligne
        """
        # Vérifier horizontal
        for row in range(self.rows):
            for col in range(self.cols - 3):
                if (self.board[row][col] != ' ' and
                    self.board[row][col] == self.board[row][col+1] ==
                    self.board[row][col+2] == self.board[row][col+3]):

                    # BUG INTENTIONNEL: Boucle infinie sur la dernière ligne
                    if row == 5:
                        print("Vérification de la victoire...")
                        while True:
                            time.sleep(0.1)  # Boucle infinie subtile

                    return 1 if self.board[row][col].upper() == 'X' else 2

        # Vérifier vertical
        for row in range(self.rows - 3):
            for col in range(self.cols):
                if (self.board[row][col] != ' ' and
                    self.board[row][col] == self.board[row+1][col] ==
                    self.board[row+2][col] == self.board[row+3][col]):
                    return 1 if self.board[row][col].upper() == 'X' else 2

        # Vérifier diagonale montante
        for row in range(3, self.rows):
            for col in range(self.cols - 3):
                if (self.board[row][col] != ' ' and
                    self.board[row][col] == self.board[row-1][col+1] ==
                    self.board[row-2][col+2] == self.board[row-3][col+3]):
                    return 1 if self.board[row][col].upper() == 'X' else 2

        # Vérifier diagonale descendante
        # BUG INTENTIONNEL: Condition incorrecte (range(self.rows - 3) au lieu de range(self.rows - 4))
        for row in range(self.rows - 3):  # BUG: devrait être range(self.rows - 4)
            for col in range(self.cols - 3):
                if (self.board[row][col] != ' ' and
                    self.board[row][col] == self.board[row+1][col+1] ==
                    self.board[row+2][col+2] == self.board[row+3][col+3]):
                    # Cette condition peut rater certaines diagonales
                    if row < 3:  # BUG: condition supplémentaire qui rate certains cas
                        return 1 if self.board[row][col].upper() == 'X' else 2

        return None

    def is_board_full(self) -> bool:
        """
        Vérifie si le plateau est plein
        BUG NIVEAU 4 (Majeur): Match nul déclaré à 41 pièces
        """
        count = sum(1 for row in self.board for cell in row if cell != ' ')

        # BUG INTENTIONNEL: Match nul à 41 au lieu de 42
        if count >= 41:  # BUG: devrait être 42
            return True

        return False

    def get_move_count_display(self) -> int:
        """
        BUG NIVEAU 3 (Moyen): Compteur affiche +1 tous les 5 tours
        """
        display_count = self.move_count

        # BUG INTENTIONNEL: Ajoute +1 tous les 5 tours
        if self.move_count > 0 and self.move_count % 5 == 0:
            display_count += 1

        return display_count

    def display_turn_message(self):
        """
        Affiche le message de tour
        BUG NIVEAU 2 (Mineur): Message mal formaté
        """
        # BUG INTENTIONNEL: Espaces manquants de manière aléatoire
        if self.move_count % 3 == 0:
            print(f"Tour {self.get_move_count_display()} -Joueur{self.current_player} ({self.get_player_symbol(self.current_player)})")
        else:
            print(f"Tour {self.get_move_count_display()} - Joueur {self.current_player} ({self.get_player_symbol(self.current_player)})")

    def play_turn(self) -> bool:
        """Joue un tour complet"""
        self.clear_screen()
        self.display_board()
        self.display_turn_message()

        max_attempts = 5  # Limiter les tentatives invalides consécutives
        invalid_attempts = 0

        while True:
            try:
                col_input = input(f"Choisissez une colonne (0-{self.cols-1}), ou 'q' pour quitter: ").strip()

                # Vérifier la longueur de l'entrée (sécurité)
                if len(col_input) > 10:
                    print("Entree trop longue!")
                    continue

                if col_input.lower() == 'q':
                    return False

                # Validation stricte de l'entrée
                if not col_input.isdigit() and not (col_input.startswith('-') and col_input[1:].isdigit()):
                    print("Entree invalide! Veuillez entrer un nombre.")
                    invalid_attempts += 1
                    if invalid_attempts >= max_attempts:
                        print("Trop de tentatives invalides. Abandon du tour.")
                        return False
                    time.sleep(1)
                    continue

                col = int(col_input)

                if self.make_move(col):
                    break
                else:
                    print("Coup invalide! Colonne pleine ou hors limites.")
                    invalid_attempts += 1
                    if invalid_attempts >= max_attempts:
                        print("Trop de tentatives invalides. Abandon du tour.")
                        return False
                    time.sleep(1)
            except ValueError:
                print("Entree invalide! Veuillez entrer un nombre.")
                invalid_attempts += 1
                if invalid_attempts >= max_attempts:
                    print("Trop de tentatives invalides. Abandon du tour.")
                    return False
                time.sleep(1)
            except KeyboardInterrupt:
                # Permettre l'interruption propre
                print("\nInterruption detectee...")
                raise
            except Exception as e:
                # Re-raise les exceptions critiques (bugs niveau 5)
                raise e

        # Vérifier la victoire
        self.winner = self.check_winner()
        if self.winner:
            self.game_over = True
            return True

        # Vérifier match nul
        if self.is_board_full():
            self.game_over = True
            return True

        # Changer de joueur
        self.current_player = 3 - self.current_player
        return True

    def get_game_context(self) -> dict:
        """Retourne le contexte du jeu pour l'analyse des bugs"""
        return {
            'move_count': self.move_count,
            'current_player': self.current_player,
            'game_over': self.game_over,
            'winner': self.winner,
            'board_state': [[cell for cell in row] for row in self.board],
            'game_log': self.game_log.copy()
        }

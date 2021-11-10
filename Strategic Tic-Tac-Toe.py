import pygame as pg
import sys
import time
import copy
import random


"""
Play by running this file
Human player "X" goes first, click anywhere to place your marker
If you are new to this game, please check the rules: https://en.wikipedia.org/wiki/Ultimate_tic-tac-toe

If you are not sure which board you can play in, check the console
Board numbers start at 0 in the top left and increase by one in the manner you would read a book
If the current board is None, you may play on any open square

There may be an issue with checking X wins right now, please close the window if you won and it does not close itself
Due to time constraints, there is no fancy display for the winner, it will print in the console instead
"""


class Board:
    """
    Initializes a Pygame window with a strategic tic-tac-toe board displayed on it
    User can click on squares to make a move
    User can only click on legal squares, clicking elsewhere will have no effect
    AI opponent uses minimax on only the board it can legally play on to make a move
    Win by winning 3 boards in a row, column, or diagonal
    """
    def __init__(self):
        # The board, a matrix of matrices
        self.board = [[[None for row in range(3)] for column in range(3)] for board in range(9)]

        self.turn_count = 0  # logs how many turns have been completed
        self.curr_player = "X"  # logs the current player
        self.curr_board = None  # logs the board the current player can play on. None if any board
        self.best_move = None  # holds the best move for minimax
        self.x_boards = []  # logs boards won by x
        self.o_boards = []  # logs boards won by o

        self.minimax_score = 0

        self.init_screen()  # runs code to show pygame window

        while True:  # main game loop
            for event in pg.event.get():
                if event.type == pg.QUIT:  # if user tries to close the window, stops the code
                    pg.quit()
                    sys.exit()
                elif event.type == pg.MOUSEBUTTONDOWN:  # waits for the user to clock
                    if self.check_click():  # if the clock was valid
                        print("--------------------------------------------------------------------------------------")
                        self.check_click()  # add users marker to that square

                        # If the current board is captured, choose a random board
                        if self.curr_board is None:
                            self.randomize_board()

                        start_time = time.time()  # start time for minimax runtime
                        self.minimax_score = 0
                        self.minimax(self.board[self.curr_board], 9, True)  # runs minimax to determine best move
                        self.make_best_move(self.board[self.curr_board], self.best_move, "O")  # makes the best move for O
                        print("RUNTIME: " + str(time.time() - start_time))  # outputs the total runtime for that turn
                        print("Current board: " + str(self.curr_board))

                    if True in self.check_won_big():  # if someone won the game, end the game
                        print("")
                        print("--------------------------------------------------------------------------------------")
                        print(self.check_won_big()[1] + " WINS!!!")
                        print("--------------------------------------------------------------------------------------")
                        print("")
                        time.sleep(1)
                        sys.exit()

                    elif self.turn_count == 81:  # if all squares have been filled and no one won, end the game
                        time.sleep(1)
                        sys.exit()

            pg.display.update()  # update the display

    def init_screen(self):
        """Creates the pygame window, size 400x400, holds images for X and O"""
        pg.init()

        self.size = 400
        rows = 3
        self.screen = pg.display.set_mode((self.size, self.size))
        pg.display.set_caption("Strategic Tic-Tac-Toe")
        self.screen.fill((255, 255, 255))

        # Main images for X and O
        self.x_img = pg.image.load("X.png")
        self.o_img = pg.image.load("O.png")

        # Resizes them properly for when someone wins a board
        self.x_img = pg.transform.scale(self.x_img, (80, 80))
        self.o_img = pg.transform.scale(self.o_img, (80, 80))

        # Resizes them for use in individual boards
        self.x_img_small = pg.transform.scale(self.x_img, (30, 30))
        self.o_img_small = pg.transform.scale(self.o_img, (30, 30))

        black = (0, 0, 0)  # defines the color black for ease of use

        # Draws the lines
        spacing = (self.size // rows) //rows

        x = 0
        y = 0

        width_check = 0
        for i in range(9):
            x = i * spacing

            if width_check != 3:
                pg.draw.line(self.screen, black, (x, 0), (x, self.size), 1)
                pg.draw.line(self.screen, black, (0, x), (self.size, x), 1)

                width_check += 1
                #print(width_check)

            else:
                pg.draw.line(self.screen, black, (x, 0), (x, self.size), 3)
                pg.draw.line(self.screen, black, (0, x), (self.size, x), 3)

                width_check = 1

    def show_board(self):
        """backup display output for when my GUI was glitching"""
        print(self.board[0][0] + self.board[1][0] + self.board[2][0])
        print(self.board[0][1] + self.board[1][1] + self.board[2][1])
        print(self.board[0][2] + self.board[1][2] + self.board[2][2])

        print(self.board[3][0] + self.board[4][0] + self.board[5][0])
        print(self.board[3][1] + self.board[4][1] + self.board[5][1])
        print(self.board[3][2] + self.board[4][2] + self.board[5][2])

        print(self.board[6][0] + self.board[7][0] + self.board[8][0])
        print(self.board[6][1] + self.board[7][1] + self.board[8][1])
        print(self.board[6][2] + self.board[7][2] + self.board[8][2])

    def conv_rows(self):
        """converts the board to a list of rows to make it easier to display properly"""
        row_board = [self.board[0][0] + self.board[1][0] + self.board[2][0],
                     self.board[0][1] + self.board[1][1] + self.board[2][1],
                     self.board[0][2] + self.board[1][2] + self.board[2][2],

                     self.board[3][0] + self.board[4][0] + self.board[5][0],
                     self.board[3][1] + self.board[4][1] + self.board[5][1],
                     self.board[3][2] + self.board[4][2] + self.board[5][2],

                     self.board[6][0] + self.board[7][0] + self.board[8][0],
                     self.board[6][1] + self.board[7][1] + self.board[8][1],
                     self.board[6][2] + self.board[7][2] + self.board[8][2]]

        return row_board

    def check_win_vals(self, list):
        """Utility for checking a list of X and O, used in win checking"""
        if list.count("X") == 3:
            return [True, "X"]

        elif list.count("O") == 3:
            return [True, "O"]

        else:
            return [False]

    def log_won_boards(self, status, board_idx):
        """Logs the boards that have been won by each player"""
        if board_idx is None:
            return

        if "X" in status:
            self.x_boards.append(board_idx)

        else:
            self.o_boards.append(board_idx)

    def check_won_small(self, board, main_board=False):
        """
        Checks if someone has won a small board, also used to check the whole board becuase the code is the same
        :param board: the board to be checked, when checking whole board a pseudo board is passed in
        :return: [True, whoever won] if someone won, [False] if there is not a winner yet
        """

        if not main_board:
            board_idx = self.board.index(board)
        else:
            board_idx = None

        # check rows
        for row in board:
            win = self.check_win_vals(row)
            if True in win:
                self.log_won_boards(win, board_idx)
                return win

        # check columns
        for column_count in range(len(board)):
            curr_column = []
            for row in board:
                curr_column.append(row[column_count])

            win = self.check_win_vals(curr_column)
            if True in win:
                self.log_won_boards(win, board_idx)
                return win

        # check diagonals
        curr_diag = []
        for row in board:
            curr_diag.append(row[board.index(row)])

        win = self.check_win_vals(curr_diag)
        if True in win:
            self.log_won_boards(win, board_idx)
            return win

        counter = 2
        curr_diag = []
        for row in board:
            curr_diag.append(row[counter])
            counter -= 1

        win = self.check_win_vals(curr_diag)
        if True in win:
            self.log_won_boards(win, board_idx)
            return win

        else:
            return [False]

    def check_won_big(self):
        """Checks to see if someone won the game"""
        boards = [None for i in range(9)]
        for board in range(len(self.board)):
            won = self.check_won_small(self.board[board])
            if True in won:
                boards[board] = won[-1]

        main_board = [[boards[0], boards[1], boards[2]],
                      [boards[3], boards[4], boards[5]],
                      [boards[6], boards[7], boards[8]]]

        # coordinates for x and o markers for won boards
        # here instead of draw_board because it would take an extra turn to update
        main_coords = {0: (25, 25),  1: (157, 25),  2: (289, 25),
                       3: (25, 157), 4: (157, 157), 5: (289, 157),
                       6: (25, 289), 7: (157, 289), 8: (289, 289)}

        # Displays won boards
        for sboard in self.x_boards:
            self.screen.blit(self.x_img, main_coords[sboard])

        for sboard in self.o_boards:
            self.screen.blit(self.o_img, main_coords[sboard])

        return self.check_won_small(main_board, True)

    def draw_board(self):
        """Displays Xs and Os on the board"""
        board = self.conv_rows()

        for row in range(len(board)):
            for square in range(len(board[row])):
                if board[row][square] == "X":
                    self.screen.blit(self.x_img_small, (45 * square + 4, 45 * row + 4))
                elif board[row][square] == "O":
                    self.screen.blit(self.o_img_small, (45 * square + 4, 45 * row + 4))

        # code to show who on a board is in the check_won_big

        pg.display.update()


    def check_click(self):
        """Finds where the user clicks and translates it to which square they clicked"""
        x, y = pg.mouse.get_pos()  # position of the click

        pos = []

        # Finds which board was clicked
        if (x < (self.size / 3)):
            col = 0

        elif (x < (self.size / 3 * 2)):
            col = 1

        elif (x < self.size):
            col = 2

            # get row of mouse click (1-3)
        if (y < (self.size / 3)):
            row = 0

        elif (y < (self.size / 3 * 2)):
            row = 1

        elif (y < self.size):
            row = 2

        pos.append([col, row])

        col += 1
        row += 1

        small_sizex = (self.size / 3) * col
        small_sizey = (self.size / 3) * row

        cell = 400 / 3 / 3  # = 44.44 repeating

        # Finds which cell they clicked
        if (x < small_sizex - (cell * 2)):
            col = 0

        elif (x < small_sizex - (cell * 1)):
            col = 1

        elif (x < small_sizex):
            col = 2

            # get row of mouse click (1-3)
        if (y < small_sizey - (cell * 2)):
            row = 0

        elif (y < small_sizey - (cell * 1)):
            row = 1

        elif (y < small_sizey):
            row = 2

        pos.append([col, row])

        # Translates the row and column to which board they clicked, also used to find next current board
        small_boards = {'[0, 0]': 0, '[1, 0]': 1, '[2, 0]': 2,
                        '[0, 1]': 3, '[1, 1]': 4, '[2, 1]': 5,
                        '[0, 2]': 6, '[1, 2]': 7, '[2, 2]': 8}

        #print("POS: " + str(pos[0]))

        small_board = small_boards[str(pos[0])]

        # If the user clicked an invalid board, do nothing
        if (self.curr_board is not None) and (small_board != self.curr_board):
            return

        if self.curr_board is None and (small_board in self.x_boards or small_board in self.o_boards):
            return

        # If that space is legal:
        if ((row or col is not None) and self.board[small_board][pos[1][1]][pos[1][0]] is None):
            self.board[small_board][pos[1][1]][pos[1][0]] = "X"  # Place their marker

            self.turn_count += 1  # Increase the turn count

            # Swap the current player
            if self.curr_player == "X":
                self.curr_player = "O"
            else:
                self.curr_player = "X"

            # Update the current board
            self.curr_board = small_boards[str(pos[1])]
            if self.curr_board in self.x_boards or self.curr_board in self.o_boards:
                self.curr_board = None
            print("Curr board after click (Legal board for AI): " + str(self.curr_board))

            # Draw the new board and check if someone won
            self.draw_board()
            self.check_won_big()

            return True

    def randomize_board(self):
        """Picks a random board in the case one is already captured. Returns the new current board as redundancy"""
        while True:
            new_board = random.randint(0, 8)

            if new_board in self.x_boards or new_board in self.o_boards:
                pass

            else:
                self.curr_board = new_board
                return self.curr_board


    # ------------------------------------------------------------------------------------------------------------------
    # Code below this line is used for minimax and moves by the AI.
    # ------------------------------------------------------------------------------------------------------------------

    def eval_board(self, board):
        """Checks if someone won the small board, just outputs who won if someone did"""

        # Checks rows
        for row in board:
            if row.count("X") == 3:
                return "X"
            elif row.count("O") == 3:
                return "O"

        # Checks columns
        for i in range(3):
            col = []
            col.append(board[0][i])
            col.append(board[1][i])
            col.append(board[2][i])

            if col.count("X") == 3:
                return "X"
            elif col.count("O") == 3:
                return "O"

        # Checks top left to bottom right diagonal
        diag = []
        diag.append(board[0][0])
        diag.append(board[1][1])
        diag.append(board[2][2])

        if diag.count("X") == 3:
            return "X"
        elif diag.count("O") == 3:
            return "O"

        # Checks top right to bottom left diagonal
        diag = []
        diag.append(board[0][2])
        diag.append(board[1][1])
        diag.append(board[2][0])

        if diag.count("X") == 3:
            return "X"
        elif diag.count("O") == 3:
            return "O"

        # No one has won
        return False

    def possible_moves(self, board):
        """
        Returns a list of possible moves (free spaces)
        Shuffles the list before returning it to induce some randomness in early moves or equally values moves
        If a board is winnable in this move, only return the move that would win the board
        Returns all open squares if none others are optimal

        NOTE: The changes to this functions had a huge impact on my runtime, it is now ~0.05 seconds at most.
        See commented code below for old method
        New method forces the completion of a row/column/diagonal if it is possible
        If no completion is possible, creates a list of optimal moves to set it up
        Chance for minimax to determine best move is much higher, before seemed random
        """
        possible = []
        has_o = [[], [], []]  # placeholder to see what parts of the board can be set up for a win
        for row in range(len(board)):
            # If a row can be finished, only return the empty spot
            if board[row].count("O") == 2 and None in board[row]:
                return [[row, board[row].index(None)]]

            elif board[row].count("O") == 1 and board[row].count(None) == 2:
                has_o[0].append(row)

            for col in range(len(board[row])):
                if board[row][col] is None:
                    possible.append([row, col])

        # If the board is empty, only return corners
        if len(possible) == 9:
            corners = [[0, 0], [0, 2], [2, 0], [2, 2]]
            random.shuffle(corners)
            return corners

        # Checks for winnable column
        for i in range(3):
            col = []
            col.append(board[0][i])
            col.append(board[1][i])
            col.append(board[2][i])

            if col.count("O") == 2 and None in col:
                return [[col.index(None), i]]

            elif col.count("O") == 1 and col.count(None) == 2:
                has_o[1].append(i)

        # Checks for winnable diagonals
        # Checks top left to bottom right diagonal
        diag = []
        diag.append(board[0][0])
        diag.append(board[1][1])
        diag.append(board[2][2])

        if diag.count("O") == 2 and None in diag:
            return [[diag.index(None), diag.index(None)]]

        elif diag.count("O") == 1 and diag.count(None) == 2:
            has_o[2].append(0)

        # Checks top right to bottom left diagonal
        diag = []
        diag.append(board[0][2])
        diag.append(board[1][1])
        diag.append(board[2][0])

        if diag.count("O") == 2 and None in diag:
            return [[diag.index(None), abs(diag.index(None) - 2)]]

        elif diag.count("O") == 1 and diag.count(None) == 2:
            has_o[2].append(1)

        potential = []  # a list of potentially optimal moves, way longer than it has to be

        for row in has_o[0]:
            potential.extend([[row, 0], [row, 1], [row, 2]])

        for col in has_o[1]:
            potential.extend([[0, col], [1, col], [2, col]])

        if 0 in has_o[2]:
            potential.extend([[0, 0], [1, 1], [2, 2]])
        if 1 in has_o[2]:
            potential.extend([[0, 2], [1, 1], [2, 0]])

        optimal = []  # a list of optimal moves if the function makes it this far

        # only adds legal moves to optimal
        for coord in potential:
            if coord in possible:
                optimal.append(coord)

        """
        OLD CODE: Does not restrict available moves
        possible = []
        for row in range(len(board)):
            for col in range(len(board[row])):
                if board[row][col] is None:
                    possible.append([row, col])

        # Shuffles the list
        try:
            random.shuffle(possible)
        except TypeError:
            pass

        return possible
        """

        if len(optimal) != 0:
            # Shuffles the list
            # Has to be below commented code, sorry for poor readability here
            try:
                random.shuffle(optimal)
            except TypeError:
                pass

            return optimal

        else:
            # placeholder in case there are no optimal moves
            return possible


    def make_temp_move(self, board, move, player):
        """Makes a move, used for copied board"""
        self.board[board][move[0]][move[1]] = player

    def make_move(self, board, move, player):
        """makes a temp move (OUTDATED)"""
        board[move[0]][move[1]] = player

    def unmake_move(self, board, move):
        """Undoes a move"""
        board[move[0]][move[1]] = None

    def minimax(self, board, max_depth, player, depth=0):
        """
        Runs minimax on a small board, to be passed in.
        True for X, False for O
        """

        # If the board has been won return a value for X or O
        if self.eval_board(board) == "O":
            return 1
        elif self.eval_board(board) == "X":
            return -1

        elif player:  # Player O
            best = float("-inf")  # Best possible value for X

            choices = self.possible_moves(board)  # Generates a list of possible moves
            for i in range(len(choices)):  # For every possible choice
                board_copy = copy.copy(board)  # copy the board
                self.make_move(board_copy, choices[i], "O")  # Make a move on the copied board
                possible = self.minimax(board_copy, max_depth, False, depth + 1)  # Recursively runs minimax for X

                # If the possible score is larger than the best score, update the best move
                if possible > best:
                    best = possible

                    if depth == 0:
                        self.best_move = choices[i]  # Update the best move

                self.unmake_move(board_copy, choices[i])  # Undoes the move

        else:  # Player X
            best = float("inf")  # Best possible value for O

            choices = self.possible_moves(board)  # Generates a list of possible moves
            for i in range(len(choices)): # For every possible choice
                board_copy = copy.copy(board)  # copy the board
                self.make_move(board_copy, choices[i], "X")  # Make a move on the copied board
                possible = self.minimax(board_copy, max_depth, True, depth + 1)  # Recursively runs minimax for O

                # If the possible score is larger than the best score, update the best move
                if possible < best:
                    best = possible

                    if depth == 0:
                        self.best_move = choices[i]  # Update the best move

                self.unmake_move(board_copy, choices[i])  # Undoes the move

        return best  # Return the best value

    def make_best_move(self, board, move, player):
        """Makes best move for AI, determined by minimax"""
        print("MADE MOVE FOR " + player + " in board " + str(self.curr_board))
        board[move[0]][move[1]] = player

        board_translation = {'[0, 0]': 0, '[1, 0]': 1, '[2, 0]': 2,
                             '[0, 1]': 3, '[1, 1]': 4, '[2, 1]': 5,
                             '[0, 2]': 6, '[1, 2]': 7, '[2, 2]': 8}

        self.curr_board = board_translation[str([move[1], move[0]])]  # Updates the current board
        if self.curr_board in self.x_boards or self.curr_board in self.o_boards:
            self.curr_board = None

        # Draws the board and checks if someone won.
        self.draw_board()
        self.check_won_big()


def main():
    game_board = Board()


if __name__ == '__main__':
        main()
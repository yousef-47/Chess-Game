import copy, math, random

from const import *
from piece import *
from book import Book


class AI:

    def __init__(self, engine='book', depth= 3):
        self.engine = engine
        self.depth = depth
        self.book = Book()
        self.color = 'black'
        self.game_moves = [] # Moves played so far
        self.explored = 0

    # ----
    # BOOK
    # ----

    def book_move(self):
        move = self.book.next_move(self.game_moves, weighted=True)
        return move



    # ------------------
    # HEURISTIC 1: POSITIONAL HEATMAPS
    # ------------------
    def heatmap(self, piece, row, col):
        """Heuristic 1: Piece-Square Tables (positional bonuses/penalties)."""
        hmp = 0
        if piece.name == 'pawn':
            if piece.color == 'black':
                hmp = [
                    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                    [0.02, 0.01, 0.00, 0.00, 0.00, 0.00, 0.01, 0.02],
                    [0.01, 0.01, 0.03, 0.06, 0.06, 0.03, 0.01, 0.01],
                    [0.02, 0.02, 0.04, 0.07, 0.07, 0.04, 0.02, 0.02],
                    [0.03, 0.03, 0.05, 0.08, 0.08, 0.05, 0.03, 0.03],
                    [0.07, 0.07, 0.08, 0.09, 0.09, 0.08, 0.07, 0.07],
                    [0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10],
                    [9.00, 9.00, 9.00, 9.00, 9.00, 9.00, 9.00, 9.00],
                ]
            elif piece.color == 'white':
                hmp = [
                    [9.00, 9.00, 9.00, 9.00, 9.00, 9.00, 9.00, 9.00],
                    [0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10],
                    [0.07, 0.07, 0.08, 0.09, 0.09, 0.08, 0.07, 0.07],
                    [0.03, 0.03, 0.05, 0.08, 0.08, 0.05, 0.03, 0.03],
                    [0.02, 0.02, 0.04, 0.07, 0.07, 0.04, 0.02, 0.02],
                    [0.01, 0.01, 0.03, 0.06, 0.06, 0.03, 0.01, 0.01],
                    [0.02, 0.01, 0.00, 0.00, 0.00, 0.00, 0.01, 0.02],
                    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                ]

        elif piece.name == 'knight':
            hmp = [
                [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                [0.00, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.00],
                [0.00, 0.02, 0.06, 0.05, 0.05, 0.06, 0.02, 0.00],
                [0.00, 0.03, 0.05, 0.10, 0.10, 0.05, 0.03, 0.00],
                [0.00, 0.03, 0.05, 0.10, 0.10, 0.05, 0.03, 0.00],
                [0.00, 0.02, 0.06, 0.05, 0.05, 0.06, 0.02, 0.00],
                [0.00, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.00],
                [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            ]

        elif piece.name == 'bishop':
            hmp = [
                [0.02, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.02],
                [0.01, 0.05, 0.03, 0.03, 0.03, 0.03, 0.05, 0.01],
                [0.01, 0.03, 0.07, 0.05, 0.05, 0.07, 0.03, 0.01],
                [0.01, 0.03, 0.05, 0.10, 0.10, 0.05, 0.03, 0.01],
                [0.01, 0.03, 0.05, 0.10, 0.10, 0.05, 0.03, 0.01],
                [0.01, 0.03, 0.07, 0.05, 0.05, 0.07, 0.03, 0.01],
                [0.01, 0.05, 0.03, 0.03, 0.03, 0.03, 0.05, 0.01],
                [0.02, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.02],
            ]

        elif piece.name == 'king':
            if piece.color == 'black':
                hmp = [
                    [0.05, 0.50, 0.10, 0.00, 0.00, 0.00, 0.10, 0.05],
                    [0.02, 0.02, 0.00, 0.00, 0.00, 0.00, 0.02, 0.02],
                    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                ]

            elif piece.color == 'white':
                hmp = [
                    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                    [0.02, 0.02, 0.00, 0.00, 0.00, 0.00, 0.02, 0.02],
                    [0.05, 0.50, 0.10, 0.00, 0.00, 0.00, 0.10, 0.05],
                ]

        else:
            hmp = [
                [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            ]

        eval = -hmp[row][col] if piece.color == 'black' else hmp[row][col]
        return eval

    # ------------------
    # HEURISTIC 2: THREATS & MOBILITY
    # ------------------
    def threats(self, board, piece):
        """Heuristic 2: Reward attacks on high-value pieces (e.g., checks)."""
        eval = 0
        for move in piece.valid_moves:
            attacked = board.squares[move.final.row][move.final.col]
            if attacked.has_piece():
                if attacked.piece.color != piece.color:
                    # checks
                    if attacked.piece.name == 'king':
                        eval += attacked.piece.value / 10500

                    # threat
                    else:
                        eval += attacked.piece.value / 45

        return eval

    def static_eval(self, board):
        # var
        eval = 0

        for row in range(ROWS):
            for col in range(COLS):
                if board.squares[row][col].has_piece():
                    # piece
                    piece = board.squares[row][col].piece
                    # white - black
                    eval += piece.value
                    # heatmap
                    eval += self.heatmap(piece, row, col)
                    # moves
                    if piece.name != 'queen':
                        eval += 0.01 * len(piece.valid_moves)
                    else:
                        eval += 0.003 * len(piece.valid_moves)
                    # checks
                    eval += self.threats(board, piece)

        eval = round(eval, 5)
        return eval

    def get_moves(self, board, color):
        moves = []
        for row in range(ROWS):
            for col in range(COLS):
                square = board.squares[row][col]
                if square.has_team_piece(color):
                    board.calc_valid(square.piece, square.row, square.col)
                    moves += square.piece.valid_moves

        return moves

    # -------
    # MINIMAX
    # -------

    def minimax(self, board, depth, maximizing, alpha, beta):

        if depth == 0:
            return self.static_eval(board), None

        """
                    Minimax with Alpha-Beta pruning.
                    Args:
                        alpha: Best score for maximizing player.
                        beta: Best score for minimizing player.
                    Returns:
                        Tuple (evaluation, best_move).
        """

        if maximizing:
            max_eval = -math.inf
            best_move = None
            moves = self.get_moves(board, 'white')
            if not moves:
                return self.static_eval(board), None

            for move in moves:
                self.explored += 1
                temp_board = copy.deepcopy(board)
                piece = temp_board.squares[move.initial.row][move.initial.col].piece
                temp_board.move(piece, move)
                eval = self.minimax(temp_board, depth - 1, False, alpha, beta)[0]
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, max_eval)
                if beta <= alpha:
                    break

            return max_eval, best_move

        else:
            min_eval = math.inf
            best_move = None
            moves = self.get_moves(board, 'black')
            if not moves:
                return self.static_eval(board), None

            for move in moves:
                self.explored += 1
                temp_board = copy.deepcopy(board)
                piece = temp_board.squares[move.initial.row][move.initial.col].piece
                temp_board.move(piece, move)
                eval = self.minimax(temp_board, depth - 1, True, alpha, beta)[0]
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, min_eval)
                if beta <= alpha:
                    break

            return min_eval, best_move # eval, and move

    # def minimax(self, board, depth, maximizing):
    #     """
    #     Pure Minimax algorithm without Alpha-Beta pruning.
    #     Args:
    #         board: Current board state
    #         depth: Remaining search depth
    #         maximizing: True if current player is maximizing (white)
    #     Returns:
    #         Tuple (evaluation, best_move)
    #     """
    #     if depth == 0:
    #         return self.static_eval(board), None
    #
    #     if maximizing:
    #         max_eval = -math.inf
    #         best_move = None
    #         moves = self.get_moves(board, 'white')
    #         if not moves:
    #             return self.static_eval(board), None
    #
    #         for move in moves:
    #             self.explored += 1
    #             temp_board = copy.deepcopy(board)
    #             piece = temp_board.squares[move.initial.row][move.initial.col].piece
    #             temp_board.move(piece, move)
    #             eval = self.minimax(temp_board, depth - 1, False)[0]
    #             if eval > max_eval:
    #                 max_eval = eval
    #                 best_move = move
    #
    #         return max_eval, best_move
    #
    #     else:
    #         min_eval = math.inf
    #         best_move = None
    #         moves = self.get_moves(board, 'black')
    #         if not moves:
    #             return self.static_eval(board), None
    #
    #         for move in moves:
    #             self.explored += 1
    #             temp_board = copy.deepcopy(board)
    #             piece = temp_board.squares[move.initial.row][move.initial.col].piece
    #             temp_board.move(piece, move)
    #             eval = self.minimax(temp_board, depth - 1, True)[0]
    #             if eval < min_eval:
    #                 min_eval = eval
    #                 best_move = move
    #
    #         return min_eval, best_move

    # ---------
    # MAIN EVAL
    # ---------

    def eval(self, main_board):
        self.explored = 0

        # add last move
        last_move = main_board.last_move
        self.game_moves.append(last_move)

        # # book engine
        if self.engine == 'book':
            move = self.book_move()
            # no more book moves ?
            if move is None:
                self.engine = 'minimax'

        # minimax engine
        if self.engine == 'minimax':
            # printing
            print('\nFinding best move...')

            # minimax initial call
            is_maximizing = self.color == 'white'

            eval, move = self.minimax(main_board, self.depth, is_maximizing, -math.inf, math.inf) # minimax with alpha-beta
            # eval, move = self.minimax(main_board, self.depth, is_maximizing) # minimax without alpha-beta


            # printing
            print('\n- Initial eval:', self.static_eval(main_board))
            print('- Final eval:', eval)
            print('- Boards explored', self.explored)
            if eval >= 5000: print('* White MATE!')
            if eval <= -5000: print('* Black MATE!')

        # append
        self.game_moves.append(move)

        return move
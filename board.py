import copy
import sys
from const import *
from square import *
from piece import *
from move import *

class Board:
    def __init__(self):
        self.squares = [[Square(row, col) for col in range(COLS)] for row in range(ROWS)]
        self.last_move = None
        self._add_pieces('white')
        self._add_pieces('black')

    def move(self, piece, move, screen=None, simulate=False):
        initial = move.initial
        final = move.final

        # Remove piece from initial square and place it on final square
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        promoted = False

        # Handle pawn promotion (only in real games, not simulation)
        if isinstance(piece, Pawn) and not simulate:
            if final.row == 0 or final.row == 7:
                if screen is None:
                    # AI or simulation move, auto promote to queen
                    promote_to = 'queen'
                else:
                    promote_to = self.ask_promotion(screen, piece.color)
                self.check_promotion(piece, final, promote_to)
                promoted = True

        # Handle castling (only in real games, not simulation)
        if isinstance(piece, King) and not simulate:
            if self.castling(initial, final, piece):
                diff = final.col - initial.col
                row = initial.row
                if diff < 0:
                    # Queenside
                    rook = self.squares[row][0].piece
                    rook_move = Move(Square(row, 0), Square(row, 3))
                else:
                    # Kingside
                    rook = self.squares[row][7].piece
                    rook_move = Move(Square(row, 7), Square(row, 5))

                if rook:
                    self.move(rook, rook_move, simulate=True)

        # move
        piece.moved = True

        # clear valid moves
        piece.clear_moves()

        # set last move
        self.last_move = move
        return promoted

    def is_mate(self, color):
        for row in range(ROWS):
            for col in range(COLS):
                square = self.squares[row][col]
                if square.has_piece():
                    piece = square.piece
                    # Only check the current player's pieces
                    if piece.color != color:
                        continue
                    self.calc_valid(piece, row, col, bool= True)
                    if piece.valid_moves:
                        return False  # At least one valid move available
        return True  # No valid moves found, it's checkmate

    def is_stalemate(self, color):
        if self.is_in_check(color):
            return False  # Cannot be stalemate if the king is in check

        for row in range(ROWS):
            for col in range(COLS):
                square = self.squares[row][col]
                if square.has_piece() and square.piece.color == color:
                    piece = square.piece
                    self.calc_valid(piece, row, col, bool=True)
                    if piece.valid_moves:
                        return False  # At least one legal move exists
        return True  # Not in check and no legal moves → stalemate

    def insufficient_material(self):
        # if the remaining pieces in the board are just the kings
        pieces = []

        for row in range(ROWS):
            for col in range(COLS):
                square = self.squares[row][col]
                if square.has_piece():
                    piece = square.piece
                    pieces.append(piece)

        # King vs King
        if len(pieces) == 2:
            return all(isinstance(p, King) for p in pieces)

        return False

    def castling(self, initial, final, piece):
        return abs(initial.col - final.col) == 2 and isinstance(piece, King)

    def check_valid(self, piece, move):
        return move in piece.valid_moves

    def find_king(self, board, color):
        for row in range(ROWS):
            for col in range(COLS):
                piece = board.squares[row][col].piece
                if isinstance(piece, King) and piece.color == color:
                    return Square(row, col)
        return None  # Return None instead of False for consistency

    def in_check(self, piece, move):
        temp_board = copy.deepcopy(self)
        temp_piece = temp_board.squares[move.initial.row][move.initial.col].piece
        temp_board.move(temp_piece, move, simulate=True)

        # Find king position after the move
        king_pos = self.find_king(temp_board, temp_piece.color)
        if not king_pos:
            return False
        # Check all rival pieces if they can attack king
        for row in range(ROWS):
            for col in range(COLS):
                sq = temp_board.squares[row][col]
                if sq.has_rival(piece.color):
                    p = sq.piece
                    temp_board.calc_valid(p, row, col, bool=False)
                    for m in p.valid_moves:
                        if m.final.row == king_pos.row and m.final.col == king_pos.col:
                            return True
        return False

    def is_in_check(self, color):
        king_pos = self.find_king(self, color)
        if not king_pos:
            return False
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.squares[row][col].piece
                if piece and piece.color != color:
                    self.calc_valid(piece, row, col, bool=False)
                    for move in piece.valid_moves:
                        if move.final.row == king_pos.row and move.final.col == king_pos.col:
                            return True
        return False

    def check_promotion(self, piece, final, promote_to='Queen'):
        if final.row == 0 or final.row == 7:
            if promote_to == 'Queen':
                self.squares[final.row][final.col].piece = Queen(piece.color)
            elif promote_to == 'Rook':
                self.squares[final.row][final.col].piece = Rook(piece.color)
            elif promote_to == 'Bishop':
                self.squares[final.row][final.col].piece = Bishop(piece.color)
            elif promote_to == 'Knight':
                self.squares[final.row][final.col].piece = Knight(piece.color)

    def calc_valid(self, piece, row, col, bool=True):
        piece.clear_moves()

        def pawn_moves():
            steps = 1 if piece.moved else 2
            start = row + piece.dir
            end = row + (piece.dir * (1 + steps))
            for possible_row in range(start, end, piece.dir):
                if Square.in_range(possible_row):
                    if self.squares[possible_row][col].is_empty():
                        move = Move(Square(row, col), Square(possible_row, col))
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_moves(move)
                        else:
                            piece.add_moves(move)
                    else:
                        break
                else:
                    break

            # Diagonal capture moves
            diag_cols = [col - 1, col + 1]
            possible_row = row + piece.dir
            for c in diag_cols:
                if Square.in_range(possible_row, c) and self.squares[possible_row][c].has_rival(piece.color):
                    move = Move(Square(row, col), Square(possible_row, c, self.squares[possible_row][c].piece))
                    if bool:
                        if not self.in_check(piece, move):
                            piece.add_moves(move)
                    else:
                        piece.add_moves(move)

        def knight_moves():
            candidates = [
                (row - 1, col + 2), (row - 1, col - 2),
                (row - 2, col + 1), (row - 2, col - 1),
                (row + 1, col + 2), (row + 1, col - 2),
                (row + 2, col + 1), (row + 2, col - 1)
            ]
            for r_, c_ in candidates:
                if Square.in_range(r_, c_) and self.squares[r_][c_].is_empty_or_rival(piece.color):
                    move = Move(Square(row, col), Square(r_, c_))
                    if bool:
                        if not self.in_check(piece, move):
                            piece.add_moves(move)
                    else:
                        piece.add_moves(move)

        def straight_moves(directions):
            for dr, dc in directions:
                r_, c_ = row + dr, col + dc
                while Square.in_range(r_, c_):
                    move = Move(Square(row, col), Square(r_, c_))
                    if self.squares[r_][c_].is_empty():
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_moves(move)
                        else:
                            piece.add_moves(move)
                    elif self.squares[r_][c_].has_rival(piece.color):
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_moves(move)
                        else:
                            piece.add_moves(move)
                        break
                    else:
                        break
                    r_ += dr
                    c_ += dc

        def king_moves():
            moves = [
                (row + 1, col), (row - 1, col),
                (row, col + 1), (row, col - 1),
                (row + 1, col + 1), (row + 1, col - 1),
                (row - 1, col + 1), (row - 1, col - 1)
            ]
            for r_, c_ in moves:
                if Square.in_range(r_, c_) and self.squares[r_][c_].is_empty_or_rival(piece.color):
                    move = Move(Square(row, col), Square(r_, c_))
                    if bool:
                        if not self.in_check(piece, move):
                            piece.add_moves(move)
                    else:
                        piece.add_moves(move)

            # Castling moves
            if not piece.moved:
                # Queenside castling
                left_rook = self.squares[row][0].piece
                if isinstance(left_rook, Rook) and not left_rook.moved:
                    if all(not self.squares[row][c].has_piece() for c in range(1, 4)):
                        moveK = Move(Square(row, col), Square(row, 2))
                        moveR = Move(Square(row, 0), Square(row, 3))
                        if bool:
                            if (not self.in_check(piece, moveK) and not self.in_check(left_rook, moveR)):
                                piece.add_moves(moveK)
                                left_rook.add_moves(moveR)
                        else:
                            piece.add_moves(moveK)
                            left_rook.add_moves(moveR)

                # Kingside castling
                right_rook = self.squares[row][7].piece
                if isinstance(right_rook, Rook) and not right_rook.moved:
                    if all(not self.squares[row][c].has_piece() for c in range(5, 7)):
                        moveK = Move(Square(row, col), Square(row, 6))
                        moveR = Move(Square(row, 7), Square(row, 5))
                        if bool:
                            if (not self.in_check(piece, moveK) and not self.in_check(right_rook, moveR)):
                                piece.add_moves(moveK)
                                right_rook.add_moves(moveR)
                        else:
                            piece.add_moves(moveK)
                            right_rook.add_moves(moveR)

        if isinstance(piece, Pawn):
            pawn_moves()

        if isinstance(piece, Bishop):
            straight_moves([(1, 1), (1, -1), (-1, 1), (-1, -1)])

        if isinstance(piece, Rook):
            straight_moves([(1, 0), (-1, 0), (0, 1), (0, -1)])

        if isinstance(piece, Knight):
            knight_moves()

        if isinstance(piece, Queen):
            straight_moves([(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)])

        if isinstance(piece, King):
            king_moves()

    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)
        for col in range(COLS):
            self.squares[row_pawn][col].piece = Pawn(color)
        self.squares[row_other][0].piece = Rook(color)
        self.squares[row_other][7].piece = Rook(color)
        self.squares[row_other][1].piece = Knight(color)
        self.squares[row_other][6].piece = Knight(color)
        self.squares[row_other][2].piece = Bishop(color)
        self.squares[row_other][5].piece = Bishop(color)
        self.squares[row_other][3].piece = Queen(color)
        self.squares[row_other][4].piece = King(color)

    @staticmethod
    def ask_promotion(screen, color):
        import pygame
        running = True
        width, height = 420, 100
        x = (WIDTH - width) // 2
        y = (HEIGHT - height) // 2
        button_width = 100
        button_height = 100
        padding = 5

        pieces = ['Queen', 'Rook', 'Bishop', 'Knight']
        buttons = []

        promotion_pieces = {
            'Queen': Queen(color),
            'Rook': Rook(color),
            'Bishop': Bishop(color),
            'Knight': Knight(color)
        }

        piece_images = {}
        for name, piece in promotion_pieces.items():
            img = pygame.image.load(piece.image_path)
            img = pygame.transform.scale(img, (75, 75))
            piece_images[name] = img

        for i, name in enumerate(pieces):
            rect = pygame.Rect(x + i * (button_width + padding), y, button_width, button_height)
            buttons.append((rect, name))

        while running:
            pygame.draw.rect(screen, (240, 240, 240), (x - 10, y - 10, width + 20, height + 20))
            for rect, name in buttons:
                pygame.draw.rect(screen, (200, 200, 200), rect)
                image = piece_images[name]
                img_rect = image.get_rect(center=rect.center)
                screen.blit(image, img_rect)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    for rect, name in buttons:
                        if rect.collidepoint(mouse_pos):
                            return name
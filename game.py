from ai import AI
from dragger import *
from const import *
import pygame
from board import Board
from square import *

from config import Config



class Game:
    def __init__(self):
        self.next_player = 'white'
        self.gamemode = 'ai'
        self.selected_piece = None
        self.ai = AI()
        self.board = Board()
        self.dragger = Dragger()
        self.config = Config()
        self.game_over = False
    # Show methods
    def show_bg(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                square = self.board.squares[row][col]
                piece = square.piece

                if(row + col) % 2 == 0:
                    color = LIGHT_SQUARE # light green

                else:
                    color = DARK_SQUARE # dark green

                    # Highlight red if it's a king in check
                if isinstance(piece, King) and self.board.is_in_check(piece.color):
                    color = '#ce3535'  # bright red

                rect = (col * SQSIZE, row * SQSIZE, SQSIZE,  SQSIZE)
                pygame.draw.rect(surface, color, rect)

                if col == 0:
                    # color
                    color = DARK_SQUARE if row % 2 == 0 else LIGHT_SQUARE
                    # coordinates n
                    lbl = self.config.font.render(str(ROWS - row), 1, color)
                    surface.blit(lbl, (5, 5 + row * SQSIZE))

                # col coordinates
                if row == 7:
                    # coordinates
                    # color
                    color = DARK_SQUARE if (row + col) % 2 == 0 else LIGHT_SQUARE
                    # coordinates
                    lbl = self.config.font.render(Square.get_alphacol(col), 1, color)
                    surface.blit(lbl, (col * SQSIZE + SQSIZE - 20, HEIGHT - 20))

    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece

                    #keeps every piece in its position except the carried one
                    if piece is not self.dragger.piece:
                        piece.set_image_path(size=80)
                        img = pygame.image.load(piece.image_path).convert_alpha()
                        img = pygame.transform.smoothscale(img, (80, 80))  # Optional: dynamically adjust size
                        img_center = col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2
                        piece.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, piece.texture_rect)

    def show_moves(self, surface):
        if self.dragger.dragging:
            piece = self.dragger.piece
            for move in piece.valid_moves:
                # Safety check: will this move result in a legal state?
                if not self.board.in_check(piece, move):
                    center_x = move.final.col * SQSIZE + SQSIZE // 2
                    center_y = move.final.row * SQSIZE + SQSIZE // 2

                    # accessing the required square
                    target_square = self.board.squares[move.final.row][move.final.col]
                    color = MOVE_DOT_COLOR

                    # if the piece exists and it's a rival piece
                    if target_square.piece and piece.color != target_square.piece.color:
                        # draw a ring for captures
                        pygame.draw.circle(surface, color, (center_x, center_y), 47, 6)
                    else:
                        # draw a dot for normal moves
                        pygame.draw.circle(surface, color, (center_x, center_y), 15)

    # Determine the next turn player
    def next_turn(self):
        self.next_player = 'white' if self.next_player == 'black' else 'black'

    def show_last_move(self,surface):
        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final
            for pos in [initial, final]:

                # color
                color = LAST_MOVE_LIGHT if (pos.row + pos.col) % 2 == 0 else LAST_MOVE_DARK

                # rect
                rect = (pos.col * SQSIZE , pos.row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

    def play_sound(self, Type= None):
        if Type == 'capture':
            self.config.capture.play()
        elif Type == 'check':
            self.config.move_check.play()
        elif Type == 'mate':
            self.config.mate.play()
        elif Type == 'castle':
            self.config.castle.play()
        elif Type == 'promote':
            self.config.promote.play()
        elif Type == 'move':  # <--- Add this line
            self.config.move_sound.play()

    def ai_move(self, screen):
        # Only act if it is AI's turn
        if self.gamemode != 'ai' or self.next_player != self.ai.color:
            return False

        move = self.ai.eval(self.board)
        if not move:
            print("AI has no valid moves!")
            return False

        initial = move.initial
        final = move.final
        ai_piece = self.board.squares[initial.row][initial.col].piece

        captured = self.board.squares[final.row][final.col].has_piece()
        castled = self.board.castling(initial, final, ai_piece)
        promoted = self.board.move(ai_piece, move, screen)

        opponent_color = 'white' if ai_piece.color == 'black' else 'black'

        if self.board.is_in_check(opponent_color) and self.board.is_mate(opponent_color):
            self.play_sound('check')
            self.play_sound('mate')
        elif not self.board.is_in_check(opponent_color) and self.board.is_mate(opponent_color):
            self.play_sound('mate')
        elif self.board.is_in_check(opponent_color):
            self.play_sound('check')
        elif promoted:
            self.play_sound('promote')
        elif captured:
            self.play_sound('capture')
        elif castled:
            self.play_sound('castle')
        else:
            self.play_sound('move')

        # Update next player
        self.next_turn()

        return True

    def reset(self):
        return self.__init__()

    def select_piece(self, piece):
        self.selected_piece = piece

    def unselect_piece(self):
        self.selected_piece = None
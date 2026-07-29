import pygame
import sys
from const import *
from game import Game
from square import Square
from move import Move
# from config import Config

class Main:
    def __init__(self):
        pygame.init()
        pygame.mixer.music.load('assets/sounds/background.mp3')
        pygame.mixer.music.set_volume(1) # set volume
        pygame.mixer.music.play(-1)  # Loop forever
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess")
        self.game = Game()
        self.AI_MOVE_EVENT = pygame.USEREVENT + 1

    def redraw_all(self):
        self.game.show_bg(self.screen)
        self.game.show_last_move(self.screen)
        self.game.show_moves(self.screen)
        self.game.show_pieces(self.screen)

    def show_game_over_message(self, text):
        font = pygame.font.SysFont('Arial', 48)
        label = font.render(text, True, (200, 0, 0))
        rect = label.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(label, rect)
        pygame.display.update()

    def mainloop(self):
        screen = self.screen
        game = self.game
        dragger = self.game.dragger
        board = self.game.board
        ai = self.game.ai

        while True:
            self.redraw_all()

            if not game.game_over and dragger.dragging:
                dragger.update_blit(screen)

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    dragger.update_mouse(event.pos)

                    pos = event.pos
                    clicked_row = dragger.mouseY // SQSIZE
                    clicked_col = dragger.mouseX // SQSIZE

                    if not game.game_over and board.squares[clicked_row][clicked_col].has_piece():
                        piece = board.squares[clicked_row][clicked_col].piece
                        if piece.color == game.next_player:
                            board.calc_valid(piece, clicked_row, clicked_col)
                            dragger.save_initial(pos)
                            dragger.drag_piece(piece)
                            self.redraw_all()

                elif event.type == pygame.MOUSEMOTION:
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)  # fixed typo
                        self.redraw_all()
                        dragger.update_blit(screen)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)  # fixed typo

                        released_row = dragger.mouseY // SQSIZE
                        released_col = dragger.mouseX // SQSIZE

                        initial = Square(dragger.initial_row, dragger.initial_col)
                        final = Square(released_row, released_col)
                        move = Move(initial, final)

                        # Check move validity and legality (king safety)
                        if not game.game_over and board.check_valid(dragger.piece, move) and not board.in_check(dragger.piece, move):
                            captured = board.squares[final.row][final.col].has_piece()
                            castled = board.castling(initial, final, dragger.piece)
                            promoted = board.move(dragger.piece, move, screen)

                            opponent_color = 'white' if dragger.piece.color == 'black' else 'black'

                            # check mate
                            if board.is_in_check(opponent_color) and board.is_mate(opponent_color):
                                game.play_sound('check')
                                game.play_sound('mate')
                                self.show_game_over_message("Checkmate!")
                                game.game_over = True

                            # Stalemate (not in check but no valid moves)
                            elif not board.is_in_check(opponent_color) and board.is_stalemate(opponent_color):
                                game.play_sound('draw')
                                self.show_game_over_message("Draw!")
                                game.game_over = True
                            # Draw due to insufficient material
                            elif board.insufficient_material():
                                game.play_sound('draw')
                                self.show_game_over_message("Draw!")
                                game.game_over = True
                            elif board.is_in_check(opponent_color):
                                game.play_sound('check')

                            elif promoted:
                                game.play_sound('promote')

                            elif captured:
                                game.play_sound('capture')

                            elif castled:
                                game.play_sound('castle')

                            else:
                                game.play_sound('move')


                            game.next_turn()
                            game.show_bg(screen)
                            game.show_pieces(screen)
                            game.show_last_move(screen)
                            pygame.display.update()
                            dragger.undrag_piece(screen)
                            # Start AI move timer (500 ms delay)
                            pygame.time.set_timer(self.AI_MOVE_EVENT, 500)
                        else:
                            dragger.undrag_piece(screen)


                # Get AI move
                elif event.type == self.AI_MOVE_EVENT:
                    pygame.time.set_timer(self.AI_MOVE_EVENT, 0)  # stop the timer
                    if game.gamemode == 'ai' and game.next_player == game.ai.color:
                        ai_played = game.ai_move(screen)
                        if ai_played:
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_pieces(screen)
                            pygame.display.update()


                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game.reset()
                        game.game_over = False
                        # return the variables to its initial values
                        board = game.board
                        dragger = game.dragger
                        self.redraw_all()

                    elif event.key == pygame.K_m:
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.stop()
                        else:
                            pygame.mixer.music.play(-1)

                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.redraw_all()
            if dragger.dragging:
                dragger.update_blit(screen)
            pygame.display.update()


# Start the game
main = Main()
main.mainloop()
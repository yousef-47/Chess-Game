import pygame
from const import *
from piece import *

class Dragger:
    def __init__(self):
        self.piece = None
        self.dragging = False
        # mouse position on the screen
        self.mouseX = 0
        self.mouseY = 0
        # for undo/move validation
        self.initial_row = 0
        self.initial_col = 0

    def update_mouse(self, pos):
        self.mouseX, self.mouseY = pos # pos is a tuple of (x cord, y cord)

    #  Draws the piece at the mouse position while dragging.
    def update_blit(self, surface):
        self.piece.set_image_path(size=128)
        path = self.piece.image_path
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.smoothscale(img, (128, 128))
        img_center = (self.mouseX, self.mouseY)
        self.piece.texture_rect = img.get_rect(center=img_center)
        surface.blit(img, self.piece.texture_rect) # update the image on the screen

    def save_initial(self, pos):
        self.initial_row = pos[1] // SQSIZE
        self.initial_col = pos[0] // SQSIZE

    # in case we are carrying a piece
    def drag_piece(self, piece):
        self.piece = piece
        self.dragging = True

    # in case we dropped the piece
    def undrag_piece(self, surface):
        self.piece = None
        self.dragging = False
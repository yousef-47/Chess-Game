import os
import pygame

from sound import Sound

class Config:

    def __init__(self):

        self.font = pygame.font.SysFont('monospace', 18, bold=True)

        self.move_sound = Sound(
            os.path.join('assets/sounds/move-self.wav'))
        self.move_check = Sound(
            os.path.join('assets/sounds/move-check.wav'))
        self.castle = Sound(
            os.path.join('assets/sounds/castle.wav'))
        self.capture = Sound(
            os.path.join('assets/sounds/capture.wav'))
        self.mate = Sound(
            os.path.join('assets/sounds/game-end.wav'))
        self.promote = Sound(os.path.join('assets/sounds/promote.wav'))

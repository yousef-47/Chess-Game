import os
class Piece:
    def __init__(self, name,color, value, image_path = None, texture_rect = None):
        self.name = name
        self.color = color
        value_sign = 1 if color == 'white' else -1
        self.value = value * value_sign
        self.valid_moves = []
        self.moved = False
        self.image_path = image_path
        self.set_image_path()
        self.texture_rect = texture_rect

    # Defines the method to set the image path.
    def set_image_path(self, size = 80):

        # Construct the file path for the image
       self.image_path =  os.path.join(
           fr'C:\Users\N..C..C\PycharmProjects\PythonProject\ChessGame\Src\assets\images\imgs-{size}px\{self.color}_{self.name}.png')

    # A method that adds a move to the list of valid moves.
    def add_moves(self, move):
        self.valid_moves.append(move)

    def clear_moves(self):
        self.valid_moves = []

class Pawn(Piece):
    def __init__(self, color):
        self.dir = -1 if color == 'white' else 1
        super().__init__('pawn', color, 1.0)

class Knight(Piece):
    def __init__(self, color):
        super().__init__('knight', color, 3.0)

class Bishop(Piece):
    def __init__(self, color):
        super().__init__('bishop', color, 3.001)

class Rook(Piece):
    def __init__(self, color):
        super().__init__('rook', color, 5.0)

class Queen(Piece):
    def __init__(self, color):
        super().__init__('queen', color, 9.0)

class King(Piece):
    def __init__(self, color):
        self.l_rook = None
        self.r_rook = None
        super().__init__('king', color, 10000.0)

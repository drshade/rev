# The game
# 
WHITE = 'w'
BLACK = 'b'
EMPTY = '_'

WHITE_X = 'X'
BLACK_X = 'O'
EMPTY_X = ' ' # '·'
VALID_X = '?'

WIDTH  = 8
HEIGHT = 8

BLANK_BOARD = [EMPTY for x in range(WIDTH * HEIGHT)]

import json

class Reversi:
    def __init__(self):
        self._turn = WHITE
        self._board = BLANK_BOARD[:]
        self._complete = False
        self._moves = []
        
        # Starting configuration
        #
        self.place(3, 3, checked = False)
        self.place(3, 4, checked = False)
        self.place(4, 4, checked = False)
        self.place(4, 3, checked = False)
    
    def invert(self):
        state = self.state_to_string()
        TEMP = "_X_"
        state = state.replace('"%s"'%WHITE, '"%s"'%TEMP).replace('"%s"'%BLACK, '"%s"'%WHITE).replace('"%s"'%TEMP, '"%s"'%BLACK)
        self.state_from_string(state)

    def state_to_string(self):
        return json.dumps({
            "turn": self._turn,
            "board": self._board,
            "complete": self._complete,
            "moves": self._moves,
        })

    def state_from_string(self, jsonstring):
        state = json.loads(jsonstring)
        self._turn = state["turn"]
        self._board = state["board"]
        self._complete = state["complete"]
        self._moves = state["moves"]

    def stats(self):
        whitepoints = 0
        blackpoints = 0
        empty = 0
        for x in range(WIDTH):
            for y in range(HEIGHT):
                if self._board[(x * WIDTH) + y] == WHITE:
                    whitepoints += 1
                elif self._board[(x * WIDTH) + y] == BLACK:
                    blackpoints += 1
                elif self._board[(x * WIDTH) + y] == EMPTY:
                    empty += 1
        return (self._complete or empty == 0, whitepoints, blackpoints, empty)
    
    def place(self, x, y, checked = True):
        if checked and (x, y) not in self.all_valid_placements():
            raise Exception("Invalid move!")
            
        if checked:
            self._moves.append((self._turn, (x, y), self._board[:]))

            opponent_colour = self.opposite_color(self._turn)
            opponent_offsets = self.adjacent_offsets_matching(x, y, opponent_colour)
            for (ox, oy) in opponent_offsets:
                #print ("X = %d, Y = %d -> OX = %d, OY = %d"%(x, y, ox, oy))
                paths = self.find_path_to(x, y, ox, oy, self._turn)
                if paths:
                    for (px, py) in paths:
                        # Set all pathways to our colour
                        #
                        self._board[(px * WIDTH) + py] = self._turn
        
        self._board[(x * WIDTH) + y] = self._turn
        self._turn = BLACK if self._turn == WHITE else WHITE
      
    def skip(self):
        if len(self.all_valid_placements()) > 0:
            raise Exception("Invalid attempt to skip (valid moves found)!")
        self._turn = BLACK if self._turn == WHITE else WHITE
        
        # Check we not in deadlock (ie next move is also going to want to skip)
        if len(self.all_valid_placements()) == 0:
            #print("Game deadlocked, finishing")
            #print(self.draw())
            self._complete = True
    
    def get_at(self, x, y):
        return self._board[(x * WIDTH) + y]
    
    def on_board(self, x, y):
        return x < WIDTH and x >= 0 and y < HEIGHT and y >= 0
    
    def opposite_color(self, colour):
        return WHITE if colour == BLACK else BLACK
    
    def adjacent_offsets_matching(self, x, y, colour):
        tests = [
            (-1, -1), (0, -1), (+1, -1),
            (-1,  0),          (+1,  0),
            (-1, +1), (0, +1), (+1, +1)
        ]
        offsets = [(tx, ty) for (tx, ty) in tests 
                   if self.on_board((tx + x), (ty + y)) and self.get_at(tx + x, ty + y) == colour]
        return offsets
        
    def all_valid_placements(self):
        opponent_colour = self.opposite_color(self._turn)
        result = []
        for x in range(WIDTH):
            for y in range(HEIGHT):
                if self._board[(x * WIDTH) + y] == EMPTY:
                    opponent_offsets = self.adjacent_offsets_matching(x, y, opponent_colour)
                    for (ox, oy) in opponent_offsets:
                        #print ("X = %d, Y = %d -> OX = %d, OY = %d"%(x, y, ox, oy))
                        paths = self.find_path_to(x, y, ox, oy, self._turn)
                        if paths:
                            #print ("X = %d, Y = %d -> OX = %d, OY = %d"%(x, y, ox, oy))
                            result.append((x, y))
        return result
    
    def find_path_to(self, x, y, offset_x, offset_y, colour):
        path = []
        while self.on_board((x + offset_x), (y + offset_y)):
            x = x + offset_x
            y = y + offset_y
            path.append((x, y))
            if self.get_at(x, y) == EMPTY:
                return None
            if self.get_at(x, y) == colour:
                return path
        return None
    
    def draw(self):
        valid_placements = self.all_valid_placements()
        (complete, whitepoints, blackpoints, empty) = self.stats()
        display = '  01234567 -> %ss turn (complete: %d, white: %d, black: %d, empty: %d)\n'%(self._turn, complete, whitepoints, blackpoints, empty)
        for y in range(HEIGHT):
            display += '%d|'%(y)
            for x in range(WIDTH):
                if self._board[(x * WIDTH) + y] == WHITE:
                    display += WHITE_X
                elif self._board[(x * WIDTH) + y] == BLACK:
                    display += BLACK_X
                elif (x, y) in valid_placements:
                    display += VALID_X
                else:
                    display += EMPTY_X
            display += '\n'
        return display

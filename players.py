from copy import deepcopy
import random
import numpy as np
from game import Player, Move, Game


def get_all_valid_moves(game: Game):
    valid_moves = []
    moves= [Move.BOTTOM, Move.LEFT, Move.RIGHT, Move.TOP]
    random.shuffle(moves)
    for i in [0, 4]:
        for j in range(5):
            for m in moves:
                g = deepcopy(game)
                ok = g._Game__move((i, j), m, g.get_current_player())
                if ok :
                    board=g.get_board() 
                    free_cells= np.count_nonzero(board==-1)
                    one_cells = np.count_nonzero(board==1)
                    if check_simmetries(valid_moves, board, free_cells, one_cells):
                        valid_moves.append((((i, j), m), g.get_board()))
    for j in [0, 4]:
        for i in range(1, 4):
            for m in moves:
                g = deepcopy(game)
                ok = g._Game__move((i, j), m, g.get_current_player())
                if ok :
                    board=g.get_board() 
                    free_cells= np.count_nonzero(board==-1)
                    one_cells = np.count_nonzero(board==1)
                    if check_simmetries(valid_moves, board, free_cells, one_cells):
                        valid_moves.append((((i, j), m), g.get_board()))
    return valid_moves


def check_simmetries(list_states, new_state, free_cells_new_state, one_cells_new_state):  #move => ((i, j), slide)

    for s in list_states:
        free_cells = np.count_nonzero(s==-1)
        one_cells = np.count_nonzero(s==1)     

        if free_cells_new_state != free_cells or one_cells_new_state != one_cells or new_state[2][2] != s[2][2]:
            return False
    
        for k in range(1, 5): # k = 4 means 4 rotations so it's like not rotating it
            for flip in [1, -1]:  # 1 => not flipped, -1 => flipped
                key = k * flip  
                int_state = np.flip(s, axis=1) if key<0 else s# axis=1 is to flip horizontally
                int_state = np.rot90(s, k=abs(k)%4, axes=(1, 0))
                if np.array_equal(new_state, int_state): # you found the simmetry, now the fun starts
                    return True     
    return False



class RandomPlayer(Player):
    
    def __init__(self) -> None:
        super().__init__()

    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        from_pos = (random.randint(0, 4), random.randint(0, 4))
        move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
        return from_pos, move

class MyPlayer(Player):
    def __init__(self, max_depth=3):
        self.max_depth = max_depth

    def make_move(self, game: Game) -> tuple[tuple[int, int], Move]:
        _, move = self.minimax(game, self.max_depth, float('-inf'), float('inf'), True)
        return move[0], move[1]
    
    def minimax(self, game:Game, depth, alpha, beta, isMaximizing):
        if depth == 0 or game.check_winner() != -1:
            return self.evaluate(game), None
 
        valid_moves = get_all_valid_moves(game) # move is the player_id of the player currently performing the move, player_id is the id of MY player
        if isMaximizing:
            best_move = None
            v = -float('inf')
            for vm in valid_moves:
                next_game = deepcopy(game)
                next_game._Game__move(vm[0], vm[1], next_game.get_current_player())
                eval,_ = self.minimax(next_game, depth-1 , alpha, beta, False)
                if eval > v:
                    v = eval
                    best_move = vm
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return v, best_move 
        
        else:
            best_move = None
            v = float('inf')
            for vm in valid_moves:
                next_game = deepcopy(game)
                next_game._Game__move(vm[0], vm[1], next_game.get_current_player())
                eval, _ = self.minimax(vm[1], depth - 1, alpha, beta, True)
                if eval < v:
                    v = eval
                    best_move = vm
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return v, best_move 
    
    def evaluate(self, game: Game) -> int:
        winner = game.check_winner()
        if winner == game.get_current_player():
            return 1
        elif winner != -1:
            return -1
        else:
            return 0
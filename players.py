from copy import deepcopy
import random
import numpy as np
from tree import Node, Tree, TrainGame, get_all_valid_moves, simm_move
from game import Player, Move, Game

global MOVES
MOVES = []

def get_moves():
    return MOVES

def len_moves():
    return len(MOVES)

def empty_moves():
    global MOVES
    MOVES = []

def get_all_valid_moves(state, player_id):
    valid_moves = []
    for i in range(5):
        for j in range(5):
            for m in [Move.BOTTOM, Move.LEFT, Move.RIGHT, Move.TOP]:
                game = TrainGame(deepcopy(state))
                ok = game.move((i, j), m, player_id)
                if ok:
                    valid_moves.append((((i, j), m), game.get_board(), game.check_winner()))
    return valid_moves


def check_simmetries(checked_state, node, free_cells_state,one_cells_state, flag_simmetries=False):  #move => ((i, j), slide)

    if free_cells_state != node.free_cells or one_cells_state != node.one_cells or node.state[2][2] != checked_state[2][2]:
        return None
    
    for k in range(1, 5): # k = 4 means 4 rotations so it's like not rotating it
        for flip in [1, -1]:  # 1 => not flipped, -1 => flipped
            key = k * flip  
            int_state = np.flip(node.state, axis=1) if key<0 else node.state# axis=1 is to flip horizontally
            int_state = np.rot90(int_state, k=abs(k)%4, axes=(1, 0))
            if np.array_equal(int_state, checked_state): # you found the simmetry, now the fun starts
                if flag_simmetries:
                    return True
                best_node = list(filter(lambda e: e.terminal==((e.depth+1)%2), node.children))
                if len(best_node)!=0:
                    my_node = best_node[0]
                else:
                    if len(node.children) == 0:
                        print(f"\nNo more children, depth: {node.depth}")
                    my_node = max(node.children, key= lambda e: e.UCT(), default=None)
                if my_node is None:
                    return None
                (i, j) = my_node.move[0]
                slide = my_node.move[1]
                simm = {
                    4: ([Move.TOP, Move.RIGHT, Move.BOTTOM, Move.LEFT], (i, j)),
                    1: ([Move.RIGHT, Move.BOTTOM, Move.LEFT, Move.TOP], (4 - j, i)),
                    2: ([Move.BOTTOM, Move.LEFT, Move.TOP, Move.RIGHT], (4 - j, 4 - i)),
                    3: ([Move.LEFT, Move.TOP, Move.RIGHT, Move.BOTTOM], (j, 4 - i)),
                    -4: ([Move.TOP, Move.LEFT, Move.BOTTOM, Move.RIGHT], (4 - j, i)),
                    -1: ([Move.LEFT, Move.BOTTOM, Move.RIGHT, Move.TOP], (i, j)),
                    -2: ([Move.BOTTOM, Move.RIGHT, Move.TOP, Move.LEFT], (j, 4 -i)),
                    -3: ([Move.RIGHT, Move.TOP, Move.LEFT, Move.BOTTOM], (4 - i, 4 - j))
                }

                my_slide= simm[4][0].index(slide)
                new_slide = simm[key][0][my_slide]
                new_pos= simm[key][1]
                return my_node, (new_pos, new_slide) 
    return None

def minimax(state, player_id, move, alfa, beta, max_depth, isMaximizing, winner):
    if winner != -1: # terminal node
        return 1 if winner == player_id else -1
    if max_depth == 0:
        return 0 #counts as a draw
    valid_moves = get_all_valid_moves(state, move) # move is the player_id of the player currently performing the move, player_id is the id of MY player
    if isMaximizing:
        v = -float('inf')
        for vm in valid_moves:
            v = max([v, minimax(vm[1], player_id, 1 - move, alfa, beta, max_depth - 1, not isMaximizing, vm[2])])
            alfa = max([alfa, v])
            if beta <= alfa:
                break
    else:
        v = float('inf')
        for vm in valid_moves:
            v = min([v, minimax(vm[1], player_id, 1 - move, alfa, beta, max_depth - 1, isMaximizing, vm[2])])
            beta = min([beta, v])
            if beta <= alfa:
                break
    return v

class RandomPlayer(Player):
    
    def __init__(self, player_id) -> None:
        super().__init__()
        self.player_id = player_id

    def make_move(self, game: 'TrainGame') -> tuple[tuple[int, int], Move]:
        # init_board = game.get_board()
        # ok = False
        # while not ok:
        #     from_pos = (random.randint(0, 4), random.randint(0, 4))
        #     move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
        #     ok = game.move(from_pos, move, self.player_id)  #THIS METHOD CHANGES THE BOARD, I NEED TO RESTORE THE PREVIOUS ONE
        # MOVES.append(((from_pos, move), deepcopy(game.get_board())))
        # game.set_board(init_board)
        # return from_pos, move
    
        vm = get_all_valid_moves(game.get_board(), self.player_id)
        chosen_move = random.choice(vm)
        # print(chosen_move)
        MOVES.append(((chosen_move[0][0], chosen_move[0][1]), chosen_move[1]))
        return chosen_move[0][0], chosen_move[0][1]


class Opponent(Player):
    def __init__(self, player_id) -> None:
        super().__init__()
        self.player_id = player_id
    
    def make_move(self, game: Game) -> tuple[tuple[int, int], Move]:
        from_pos = (random.randint(0, 4), random.randint(0, 4))
        move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
        if len(MOVES) % 2 == self.player_id: # if it's your turn than add a new element to the list
            MOVES.append((from_pos, move))
        else: # your previous move was not valid, try again
            MOVES[-1] = (from_pos, move)
        return from_pos, move

class MyPlayer(Player):

    def __init__(self, tree:Tree, player_id) -> None:
        super().__init__()
        self.tree:Tree = tree
        self.player_id = player_id
        self.current_state:Node = self.tree.head
        self.not_found = False
        self.switch_turn = None
        self.switch_cause = None
    
    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        if not self.not_found:
            if len(MOVES) == 0: #First move of the game
                best_move = max(self.current_state.children, key=lambda e: e.UCT())
                from_pos, move = best_move.move[0], best_move.move[1]
                next_state = self.current_state.find_child(best_move.state)
                if next_state == None:
                    self.not_found = True
                else:
                    self.current_state = next_state
                    MOVES.append((best_move.move, best_move.state))
            # LOOK FOR THE NODE IN THE TREE USING THE MOVES LIST
            else:
                self.current_state, best_move= simm_move(self.current_state, game.get_board()) # find the opponent last move in the tree
                if best_move is not None:
       
                    # from_pos, move= [best_move[0][1], best_move[0][0]], best_move[1]
                    MOVES.append(((from_pos, move), self.current_state.state))
                    return best_move
                else:
                    # print("Opponent move not found")
                    self.not_found = True
                    self.switch_cause = "Opponent move not found"
        # IF YOU DON'T FIND THE NODE, PLAY RANDOMLY
        if self.not_found:
            # if self.switch_turn is not None:
            #     self.current_state, move= search_new_node(self.tree.head, game.get_board(), np.count_nonzero(game.get_board()== -1))
            #     if move is not None:
            #         print("YEEEEE, TROVATA")
            #         MOVES.append((move, self.current_state))
            #         self.not_found = False
            #         return move
            if self.switch_turn is None:
            #     print(f"Switch strategy at turn {len(MOVES) + 1}")
                self.switch_turn = len(MOVES) + 1
                if self.switch_turn % 2 == 0:
                    print("WHY!!!") 
                # print(MOVES)
                # now try to print the entire steps until now
    
            
            # RANDOM
            # print("RANDOM")
            from_pos = (random.randint(0, 4), random.randint(0, 4))
            move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
            self.not_found = True
        

            # MINIMAX
            # valid_moves = get_all_valid_moves(game.get_board(), self.player_id)
            # scores_list = []
            # for vm in valid_moves:
            #     score = minimax(vm[1], self.player_id, (self.player_id + 1) % 2, -float('inf'), float('inf'), 3, True, vm[2])
            #     scores_list.append((vm[0], score))
            # chosen_move = max(scores_list, key=lambda e: e[1])
            # from_pos = chosen_move[0][0]
            # move = chosen_move[0][1]

            if len(MOVES) % 2 == self.player_id: # if it's your turn than add a new element to the list
                MOVES.append((from_pos, move))
            else: # your previous move was not valid, try again
                MOVES[-1] = (from_pos, move)
        return from_pos, move

def search_new_node(node, board, free_cells):
        if node is None:
            return None, None
        node_list = list(filter(lambda e: e.free_cells >= free_cells, node.children))
        if len(node_list) == 0:
            return None, None
        for n in node_list:     
            if n.free_cells == free_cells:
                my_node, move = simm_move(n, board)
            if n.free_cells > free_cells:
                my_node, move = search_new_node(n, board, free_cells)
            if move is not None:
                return my_node,move
        return None, None
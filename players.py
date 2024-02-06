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
                    MOVES.append((best_move, self.current_state))
                    return best_move
                else:
                    # print("Opponent move not found")
                    self.not_found = True
                    self.switch_cause = "Opponent move not found"
        # IF YOU DON'T FIND THE NODE, PLAY RANDOMLY
        if self.not_found:
            if self.switch_turn is not None:
                self.current_state, move= search_new_node(self.tree.head, game.get_board(), np.count_nonzero(game.get_board()== -1))
                if move is not None:
                    print("YEEEEE, TROVATA")
                    MOVES.append((move, self.current_state))
                    self.not_found = False
                    return move
            if self.switch_turn is None:
            #     print(f"Switch strategy at turn {len(MOVES) + 1}")
                self.switch_turn = len(MOVES) + 1
                # print(MOVES)
                # now try to print the entire steps until now
    
            
            # RANDOM
            print("RANDOM")
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
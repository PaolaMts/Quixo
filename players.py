from copy import deepcopy
import random
from tree import Node, Tree, TrainGame, get_all_valid_moves
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
    
        vm = get_all_valid_moves(deepcopy(game.get_board()), self.player_id)
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
                best_move = max(self.current_state.children, key=lambda e: e.wins / (e.wins + e.losses))
                from_pos, move = best_move.move[0], best_move.move[1]
                next_state = self.current_state.find_child(best_move.move)
                if next_state == None:
                    self.not_found = True
                    self.switch_turn = len(MOVES) + 1
                else:
                    self.current_state = next_state
                    MOVES.append(best_move.move)
            # LOOK FOR THE NODE IN THE TREE USING THE MOVES LIST
            else:
                opponent_move = self.current_state.find_child(MOVES[-1]) # find the opponent last move in the tree
                if opponent_move is not None:
                    best_move = max(opponent_move.children, key=lambda e: e.wins / (e.wins + e.losses), default=None)
                    if best_move is not None:
                        from_pos, move = best_move.move[0], best_move.move[1]
                        self.current_state = best_move
                        MOVES.append(best_move.move)
                    else:
                        # print("Best move not found")
                        self.not_found = True
                        self.switch_cause = "Best move not found"
                else:
                    # print("Opponent move not found")
                    self.not_found = True
                    self.switch_cause = "Opponent move not found"
        # IF YOU DON'T FIND THE NODE, PLAY RANDOMLY
        if self.not_found:
            if self.switch_turn is None:
            #     print(f"Switch strategy at turn {len(MOVES) + 1}")
                self.switch_turn = len(MOVES) + 1
                # print(MOVES)
                # now try to print the entire steps until now
                f_node = self.tree.head
                for m in MOVES:
                    # print(f"list of moves:{MOVES}")
                    child = f_node.find_child(m)
                    # child.print() if child is not None else print("None")
                    # if child is None:
                    #     # print("LIST OF CHILDREN:")
                    #     for c in f_node.children:
                    #         print(c.move)
                    f_node = child
            
            # RANDOM
            from_pos = (random.randint(0, 4), random.randint(0, 4))
            move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])

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

   
import numpy as np
from game import Move, Game
from copy import deepcopy
from colorama import Fore


class Node():
    def __init__(self, move, state, parent:'Node'=None, terminal=False, is_new=True) -> None:
        self.parent = parent  # TO CLIMB THE TREE UPWARD
        self.children: list['Node'] = [] 
        self.move = move  #THE MOVE ASSIGNED TO THE NODE
        self.wins = 0  
        self.losses = 0
        self.depth = parent.depth + 1 if parent is not None else 0
        self.terminal = terminal
        self.state = state #state of the board on that move 
        self.free_cells = np.count_nonzero(self.state == -1)
        self.is_complete = False
        

        if parent is not None:  # include the new node in the children list of the parent
            parent.append_child(self, is_new=is_new)
        
    def append_child(self, child:'Node', is_new=True):  #add a child to the node
        self.children.append(child)
        # if is_new:
        #     self.is_complete = len(self.children) == len(get_all_valid_moves(self.state, self.depth % 2)) 
    
    def UCT(self):
        return self.wins / (self.wins + self.losses) + (np.sqrt(2 * np.log(self.parent.wins + self.parent.losses) / (self.wins + self.losses)) if self.parent is not None else 0)

    def find_child(self, state, ):
        free_cells_state = np.count_nonzero(state == -1)
        for c in self.children:
            k = check_simmetries(state, c, free_cells_state, True)
            if k is not None:
                return c
        return None # if no child has the assigned move
    
    def print(self):
        print(f"move:{self.move}, wins:{self.wins}, losses:{self.losses}, depth:{self.depth}, #children: {len(self.children)}")


class Tree():
    def __init__(self) -> None:
        self.head = Node(None, np.ones((5, 5), dtype=np.uint8) * -1) # Tree head has no move associated to it
        # initialize all the valid starting moves for the tree
        # vm = get_all_valid_first_moves()
        # for valid_move in vm:
        #     Node(valid_move, self.head)
        self.depth = 0
        self.next_idx = 1
    
    def set_depth(self, depth):
        if depth > self.depth:
            self.depth = depth
    
    def update_idx(self):
        self.next_idx+=1

    def print(self):
        print(f"Number of sons:{len(self.head.children)}")

class TrainGame(Game):
    def __init__(self, board=np.ones((5, 5), dtype=np.uint8) * -1, current_player=1) -> None:  #possibility to start a game from a given intermediate state
        self._board = board
        self.current_player_idx = current_player

    def print(self):
        for i in range(5):
            for j in range(5):
                v = self._board[i][j]
                print(f"{Fore.BLUE}O{Fore.RESET} " if v == 0 else f"{Fore.RED}X{Fore.RESET} " if v == 1 else f"{Fore.GREEN}E{Fore.RESET} ", end="")
            print()
        print()

    def set_board(self, board) -> None:
        self._board = board

    def move(self, from_pos: tuple[int, int], slide: Move, player_id: int) -> bool:
        return self._Game__move(from_pos, slide, player_id)


def get_ancestors(node:Node):
    n = node
    l:list[Node] = [n]
    while n.parent is not None:
        l.append(n.parent)
        n=n.parent
    return sorted(l, key=lambda e: e.depth)


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

def simm_move(node, state):
    free_cells_state = np.count_nonzero(state == -1)
    for c in node.children:
        move = check_simmetries(state, c, free_cells_state, False)
        if move is not None:
            return move
    return None, None

def check_simmetries(checked_state, node, free_cells_state, flag_simmetries=False):  #move => ((i, j), slide)

    if free_cells_state != node.free_cells:
        return None
    
    for k in range(1, 5): # k = 4 means 4 rotations so it's like not rotating it
        for flip in [1, -1]:  # 1 => not flipped, -1 => flipped
            key = k * flip  
            int_state = np.flip(node.state, axis=1) if key<0 else node.state# axis=1 is to flip horizontally
            int_state = np.rot90(int_state, k=abs(k)%4, axes=(1, 0))
            if np.array_equal(int_state, checked_state): # you found the simmetry, now the fun starts
                if flag_simmetries:
                    return True
                my_node = max(node.children, key= lambda e: e.UCT())
                (i, j) = my_node.move[0]
                slide = my_node.move[1]
                simm = {
                    4: ([Move.TOP, Move.RIGHT, Move.BOTTOM, Move.LEFT], (i, j)),
                    1: ([Move.RIGHT, Move.BOTTOM, Move.LEFT, Move.TOP], (4 - j, i)),
                    2: ([Move.BOTTOM, Move.LEFT, Move.TOP, Move.RIGHT], (4 - i, 4 - j)),
                    3: ([Move.LEFT, Move.TOP, Move.RIGHT, Move.BOTTOM], (j, 4 - i)),
                    -4: ([Move.TOP, Move.LEFT, Move.BOTTOM, Move.RIGHT], (4 - i, j)),
                    -1: ([Move.LEFT, Move.BOTTOM, Move.RIGHT, Move.TOP], (j, i)),
                    -2: ([Move.BOTTOM, Move.RIGHT, Move.TOP, Move.LEFT], (i, 4 - j)),
                    -3: ([Move.RIGHT, Move.TOP, Move.LEFT, Move.BOTTOM], (4 - j, 4 - i))
                }

                my_slide= simm[4][0].index(slide)
                new_slide = simm[key][0][my_slide]
                new_pos= simm[key][1]
                return my_node, (new_pos, new_slide) 
    return None
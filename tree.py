import numpy as np
from game import Move, Game
from copy import deepcopy
from colorama import Fore

class Node():
    
    def __init__(self, move, state, parent:'Node'=None, terminal=False) -> None:
        self.parent = parent  # TO CLIMB THE TREE UPWARD
        self.children: list['Node'] = [] 
        self.move = move  #THE MOVE ASSIGNED TO THE NODE
        self.wins = 0  
        self.losses = 0
        self.depth = parent.depth + 1 if parent is not None else 0
        self.terminal = terminal
        self.state = state #state of the board on that move 

        if parent is not None:  # include the new node in the children list of the parent
            parent.append_child(self)

    def append_child(self, child:'Node'):  #add a child to the node
        self.children.append(child)

    def is_complete(self):
        return len(self.children) == len(get_all_valid_moves(self.state, self.depth % 2))


    def find_child(self, move):
        for c in self.children:
            if move == c.move:
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
    
    def set_depth(self, depth):
        if depth > self.depth:
            self.depth = depth

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


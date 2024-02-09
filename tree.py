import numpy as np
from game import Move, Game
from copy import deepcopy
from colorama import Fore 

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

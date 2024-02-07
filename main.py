from game import Game
from tree import Node, Tree, TrainGame
from players import MyPlayer, RandomPlayer, empty_moves
from utils import serialize_node, deserialize_tree, initialize_tree, expand_tree
from tqdm.auto import tqdm
import numpy as np
import pickle
import os

TEST_MATCHES = 1
MODE = "train"
      

if __name__ == '__main__':
    # mc_tree, node_list = initialize_tree()
    cont_terminal = 0 

    mc_tree = Tree(5)
    node_list:list[Node] = []
    if os.path.exists('albero.pkl'):
        with open('albero.pkl', 'rb') as file:
            loaded_tree = pickle.load(file)
            mc_tree.head, node_list = deserialize_tree(loaded_tree)
            mc_tree.depth = max(node_list, key=lambda e: e.depth).depth          
    else:     
        initialize_tree(mc_tree, node_list,250)

    print(f"Max Node: {max(node_list, key=lambda e: e.depth).depth }")
    print(f"non_complete_nodes: {len(list(filter(lambda e: e.depth==2 and not e.is_complete, node_list)))}")  
    print(f"depht 2 : {len(list(filter(lambda e: e.depth==2, node_list)))}")    
    
    if MODE == "train":
        len_node_before_expansion = len(node_list) 
        # expand_tree(mc_tree, node_list)
        len_node_after_expansion = len(node_list)
        print(f"nodes after expansion: {len_node_after_expansion}")

        serialized_tree= serialize_node(mc_tree.head) 
        with open('albero.pkl', 'wb') as file:
            pickle.dump(serialized_tree, file)

    print(f"Depth: {mc_tree.depth}")
        
    wins = 0
    losses = 0

    # print(f"# of nodes = {len(node_list)}")

    print("\nTEST GAMES")

    switch_turns = []
        
    for _ in tqdm(range(TEST_MATCHES)):
        g = TrainGame(np.ones((5, 5), dtype=np.uint8) * -1, 1)
        g = Game()
        player1 = MyPlayer(mc_tree, 0)
        player2 = RandomPlayer(1)
        winner = g.play(player1, player2)
        switch_turns.append((player1.switch_turn, player1.switch_cause))
        if winner == 0:
            wins +=1
        else:
            losses += 1
        # g.print()
        empty_moves()
    print(f"wins: {wins}, losses: {losses}")

    print(max(switch_turns, key=lambda e: e[1])[0])
    
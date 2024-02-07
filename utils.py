from tree import Tree, Node, TrainGame, get_all_valid_moves, get_ancestors
from tqdm.auto import tqdm
import numpy as np
from players import RandomPlayer, get_moves, len_moves, empty_moves
from copy import deepcopy


def minimax(state, player_id, move, alfa, beta, max_depth, isMaximizing, winner):
    if winner != -1: # terminal node
        return 1 if winner == player_id else -1
    if max_depth == 0:
        return 0 #counts as a draw
    valid_moves = get_all_valid_moves(state, move) # move is the player_id of the player currentòy performing the move, player_id is the id of MY player
    if isMaximizing:
        v = -float('inf')
        for vm in valid_moves:
            v = max([v, minimax(vm[1], player_id, (move + 1) % 2, alfa, beta, max_depth - 1, not isMaximizing, vm[2])])
            alfa = max([alfa, v])
            if beta <= alfa:
                break
    else:
        v = float('inf')
        for vm in valid_moves:
            v = min([v, minimax(vm[1], player_id, (move + 1) % 2, alfa, beta, max_depth - 1, not isMaximizing, vm[2])])
            beta = min([beta, v])
            if beta <= alfa:
                break
    return v

def initialize_tree(mc_tree: Tree, node_list: list[Node], init_train=1_000):
    print("INITIALIZE THE TREE")
    n_wins = 0
    n_losses = 0
    for _ in tqdm(range(init_train)):
        g = TrainGame(np.ones((5, 5), dtype=np.uint8) * -1, 1)
        # g.print()
        player1 = RandomPlayer(0)
        player2 = RandomPlayer(1)
        winner = g.play(player1, player2)

        if winner == 0:
            n_wins += 1
        else:
            n_losses += 1
        mc_tree.set_depth(len_moves())
        l= len_moves()
        parent = mc_tree.head
        for i in range(len_moves()):
            if i >= mc_tree.max_depth:
                break 
            child = parent.find_child(get_moves()[i][1])
            if child is None:
                child = Node(get_moves()[i][0], get_moves()[i][1], parent=parent, terminal=winner if i == len_moves() - 1 else -1)
                node_list.append(child)
            if winner == 0:
                if child.depth % 2 == 0:
                    child.wins += 1
                else:
                    child.losses += 1
            else:
                if child.depth % 2 == 0:
                    child.losses += 1
                else:
                    child.wins += 1
            parent = child
        empty_moves()
        l = len_moves()

def expand_tree(mc_tree: Tree, node_list: list[Node], n_expansions = 100):
    nodes_to_expand = sorted(filter(lambda e:  e.terminal==-1 and not e.is_complete and e.depth < mc_tree.max_depth, node_list), key=lambda e: (e.depth, -e.UCT()), reverse=False)
    print(f"min_depth to expand: {nodes_to_expand[0].depth}")
    print(f"Nodes to expand: {len(nodes_to_expand)}")
    
    expansions = len(nodes_to_expand) if n_expansions >= len(nodes_to_expand) else n_expansions
    print(f"# of nodes = {len(node_list)}")
    
    print("\nEXPANSION")
    for j in tqdm(range(expansions)):
        node = nodes_to_expand[j]
        for _ in range(100):
            empty_moves()
            g = TrainGame(deepcopy(node.state), (node.depth + 1) % 2)
            player1 = RandomPlayer(0)
            player2 = RandomPlayer(1)
            winner = g.play(player1, player2)
            mc_tree.set_depth(node.depth + len_moves())
            ancestors = get_ancestors(node)
            for a in ancestors:
                if a.depth % 2 == 0: #moves of player 1
                    if winner == 1:
                        a.wins += 1
                    else:
                        a.losses += 1
                else: #moves of player 0
                    if winner == 1:
                        a.losses += 1
                    else:
                        a.wins += 1
            parent = node
            for i in range(len_moves()):
                if node.depth + i >= mc_tree.max_depth:
                    break
                child = parent.find_child(get_moves()[i][1])
                if child is None:
                    child = Node(get_moves()[i][0], get_moves()[i][1], parent=parent, terminal=winner if i == len_moves() - 1 else -1)
                    node_list.append(child)
                if winner == 0:
                    if child.depth % 2 == 0:
                        child.wins += 1
                    else:
                        child.losses += 1
                else:
                    if child.depth % 2 == 0:
                        child.losses += 1
                    else:
                        child.wins += 1
                parent = child
            empty_moves()  
  

def serialize_node(node:Node, i):
    serialized_node = {
        'move': node.move,
        'state': node.state,
        'wins': node.wins,
        'losses': node.losses,
        'terminal': node.terminal,
        'is_complete': node.is_complete,
        'children': [serialize_node(child, i+1) for child in node.children if child.depth==i+1],
    }
    return serialized_node

# def serialize_node(node: Node):
#     stack = [node]
#     serialized_tree = []

#     while stack:
#         current_node = stack.pop()
#         serialized_node = {
#             'move': current_node.move,
#             'state': current_node.state,
#             'wins': current_node.wins,
#             'losses': current_node.losses,
#             'terminal': current_node.terminal,
#             'is_complete': current_node.is_complete,
#             'children': [],
#         }

#         # Aggiungiamo i figli solo se il nodo corrente ha figli e lo stiamo processando per la prima volta
#         if current_node.children and not serialized_node['children']:
#             for child in reversed(current_node.children):
#                 stack.append(child)

#         # Aggiungiamo il nodo corrente alla lista dei nodi serializzati
#         serialized_tree.append(serialized_node)

#     # Restituiamo la testa dell'albero serializzata
#     return serialized_tree[0] if serialized_tree else None



# def deserialize_tree(serialized_node):
#     # Creiamo una pila per gestire i nodi da visitare
#     stack = [(None, serialized_node)]
#     node_list = []

#     while stack:
#         parent, serialized_node = stack.pop()
#         move = serialized_node.get('move')
#         state = serialized_node.get('state')
#         terminal = serialized_node.get('terminal')
#         node = Node(move, state, parent, terminal, False)


#         wins = serialized_node.get('wins', 0)
#         losses = serialized_node.get('losses', 0)
#         node.is_complete = serialized_node.get('is_complete', False)
#         node.wins = wins
#         node.losses = losses

#         node_list.append(node)

#         children_data = serialized_node.get('children', [])
#         for child_data in children_data:
#             stack.append((node, child_data))

#     # Restituiamo sia il nodo principale che la lista dei nodi deserializzati
#     return node_list[0], node_list





def deserialize_tree(serialized_node,i, parent=None, node_list=None):
    move = serialized_node.get('move')
    state = serialized_node.get('state')
    terminal = serialized_node.get('terminal')
    node = Node(move, state, parent, terminal, False, )

    wins = serialized_node.get('wins', 0)
    losses = serialized_node.get('losses', 0)
    node.is_complete = serialized_node.get('is_complete', False)
    node.wins = wins
    node.losses = losses
    
    children_data = serialized_node.get('children', [])
    for child_data in children_data:
        if i==node.depth:
            deserialize_tree(child_data,i+1, parent=node, node_list=node_list)

    if node_list is not None:
        node_list.append(node)
    return node, node_list


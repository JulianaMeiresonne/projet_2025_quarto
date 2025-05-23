import socket
import json
import random
import copy
import time

#variables initiales
port_perso = 8888
port_serveur_global = 3000 # connection au serveur du prof
IP_serveur_global = "localhost" # adress IP du serveur du prof
name = "Vénéré_maîtresse1"
matricules = ["23342", "23268"]
chosen_pieces =[]
all_position = []


def generated_pieces(): # génèrer la liste de tous les moves
          chosen_pieces.clear()
          # Big/Small: B/S
          # Dark/Light: D/L
          # Empty/Full: E/F
          # Cylinder/Prism: C/P
          for size in ["B", "S"]:
              for color in ["D", "L"]:
                  for weight in ["E", "F"]:
                      for shape in ["C", "P"]:
                          chosen_pieces.append(f"{size}{color}{weight}{shape}")

def same(L):
    if None in L:
        return False
    common = frozenset(L[0])
    for elem in L[1:]:
        common = common & frozenset(elem)
    return len(common) > 0


def getLine(board, i):
    return board[i * 4 : (i + 1) * 4]


def getColumn(board, j):
    return [board[i] for i in range(j, 16, 4)]


# dir == 1 or -1
def getDiagonal(board, dir):
    start = 0 if dir == 1 else 2
    return [board[start + i * (4 + dir)] for i in range(4)]

def winner(board):                                                  #définition de la fonction permettant de rassembler les conditions de réussite au jeu
    for i in range(4):
        if same(getLine(board, i)):
            return True
        if same(getColumn(board, i)):
            return True
    if same(getDiagonal(board, 1)):
        return True
    return same(getDiagonal(board, -1))

def isFull(board):
    for elem in board:
        if elem is None:
            return False
    return True

def gameOver(state):                                                #cette fonction permet de dire à l'IA quand elle doit cesser de réfléchir ou de jouer
     if winner(state) is not None:
          return True
     elif isFull(state) is True:
          return True
    
def utility(state, player):                                         #permet d'avoir un état de succés pour l'IA
	theWinner = winner(state)
	if theWinner is None:
		return 0
	if theWinner == player:
		return 1
	return -1

def moves(state):                                                                       #va nous permettre de return tout les moves possibles à faire
    moves=[]                                                                            #liste vide de move que l'on peut faire
    empty_case=[n for n,position in enumerate(state["board"]) if position is None]
    pieces_to_use= [piece for piece in chosen_pieces if piece not in state["board"]]
    for pos in empty_case:
        for piece in pieces_to_use:
            moves.append({"position":pos , "piece":piece})
    return moves


def random_move(game_board, piece):

    generated_pieces()
              # Move
          # {
          #   "pos": <index>,        # between 0 and 15 or null if first move
          #   "piece": <piece_str>,  # piece for the opponent example "BDEC"
          # }
    all_position =list(range(len(game_board))) #range renvoie une object range donc il faut transformer en liste
    index = 0 #permte de connaitre l'indice d'un object sur le plateau de jeux 
    for n in game_board:
        if n != None:
            if n in chosen_pieces:
                chosen_pieces.remove(n)
            if index in all_position: 
                all_position.remove(index)
        index +=1
    pos = random.choice(all_position)
    if piece!= None :  #pour éviter les bad moves causé par la piece choisit par notre adversaire
        if piece in chosen_pieces:
            chosen_pieces.remove(piece)
    piece = random.choice(chosen_pieces)
    if len(piece) == 0:
        piece = None
    return {"pos": pos, "piece": piece}

def timeit(fun):
    def wrapper(*args, **kwargs):
            start = time.time()  # Temps de début
            res = None
            time_spend = 0
            limit_second=3
            while time_spend<limit_second:
                res = fun(*args, **kwargs)
                time_spend=time.time()-start
                if time_spend>=limit_second:
                    res is None
            if res is None:
                return random_move()
            return res
    return wrapper

@timeit
def Quarto_state(players):
    state = {"players": players, "current": 0, "board": [None] * 16, "piece": None}

def currentPlayer(state):                                   #permet de savoir qui joue
    return state["players"][state["current"]]

def apply(state, move):
    def next(state, move):
        newState = copy.deepcopy(state)

        if state["piece"] is not None:
            if "pos" not in move:
                raise ValueError
            try:
                pos = int(move["pos"])
                state["board"][pos]
            except (ValueError, IndexError):
                return ValueError
            newState["board"][pos] = state["piece"]
        piece = frozenset(move["piece"])
        newState["piece"] = move["piece"]
        newState["current"] = (state["current"] + 1) % 2
        return newState
    return state, next


lines = [[0, 1, 2, 3],[4, 5, 6, 7],[8, 9, 10, 11],[12, 13, 14, 15],                         #toutes les lignes possibles pour gagner la partie
         [0, 4, 8, 12],[1, 5, 9, 13],[2, 6, 10, 14],[3, 7, 11, 15],
         [0, 5, 10, 15],[3, 6, 9, 12]]

def lineValue(line, player,state):
    '''on implémente ici la logique pour faire un bon coup
       voir les caractéristiques communes des pièces placées sur le plateaux et leurs position pour voir si on peut en aligner 4 communes'''
    # pieces=[state[i] for i in line if state[i] is not None]                                #on prends un liste avec toutes les pièces sur le plateaux pour chaque ligne
    # if len(pieces)<4:                                                                      #la ligne de 4 n'est pas complète
    #     return 0
    # return
    counters = {1: 0,2: 0,None: 0}
    for elem in line:
         counters[elem] +=1
    if counters[player] > counters[player%2+1]:
        return 1
    if counters[player] == counters[player%2+1]:
         return 0
    return -1

def heuristic(state, player):
	if gameOver(state):
		theWinner = winner(state)
		if theWinner is None:
			return 0
		if theWinner == player:
			return 9
		return -9
	res = 0
	for line in lines:
		res += lineValue([state[i] for i in line], player)
	return res

def negamaxWithPruningLimitedDepth(state, player, depth=4, alpha=float('-inf'), beta=float('inf')):                             #c'est la fonction ''finale de l'IA'' qui nous donne le move
	if gameOver(state) or depth == 0:
		return -heuristic(state, player), None

	theValue, theMove = float('-inf'), None
	for move in moves(state):
		successor = apply(state, move)
		value, _ = negamaxWithPruningLimitedDepth(successor, player%2+1, depth-1, -beta, -alpha)
		if value > theValue:
			theValue, theMove = value, move
		alpha = max(alpha, theValue)
		if alpha >= beta:
			break
	return -theValue, theMove
         

if __name__ == "__main__":
  socket_inscription = socket.socket() #TCP
  socket_inscription.connect((IP_serveur_global,port_serveur_global))
  socket_serveur_local = socket.socket()
  socket_serveur_local.bind(('0.0.0.0',port_perso))
  #Inscription au serveur
  message_connection = {
    "request": "subscribe",
    "port": port_perso,
    "name": name,
    "matricules": matricules
  }
  socket_inscription.send(json.dumps(message_connection).encode()) #!!!!!! json.dumps().encode(), il faut pas oublié encode()
  message = socket_inscription.recv(1024)
  message_receive =json.loads(message.decode())


  #Communication serveur (envoyer et recevoir information)
  while message_receive["response"] == "ok":
    socket_serveur_local.listen()
    client, address = socket_serveur_local.accept() #client : la méthode accept(), Renvoie un tuple avec un socket client et l’adresse de ce dernier, ce socket client est celui qui doit être utiliser pour communiquer (envoyer et recevoir info) car il reste constament connecter au client donc pas de [Errno 32] Broken pipe
    with client:
      message_ping = client.recv(1024)
      message_receive_ping =json.loads(message_ping.decode())
      if message_receive_ping["request"] == "ping":
        message_pong = {"response": "pong"}
        client.send(json.dumps(message_pong).encode())
      elif message_receive_ping["request"] == "play": 
        move = negamaxWithPruningLimitedDepth(message_receive_ping["state"]["board"],message_receive_ping["state"]["piece"])
        move_sent = { "response": "move","move": move,"message": "Fun message"}
        client.send(json.dumps(move_sent).encode())

  # python server.py quarto
  # python IA_creation_Kenza.py
  # python player_adversary.py
  # python -m pip install -r requirements.txt
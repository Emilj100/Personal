"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    count_x = sum(row.count(X) for row in board)
    count_o = sum(row.count(O) for row in board)
    
    if count_x > count_o:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell == EMPTY:
                actions.add((i, j))
    return actions




def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i, j = action
    copy_board = copy.deepcopy(board)
    turn = player(copy_board)
    if copy_board[i][j] == EMPTY:
        copy_board[i][j] = turn
    else:
        raise ValueError("Cell isnt empty")

    return copy_board



def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Tjek horizontalt
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2]:
            if not board[i][0] == EMPTY:
                return board[i][0]
            
    # Tjek vertikalt
    for i in range(3):
        if board[0][i] == board[1][i] == board[2][i]:
            if not board[0][i] == EMPTY:
                return board[0][i]

    # Tjek diagonalt
    if board[0][0] == board[1][1] == board[2][2]:
        if not board[0][0] == EMPTY:
            return board[0][0]
        
    if board[0][2] == board[1][1] == board[2][0]:
        if not board[0][2] == EMPTY:
            return board[0][2]
        
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True

    return not any(cell == EMPTY for row in board for cell in row)


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    winner_function = winner(board)
    if winner_function == X:
        return 1
    elif winner_function == O:
        return -1
    else:
        return 0


def minimax_value(board):

    if terminal(board):
        return utility(board)
    
    turn = player(board)
    
    if turn == X:
        best_value = float('-inf')
    else:
        best_value = float('inf')
    for action in actions(board):
        new_board = result(board, action)
        value = minimax_value(new_board)
        if turn == X:
            if value > best_value:
                best_value = value
        else:
            if value < best_value:
                best_value = value

    return best_value
    

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    
    turn = player(board)

    if turn == X:
        best_value = float('-inf')
    else:
        best_value = float('inf')

    best_action = None
    possible_actions = actions(board)
    for action in possible_actions:
        new_board = result(board, action)
        value = minimax_value(new_board)
        if turn == X:
            if value > best_value:
                best_value = value
                best_action = action
        else:
            if value < best_value:
                best_value = value
                best_action = action

    return best_action

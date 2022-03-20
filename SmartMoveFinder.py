import random

# This is a dictionary that assigns a value to each piece. The values are used to calculate the
# material score of the board.
pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}


# `knightScores` is a matrix that assigns a score to each square on the board. The score is based on
# the position of the knight on the board.
knightScores = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]


# A matrix that assigns a score to each square on the board. The score is based on the position of the
# bishop on the board.
bishopScores = [[4, 3, 2, 1, 1, 2, 3, 4],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [4, 3, 2, 1, 1, 2, 3, 4]]



# The queenScores matrix is a matrix that assigns a score to each square on the board. The score is
# based on the position of the queen on the board.
queenScores = [[1, 1, 1, 3, 1, 1, 1, 1],
               [1, 2, 3, 3, 3, 1, 1, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 1, 2, 3, 3, 1, 1, 1],
               [1, 1, 1, 3, 1, 1, 1, 1]]

# `rookScores` is a matrix that assigns a score to each square on the board. The score is based on the
# position of the rook on the board.
rookScores = [[4, 3, 4, 4, 4, 4, 3, 3],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [1, 1, 2, 3, 3, 2, 1, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 1, 2, 2, 2, 2, 1, 1],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [4, 3, 4, 4, 4, 4, 3, 4]]

# A matrix that assigns a score to each square on the board. The score is based on the position of the
# pawn on the board.
whitePawnScores = [[8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [0, 0, 0, 0, 0, 0, 0, 0]]

# This is the board score for black pawns. The score is based on the position of the pawn on the
# board.
blackPawnScores = [[0, 0, 0, 0, 0, 0, 0, 0],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8]]



# This is a dictionary that contains the values for each piece. The values are used to calculate the
# material score of the board.
piecePositionScores = {"N": knightScores, "Q":queenScores, "B": bishopScores, "R": rookScores, "bp": blackPawnScores, "wp": whitePawnScores}






# This is a constant that is used to determine whether a game is won, lost, or drawn.
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3




def findRandomMove(validMoves):
    """
    Return a random move from the list of valid moves
    
    :param validMoves: a list of valid moves
    :return: a random move.
    """

    return random.choice(validMoves)


def findBestMoveMinMaxNoRecursion(gs, validMoves):
    """
    Finds the best move based on material(board space) alone --> Greedy Algorithm

    :param gs: the game state
    :param validMoves: A list of valid moves for the current player
    :return: The best move for the player to make.
    """

    turnMultiplier = 1 if gs.whiteMove else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentsMoves = gs.getValidMoves()
        if gs.stalemate:
            opponentMaxScore = STALEMATE
        elif gs.checkmate:
            opponentMaxScore = -CHECKMATE
        else:
            opponentMaxScore = -CHECKMATE
            for opponentsMove in opponentsMoves:
                gs.makeMove(opponentsMove)
                gs.getValidMoves()
                if gs.checkmate:
                    score = CHECKMATE
                elif gs.stalemate:
                    score = STALEMATE
                else:
                    score = -turnMultiplier * scoreMaterial(gs.board)
                if score > opponentMaxScore:
                    opponentMaxScore = score
                gs.undoMove()
        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
    return bestPlayerMove

def findBestMove(gs, validMoves, returnQueue):
    """
    This function takes in a game state, a list of valid moves, and a queue. 
    It then finds the best move in the list of valid moves and puts it in the queue.
    
    :param gs: the game state
    :param validMoves: a list of valid moves
    :param returnQueue: a multiprocessing.Queue object that the function will put its answer into
    """
    global nextMove, counter
    nextMove = None
    random.shuffle(validMoves)
    counter = 0
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    returnQueue.put(nextMove)


def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    """
    This function takes in a game state, a list of valid moves, a depth, and a boolean indicating
    whether or not it's white's turn. 
    It returns the move with the highest or lowest value, depending on whether it's white's turn or
    black's turn.
    
    :param gs: the game state
    :param validMoves: A list of valid moves
    :param depth: The depth of the search tree
    :param whiteToMove: boolean that is True if it's white to move, and False if it's black to move
    """
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)
    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth-1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth-1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore 

def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    """
    This function is the heart of the MiniMax algorithm. It takes a game state, a list of valid moves, a
    depth, and a multiplier. 
    It returns a tuple of the best move and the value of that move.
    
    :param gs: the gamestate object
    :param validMoves: a list of valid moves
    :param depth: The depth of the search tree
    :param turnMultiplier: 1 for black, -1 for white
    """
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMax(gs, nextMoves, depth-1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore

def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    """
    This function is the heart of the MiniMax algorithm. It takes a game state, a depth, and a turn
    multiplier. It then recursively calls itself to find the maximum score of all the possible moves at
    this point in the game. It does this by first checking to see if the game is over, or if the depth
    has been reached. If so, it returns the turn multiplier times the score of the board. Otherwise, it
    loops through all the possible moves and calls itself on each move. It does this by first making the
    move, then recursively calling itself on the next set of moves. It then undoes the move, and checks
    to see if the score is greater than the current maximum score. If so, it sets the maximum score to
    the score of the board, and if the depth is DEPTH (the original call), it sets the nextMove to the
    move that resulted in the maximum score.
    
    :param gs: the game state
    :param validMoves: The list of valid moves for the current player
    :param depth: How deep to search for moves
    :param alpha: The best score we know we can achieve from this position
    :param beta: The value of the best alternative for MAX along the path to state
    :param turnMultiplier: 1 if white's turn, -1 if black's turn
    :return: The score of the best move.
    """
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth-1,-beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore


def scoreBoard(gs):
    """
    This function takes in a GameState object and returns a score for the state
    
    :param gs: the game state
    :return: The score of the board.
    """
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                piecePositionScore = 0
                if square[1] != "K":
                    if square[1] == "p":
                        piecePositionScore = piecePositionScores[square][row][col]
                    else:
                        piecePositionScore = piecePositionScores[square[1]][row][col]
                if square[0] == 'w':
                    score += pieceScore[square[1]] + piecePositionScore * .1
                elif square[0] == 'b':
                    score -= pieceScore[square[1]] + piecePositionScore * .1
    return score

def scoreMaterial(board):
    """
    Given a board, return the material score of the board
    
    :param board: the board state to evaluate
    :return: The score of the board.
    """
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':

                score += pieceScore[square[1]]
            elif square[0] == 'b':

                score -= pieceScore[square[1]]
    return score

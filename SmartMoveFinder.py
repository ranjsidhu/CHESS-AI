import random

# dictionary which assigns 'level of power' to each piece
pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}

knightScores = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

bishopScores = [[4, 3, 2, 1, 1, 2, 3, 4],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [4, 3, 2, 1, 1, 2, 3, 4]]

queenScores = [[1, 1, 1, 3, 1, 1, 1, 1],
               [1, 2, 3, 3, 3, 1, 1, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 1, 2, 3, 3, 1, 1, 1],
               [1, 1, 1, 3, 1, 1, 1, 1]]

rookScores = [[4, 3, 4, 4, 4, 4, 3, 3],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [1, 1, 2, 3, 3, 2, 1, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 1, 2, 2, 2, 2, 1, 1],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [4, 3, 4, 4, 4, 4, 3, 4]]

whitePawnScores = [[8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [0, 0, 0, 0, 0, 0, 0, 0]]

blackPawnScores = [[0, 0, 0, 0, 0, 0, 0, 0],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8]]



piecePositionScores = {"N": knightScores, "Q":queenScores, "B": bishopScores, "R": rookScores, "bp": blackPawnScores, "wp": whitePawnScores}





# assigning 1000 'points' to a CHECKMATE constant
CHECKMATE = 1000
# stalemate is better than a losing position
STALEMATE = 0
# how far deep into the tree the recursion is to go
DEPTH = 3


# when board is scored --> positive value = white winning, negative value = black winning
# i.e. white checkmate = 1000, black checkmate = -1000
# known as a zero-sum game

def findRandomMove(validMoves):
    '''Pick and return a random move'''
    return random.choice(validMoves)
    # return validMoves[random.randint(0, len(validMoves)- 1)]

# minmax without recursion
def findBestMoveMinMaxNoRecursion(gs, validMoves):
    '''Finds best move based on material(board space) alone --> Greedy Algorithm'''
    # from black's perspective, CHECKMATE is worst possible score
    # starting greedy algorithm from the worst possible situation so there is a goal/target to reach and a comparable value
    # white's perspective --> maxScore = -CHECKMATE; if score > maxScore
    # allows both sides to maximise score instead of aiming for higher/lower scores respectively
    turnMultiplier = 1 if gs.whiteMove else -1
    # trying to minimise the opponent's best move
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves) # adds variety of moves; picks first of multiple moves with same possible value
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
        gs.undoMove()  # stops the greedy algorithm from duplicating pieces to get a higher score
    return bestPlayerMove


def findBestMove(gs, validMoves, returnQueue):
    '''Helper method to call the intial recursive call to nextMove in findMoveMinMax and return it'''
    global nextMove, counter
    nextMove = None
    random.shuffle(validMoves)
    #findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
    # alpha = current min = -CHECKMATE
    # beta = current max = CHECKMATE
    counter = 0
    #findMoveNegaMax(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1)
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    #print(counter) # how many times the function is called --> TESTING PURPOSES 
    returnQueue.put(nextMove)


# depth is how far down the game tree the recursion algorithm will go
# to change how many moves the AI looks ahead, change the DEPTH constant i.e. how 'smart' the AI is
def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0: # terminal node in game tree
        return scoreMaterial(gs.board)
    
    if whiteToMove:
        # if whiteToMove is true, the score is to be maximised
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth-1, False)# recursively calling function
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore

    else:
        # black's go --> the score is to be minimised
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
    # nega max --> alwyas looking for a maximum
    # multiply it by -1 on black's turn
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
    # alpha = upper bound, beta = lower bound/ minimum/maximum possible score
    # nega max --> alwyas looking for a maximum
    # multiply it by -1 on black's turn
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    
    # move ordering --> for alpha beta pruning efficiency
    # evaluate best moves first
    # not look at branches with 'worse' moves
    # ^ implement later
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth-1,-beta, -alpha, -turnMultiplier)# everything is reversed for opponent
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
                #print(move, score)# debugging/testing
        gs.undoMove()
        if maxScore > alpha:# pruning happens
            alpha = maxScore
        
        if alpha >= beta:
            break# won't need to evaluate rest of tree

    return maxScore


# a positive score is good for white, a negative score is good for black
def scoreBoard(gs):
    # Look for checkmate before scoring board --> efficiency
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE # black wins
        else:
            return CHECKMATE # white wins
    elif gs.stalemate:
        return STALEMATE # neither side wins

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                # score positionally
                piecePositionScore = 0
                if square[1] != "K":# no position table for king
                    if square[1] == "p":# for pawns
                        piecePositionScore = piecePositionScores[square][row][col]
                    else:# for other pieces
                        piecePositionScore = piecePositionScores[square[1]][row][col]
                



                if square[0] == 'w':
                    # increasing score positively if piece is white
                    # type of piece e.g. pawn, rook etc = square[1]
                    score += pieceScore[square[1]] + piecePositionScore * .1
                elif square[0] == 'b':
                    # increasing score negatively (decreasing) if piece is black
                    score -= pieceScore[square[1]] + piecePositionScore * .1
    return score



def scoreMaterial(board):
    '''Score the board based on material'''
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                # increasing score positively if piece is white
                # type of piece e.g. pawn, rook etc = square[1]
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                # increasing score negatively (decreasing) if piece is black
                score -= pieceScore[square[1]]
    return score
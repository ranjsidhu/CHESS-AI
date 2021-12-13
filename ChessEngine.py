import copy
# This class is responsible for storing all information about the current state of a chess game
# Will also be repsonsible for determining legal chess moves at the current state
# A move log will be kept which enables recursion to be used to undo moves or display history of moves

# pieces are named according to the standard chess notations
# bR=black rook, bN=black knight, bB=black bishop, bQ=black queen, bK=black king, bp=black pawn
# wR=white rook, wN=white knight, wB=white bishop, wQ=white queen, wK=white king, wp=white pawn

# class which will be responsible for storing the foundation of a standard chess board
# will be responsible for determining if it is a black or white move
class GameState():
    # constructor function
    def __init__(self):
        # string representation of the 8x8 chess board as a 2-dimesnional array
        # 1 element = 2 characters --> colour('w' or 'b') and piece('K', 'Q', 'R', 'B', 'N', 'P')
        # '--' = an empty space on the board --> no piece
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]

        # dictionary to avoid a long if statement later on when deciding which function to call when a piece is being moved
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'K': self.getKingMoves, 'Q': self.getQueenMoves}

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)# initial whiteKingLocation
        self.blackKingLocation = (0, 4)# initial blackKingLocation
        self.checkmate = False
        self.stalemate = False
        # coordinates for the square where en-passant capture is possible
        self.enPassantPossible = ()
        self.enPassantPossibleLog = [self.enPassantPossible]
        # setting all parameters of CastleRights class to True at the beginning of a game
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]


        #self.protects = [][]
        #self.threatens = [][]
        #self.squaresCanMoveTo = [][]


    def makeMove(self, move):

        '''Takes a move as a paraemter and executes it'''

        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove  # this will swap player turns
        # updating king's position if needed
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        # cannot use else as that would include any other piece
        # only the Kings are required
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
        
        # pawn promotion with QUEEN only to favour simplicity
        if move.isPawnPromotion:
            # will get the colour of the pawn moved
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
        
        # en passant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--' # capturing the pawn
        
        # updating enPassantPossible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: # the piece is a pawn and has moved 2 squares forward
            self.enPassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enPassantPossible = ()
        
        # castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:# kingside castle
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] # moves the rook
                self.board[move.endRow][move.endCol+1] = '--' # erase the old rook
            else: # queenside castle
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2] # moves the rook
                self.board[move.endRow][move.endCol-2] = '--' # erase the old rook
        

        self.enPassantPossibleLog.append(self.enPassantPossible)
        
        # updating castling rights - whenever it is a king or rook move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))




    def undoMove(self):

        '''Undo last move made'''

        if len(self.moveLog) != 0:  # there must be a move to undo
            move = self.moveLog.pop()  # removes last move from moveLog and stores it in a variable
            # moves piece back to intial row and column
            self.board[move.startRow][move.startCol] = move.pieceMoved
            # returns the captured piece back to the board
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # swaps player turn
            # updating king's position if needed
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            
            # undo en passant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--' # leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
            # update en passant log
            self.enPassantPossibleLog.pop()
            self.enPassantPossible = self.enPassantPossibleLog[-1]

            # undo castling rights
            self.castleRightsLog.pop() # get rid of new castle rights from move being undone
            castle_rights = copy.deepcopy(self.castleRightsLog[-1])
            self.currentCastlingRight = castle_rights # set current castle rights to the last one in the list
            # undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: # kingside
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else: # queenside
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'
            
            self.checkmate = False
            self.stalemate = False

    # all moves where the King is in check i.e. checkmate moves
    def getValidMoves(self):  # getValidMoves in tutorial
        # NÄIVE ALGORITHM IMPLEMENTATION --> favours simplicity over efficency
        # inefficent because it generates all possible opponent moves for every move
        tempEnPassantPossible = self.enPassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs) # copy current castling rights
        # 1. generate all possible moves
        moves = self.allPossibleMoves()
        # 2. make move
        for i in range(len(moves)-1, -1, -1): # iterating through the for loop backwards by -1 with range(len(moves)-1, -1)
            self.makeMove(moves[i])
            # 3. generate all opponent moves
            # 4. look for opponent moves that attack king
            # makeMove function swaps turns, so the turns must be swapped again before calling inCheck()
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                # 5. if king is not safe --> invalid move
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0: # either checkmate or stalemate if there are no valid moves remaining
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        
        # calling castle moves functions
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        self.enPassantPossible = tempEnPassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves


    # determines if current player is in check
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    # determines if the enemy can attack square (r,c)
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove # switches to an opponent's view of the board
        oppMoves = self.allPossibleMoves()
        self.whiteToMove = not self.whiteToMove # switch turns
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: # shows that the second square clicked is under attack
                return True
        return False


    # all possible moves (not considering check)
    def allPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):  # number of rows
            # number of columns in each row
            for c in range(len(self.board[r])):
                # first character of a given square is the colour of the piece --> which colour's go it is
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    # second character is the type of piece --> R, N, B, Q, K, p
                    piece = self.board[r][c][1]
                    # generating each possible move for each type of piece on the current board
                    # calls the paired function for the key value in the dictionary in the constructor function
                    self.moveFunctions[piece](r, c, moves)
        return moves

    # get all possible pawn moves for the pawn at [row][col]
    # add to list
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:  # white pawn moves

            # a pawn can move 2 sqaures forward from its original position
            # - one square forward if it is not blocked
            # - capture diagonally
            # check if space in front of pawn is clear
            # check if 2 spaces in front of you is clear
            # check which row pawn is in
            # append moves to list accordingly
            if self.board[r-1][c] == "--":  # one square advancement --> white
                moves.append(Move((r, c), (r-1, c), self.board))
                # checks if two spaces ahead is clear only if one ahead is clear
                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r, c), (r-2, c), self.board))
            if (c-1) >= 0:  # avoids pawn from going off the left of the board
                if self.board[r-1][c-1][0] == 'b':  # enemy piece to capture on left
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnpassantMove=True))
            if (c+1) <= 7:
                if self.board[r-1][c+1][0] == 'b':  # enemy piece to capture on the right
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r-1, c+1), self.board, isEnpassantMove=True))

        else:  # black pawn moves
            if self.board[r+1][c] == "--":  # one square advancement --> black
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    # two square advancement --> black
                    moves.append(Move((r, c), (r+2, c), self.board))
            if (c-1) >= 0:
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r+1, c-1), self.board, isEnpassantMove=True))
            if (c+1) <= 7:
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r+1, c+1), self.board, isEnpassantMove=True))




    # get all possible Rook moves at [row][col]
    # add to list
    def getRookMoves(self, r, c, moves):
        # rooks can move left/right/up/down
        # no limit of squares providing there is no piece blocking them
        # they can capture in their direction of movement
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))# up, left, down, right
        if self.whiteToMove:# enemyColour = 'b' if self.whiteToMove else 'w'
            enemyColour = 'b'
        else:
            enemyColour = 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:# if the direction is on the board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColour:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break


    # get all possible Knight moves at [row][col]
    # add to list
    def getKnightMoves(self, r, c, moves):
        # knights can move in L shapes e.g. (one left, two up), (two left, one up)
        # they can capture a piece on the squares they can move to
        knightDirections = ((-2,-1), (-2,1), (-1, -2), (-1,2), (1,-2), (1,2), (2,-1), (2,1))# knightMoves in tutorial
        allyColour = "w" if self.whiteToMove else "b"
        for k in knightDirections:
            endRow = r + k[0]
            endCol = c + k[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColour:
                    moves.append(Move((r, c), (endRow, endCol), self.board))
    
    # get all possible Bishop moves at [row][col]
    # add to list
    def getBishopMoves(self, r, c, moves):
        # bishops move diagonally
        # no limit of squares providing a piece is not blocking them
        # can capture pieces in their direction of movement
        directions = ((-1,-1), (-1,1), (1,-1), (1,1)) # diagonal directions
        enemyColour = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r,c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColour:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    # get all possible King moves at [row][col]
    # add to list
    def getKingMoves(self, r, c, moves):
        # King can move in any direction
        # limit of one square in any direction
        # can capture any piece except the opposing king and only if the move doesn't make the king go into check
        kingMoves = ((-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1))
        allyColour = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColour:
                    moves.append(Move((r,c), (endRow, endCol), self.board))
        
    

    # generate all valid castle moves for the king at (r,c) and add to list of moves
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return # cannot castle whilst in check
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)

        # update the castle rights given the move
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:# white rook starts on row 7
                if move.startCol == 0:# left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:# right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:# white rook starts on row 7
                if move.startCol == 0:# left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:# right rook
                    self.currentCastlingRight.bks = False
        
        # if a rook is captured
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bks = False


    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r,c), (r, c+2), self.board, isCastleMove=True))


    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
             if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r,c), (r, c-2), self.board, isCastleMove=True))
    
    # get all possible Queen moves at [row][col]
    # add to list
    def getQueenMoves(self, r, c, moves):
        # Queen can move in any direction
        # no limit of squares providing their is no piece blocking them
        # can capture any piece in their direction of movement
        # queen can be modelled as a rook and a bishop
        # --> unlimited forward/backward/left/right direction == rook
        # --> unlimited diagonal direction == bishop
        # therefore, using abstraction:
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)


class CastleRights():
    """Initializing white/black king side and white/black queen side castling right variables"""
    def __init__(self, wks, bks, wqs, bqs):
        """Constructor function for CastleRights class"""
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs




# class which will be responsible for checking if a move can be made
class Move():

    # maps keys to values
    # chess is mapped with rank-file notation where the rank is equal to the depth and file is equal to the width
    # i.e. rank = row, file = depth

    # maps ranks to indexes in board array
    ranksToRows = {"1": 7, "2": 6, "3": 5,
                   "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    # for each key and value, it makes a pair by reversing the previous dictionary
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2,
                   "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSquare, endSquare, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSquare[0]
        self.startCol = startSquare[1]
        self.endRow = endSquare[0]
        self.endCol = endSquare[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        
        # pawn promotion
        """ self.isPawnPromotion = False
        if (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7):
            self.isPawnPromotion = True """
        # ALTERNATIVE WAY OF WRITING CODE
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)


        # en passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        
        # castle move
        self.isCastleMove = isCastleMove
        
        self.isCapture = self.pieceCaptured != '--'
    
        # moveID is similar to a hash function as each move will have a unique ID
        self.moveID = self.startRow * 1000 + self.startCol * \
            100 + self.endRow * 10 + self.endCol
        # print(self.moveID)





        """
        Overriding equals method
        """
    def __eq__(self, other):
        if isinstance(other, Move):  # makes sure if the other object is an instance of the Move class
            # if same piece, same startRow, startCol, endRow, endCol
            return self.moveID == other.moveID
        return False  # if they are not equal
    
    # function which uses the dictionaries to convert array indices into ranks/files for a selected square
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    # function which puts the start positions and end positions into chess notation e.g. e2e4
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    
    # overriding the str() function
    def __str__(self):
        # castle move
        if self.isCastleMove:
            # "O-O" kingside castle
            # "O-O-O" queenside castle
            return "O-O" if self.endCol == 6 else "O-O-O"
        
        endSquare = self.getRankFile(self.endRow, self.endCol)
        
        # pawn moves
        if self.pieceMoved[1] == 'p':
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare
        
        # pawn promotions
        #if self.isPawnPromotion:


        # two of the same type of piece moving to a square, Nbd2 if both Knights can move to d2

        # adding + for a check move, and # for a checkmate move

        # piece moves
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += 'x'
        return moveString + endSquare
# This file is the main driver file
# It will handle user input and display current 'state' object
import pygame as p
import ChessEngine, SmartMoveFinder
# to allow interaction with the board whilst the AI is 'thinking'
from multiprocessing import Process, Queue

# initialising pygame so there are no module-related errors
p.init()
# set the title of the window
p.display.set_caption("Chess")


# using capitals to set constants
# using constants to set dimensions of pygame window
BOARD_WIDTH = BOARD_HEIGHT = 512
# dimesnions of move log
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
# dimensions of chess board are 8x8
DIMENSIONS = 8
# size of squares on chess board using integer division
SQ_SIZE = BOARD_HEIGHT // DIMENSIONS
# for animations
MAX_FPS = 15
# initil dictionary of images
IMAGES = {}


def loadImages():

    '''Initialising a global dictionary of images - this will be called once in main()'''
    # Images should only be loaded into memory once so the game plays smoothly
    # Loading images in every frame would become noticeable to the user

    # loading all pieces into an array
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK','wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    # setting up a for loop which will assign the respective image of the piece to the piece itself
    for piece in pieces:
        # concatenating the address of the image to the name of the piece
        # using the concept of key-value pairs in Python dictionaries
        # using pygame.transform.scale to scale the images to the allocated 'SQ_SIZE' constant mentioned above
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():

    '''Main driver for code --> handle user input --> update graphics'''

    # dimensions of pygame window
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    # creating clock
    clock = p.time.Clock()
    moveLogFont = p.font.SysFont("Arial", 16, False, False)#fontsize=12
    # importing the GameState class from the ChessEngine file to allow access to the current state of board and all over methods
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # if a valid move is made, only then should a new set of moves be generated --> for efficiency
    animate = False # flag variable for when a move should be animated
    loadImages()  # one time --> before while loop
    running = True

    # no square has been selected initially
    # this tuple will store a row and column value
    squareSelected = ()

    # keeps track of player clicks (two tuples) -> [(6, 4), (4, 4)]
    # first click is piece selected, second click is location to move it too
    playerClicks = []
    gameOver = False

    # if a human is playing white, then this will be true
    # if an AI is playing, then false
    # playerTwo applies to black
    # optimised for one difficulty level AI
    # set both to false for AI vs AI
    playerOne = True
    playerTwo = False

    AIThinking = False
    moveFinderProcess = None
    moveUndone = False

    while running:

        # aim is to be able to interact with chess board but not be able to make a move whilst the AI is thinking of a move
        # do not want an unresponsive board whilst the AI is thinking of a move
        # use of asyncrhonous methods
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        # checks if the event happening is the quit button
        for e in p.event.get():
            if e.type == p.QUIT:
                # closes loop if the program is not running anymore
                running = False

            # adding mouse event handling
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()  # (x,y) location of the mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if squareSelected == (row, col) or col >= 8:  # user clicked same square twice or user clicked move log panel
                        squareSelected = ()  # deselect
                        playerClicks = []  # clear previous click
                    else:
                        squareSelected = (row, col)
                        # appends first and second click to playerClicks array
                        playerClicks.append(squareSelected)
                    if len(playerClicks) == 2 and humanTurn:  # --> after second click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        # FOR TESTING/DEBUGGING PURPOSES
                        #print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                squareSelected = ()  # reset user clicks
                                playerClicks = []
                        if not moveMade:# invalid move or user changed mind about piece
                            playerClicks = [squareSelected]

            # adding key handling
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # 'z' triggers the undoMove function to be called from the ChessEngine file
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                    
                if e.key == p.K_r: #reset the board when 'r' is pressed
                    # reinitialise gs
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    squareSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True

        # AI Move Finder + threading
        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                print("thinking...")
                returnQueue = Queue()# used to pass data between threads
                # target is the function to be called
                moveFinderProcess = Process(target=SmartMoveFinder.findBestMove, args=(gs, validMoves, returnQueue))
                moveFinderProcess.start()# call findBestMove(gs, validMoves, returnQueue)

            if not moveFinderProcess.is_alive():# is the moveFinderProcess still running?
                print("done thinking")
                AIMove = returnQueue.get()
                if AIMove is None:
                    # e.g. next move is checkmate
                    AIMove = SmartMoveFinder.findRandomMove(validMoves)
                gs.makeMove(AIMove)
                moveMade = True
                animate = True
                AIThinking = False


        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False

        drawGameState(screen, gs, validMoves, squareSelected, moveLogFont)

        if gs.checkmate or gs.stalemate:
            gameOver = True
            text =  'Stalemate' if gs.stalemate else 'Black wins by checkmate' if gs.whiteToMove else 'White wins by checkmate'
            drawEndGameText(screen, text)

        
        # makes clock tick at maximum 15 fps
        clock.tick(MAX_FPS)
        # updates select portion of the screen
        p.display.flip()



# gs from tutorial = GameState in my code

'''
Graphics handling
'''


def drawGameState(screen, gs, validMoves, squareSelected, moveLogFont):

    '''draw the current board which takes screen and the GameState class as parameters'''

    # squares must be drawn before pieces so the pieces will be visible
    # --> draws squares on the board --> can be used to suggets moves to the user
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, squareSelected)
    drawPieces(screen, gs.board)  # draws pieces on top of squares
    drawMoveLog(screen, gs, moveLogFont)

def drawBoard(screen):

    '''Draw squares on the board / top left square = light'''

    # using grey as black pieces will not be visible on traditional black
    colours = [p.Color("white"), p.Color("gray")]
    # for loop for rows
    for r in range(DIMENSIONS):
        # for loop for columns
        for c in range(DIMENSIONS):
            colour = colours[((r+c) % 2)]
            p.draw.rect(screen, colour, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def highlightSquares(screen, gs, validMoves, squareSelected):

    '''Highlight square selected and moves for piece selected'''

    if squareSelected != ():
        r, c = squareSelected
        #                               if whiteToMove: --> assign 'w' else assign 'b'
        # then compare to board[r][c][0]
        # checks if square selected is a piece that can be moved
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            # highlight the selected square
            # Surface allows shapes/text to be drawn on top of existing objects
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) # transparency value --> 0=transparent, 255=opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            # highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))


def drawPieces(screen, board):

    '''draw the pieces on the board using the current gs.board'''

    for r in range(DIMENSIONS):
        for c in range(DIMENSIONS):
            # goes trhough 2D array from ChessEngine one by one
            piece = board[r][c]
            if piece != "--":  # draws piece if the square is not empty
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawMoveLog(screen, gs, font):
    '''Draws the move log'''
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):# go through moveLog 2 at a time
        #(turn 1 not turn 0 and keeps track in form: 1. f2f5 f5f2 2.e2e4 e7e5 etc.)
        moveString = str(i//2 + 1) + ". " + str(moveLog[i]) + " "# str function here is defined in ChessEngine
        if i+1 < len(moveLog): #make sure black made a move
            moveString += str(moveLog[i+1]) + "  "
        moveTexts.append(moveString)
    
    movesPerRow = 3
    padding = 5
    lineSpacing = 2
    textY = padding
    for i in range(0, len(moveTexts), movesPerRow):# put 'movesPerRow' number of moves on a row in the move log panel
        text = ""
        for j in range(movesPerRow):
            if i+j < len(moveTexts):
                text += moveTexts[i+j]
        textObject = font.render(text, True, p.Color('white'))  
        # shadowing effect for readability
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing





def animateMove(move, screen, board, clock):

    '''Animating a move'''

    colours = [p.Color("white"), p.Color("gray")]
    dR = move.endRow - move.startRow # delta rows --> change in rows
    dC = move.endCol - move.startCol # delta columns --> change in columns
    framesPerSquare = 10 # frames to move one square
    # framecount = frames per sqaure * number of squares moved
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = ((move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)) # frame/frameCount = how far through the animation
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece moved from its ending square
        colour = colours[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, colour, endSquare)
        # draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60) # 60 frames per second for animation


def drawEndGameText(screen, text):

    '''Draw text on screen for when the game ends by stalemate/checkmate'''

    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    # shadowing effect for readability
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH/2 - textObject.get_width()/2, BOARD_HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2,2))






if __name__ == '__main__':
    main()
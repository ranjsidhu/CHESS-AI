import pygame as p
import ChessEngine, SmartMoveFinder
from multiprocessing import Process, Queue

p.init()
p.display.set_caption("Chess")



# Setting the size of the board.
BOARD_WIDTH = BOARD_HEIGHT = 512

# Setting the size of the move log panel.
MOVE_LOG_PANEL_WIDTH = 280
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT

# Setting the number of rows and columns in the board.
DIMENSIONS = 8

# This is the size of each square on the board.
SQ_SIZE = BOARD_HEIGHT // DIMENSIONS

# Limiting the number of frames per second that the game will run at.
MAX_FPS = 15

# Creating a dictionary of images.
IMAGES = {}


def loadImages():
    """
    The function loads all the images of the pieces and scales them to the appropriate size
    """

    pieces = ['wp', 'wR', 'wN', 'wB', 'wK','wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():


   # Creating a screen object that is a pygame display object.
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))

    clock = p.time.Clock()
    moveLogFont = p.font.SysFont("Arial", 16, False, False)

    # Initializing the game state.
    gs = ChessEngine.GameState()
    # Getting the valid moves for the current player.
    validMoves = gs.getValidMoves()

    moveMade = False
    animate = False
    loadImages()
    running = True
    squareSelected = ()
    playerClicks = []
    gameOver = False
    playerOne = True
    playerTwo = False
    AIThinking = False
    moveFinderProcess = None
    moveUndone = False

    while running:

        # A way to check if the current player is human or not.
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        # This is a loop that runs through all the events that are happening in the game.
        for e in p.event.get():
            # This is the code that is checking if the user has clicked the close button.
            if e.type == p.QUIT:

                running = False


            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if squareSelected == (row, col) or col >= 8:
                        squareSelected = ()
                        playerClicks = []
                    else:
                        squareSelected = (row, col)
                        playerClicks.append(squareSelected)
                    if len(playerClicks) == 2 and humanTurn:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        # FOR TESTING/DEBUGGING PURPOSES
                        #print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                squareSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [squareSelected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                    if AIThinking:
                        # Terminating the process that is running the move finder.
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                    
                if e.key == p.K_r:
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

        # This is the code that is running the simulation of the game.
        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                print("thinking...")
                # The below code is creating a queue that will be used to send data from the child
                # process back to the parent process.
                returnQueue = Queue()
                # This is a multiprocessing function that is used to find the best move.
                moveFinderProcess = Process(target=SmartMoveFinder.findBestMove, args=(gs, validMoves, returnQueue))
                # Starting a new process that will run the moveFinder.py script.
                moveFinderProcess.start()

            # This is checking if the process is still running. If it is not running, then it is done.
            if not moveFinderProcess.is_alive():
                print("done thinking")
                # Getting the move from the queue and returning it.
                AIMove = returnQueue.get()
                # Checking if the move is None. If it is, then it is not a valid move.
                if AIMove is None:
                    AIMove = SmartMoveFinder.findRandomMove(validMoves)
                # Making the move that the AI has determined is the best move.
                gs.makeMove(AIMove)
                moveMade = True
                animate = True
                AIThinking = False


        if moveMade:
            if animate:
                # Animating the last move in the move log.
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            # Getting all the valid moves for the current player.
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False

        # Drawing the game state.
        drawGameState(screen, gs, validMoves, squareSelected, moveLogFont)

        # This is checking if the game is over by checkmate or stalemate. If it is, then it will set
        # the gameOver variable to True and set the text to the appropriate message. Then it will draw
        # the text on the screen.
        if gs.checkmate or gs.stalemate:
            gameOver = True
            text =  'Stalemate' if gs.stalemate else 'Black wins by checkmate' if gs.whiteToMove else 'White wins by checkmate'
            drawEndGameText(screen, text)

        # Creating a clock object that will be used to control the frame rate of the game.
        clock.tick(MAX_FPS)
        # Updating the screen.
        p.display.flip()

def drawGameState(screen, gs, validMoves, squareSelected, moveLogFont):
    """
    Draws the game state to the screen
    
    :param screen: the pygame screen object
    :param gs: the game state
    :param validMoves: a list of valid moves
    :param squareSelected: a tuple containing the coords of the square selected (in
    :param moveLogFont: The font to use for the move log
    """

    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, squareSelected)
    drawPieces(screen, gs.board)
    drawMoveLog(screen, gs, moveLogFont)

def drawBoard(screen):
    """
    Draws the board on the screen.
    
    :param screen: the screen to draw the board on
    """

    colours = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSIONS):
        for c in range(DIMENSIONS):
            colour = colours[((r+c) % 2)]
            p.draw.rect(screen, colour, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def highlightSquares(screen, gs, validMoves, squareSelected):
    """
    This function highlights the squares that are valid moves for the selected piece
    
    :param screen: the display variable
    :param gs: the global state of the game
    :param validMoves: a list of valid moves. For example, it would be [3, 5, 12, 20]
    :param squareSelected: a tuple of the square which is currently selected by the player
    """

    if squareSelected != ():
        r, c = squareSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

def drawPieces(screen, board):
    """
    Draws the pieces on the board.
    
    :param screen: the screen to draw the pieces on
    :param board: a 2D list containing the pieces on the board
    """

    for r in range(DIMENSIONS):
        for c in range(DIMENSIONS):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawMoveLog(screen, gs, font):
    """
    Draws the move log.
    
    :param screen: the pygame screen object
    :param gs: the game state
    :param font: the font object that has been used to render the text
    """


    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ". " + str(moveLog[i]) + " "
        if i+1 < len(moveLog):
            moveString += str(moveLog[i+1]) + "  "
        moveTexts.append(moveString)
    
    movesPerRow = 3
    padding = 5
    lineSpacing = 2
    textY = padding
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i+j < len(moveTexts):
                text += moveTexts[i+j]
        textObject = font.render(text, True, p.Color('white'))  
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing

def animateMove(move, screen, board, clock):
    """
    This function takes a move, a screen, a board, and a clock, and animates the move
    
    :param move: a Move object
    :param screen: the pygame screen object
    :param board: the game board surface
    :param clock: the pygame clock object
    """

    colours = [p.Color("white"), p.Color("gray")]
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = ((move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount))
        drawBoard(screen)
        drawPieces(screen, board)
        colour = colours[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, colour, endSquare)
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawEndGameText(screen, text):
    """
    Draws the text that appears when the game ends.
    
    :param screen: The screen to draw the text to
    :param text: The text to be displayed
    """

    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH/2 - textObject.get_width()/2, BOARD_HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2,2))


if __name__ == '__main__':
    main()

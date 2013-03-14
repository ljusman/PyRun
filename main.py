import random, copy, os, pygame, sys, player, AI
import constants as CONST
from pygame.locals import *

JUMPING_DURATION = 500      # milliseconds
HORZ_MOVE_INCREMENT = 4     # pixels
TIME_AT_PEAK = JUMPING_DURATION / 2
JUMP_HEIGHT = 200           # pixels


# Here is the place to define constants for AI implementation...
SOCCER_BALL_POSITION = ((WINWIDTH - 100), HALF_WINHEIGHT - 100)
SOCCER_BALL_SIZE = (16, 16)
SOCCER_GRAVITY = 0.02
SOCCER_FLOOR_ADJUSTMENT_FACTOR = 2.6
SOCCER_ROTATE_INCREMENT = 2
aiMoveStarted = False

def floorY():
    ''' The Y coordinate of the floor, where the man is placed '''
    return WINHEIGHT - HALF_WINHEIGHT

def jumpHeightAtTime(elapsedTime):
    ''' The height of the jump at the given elapsed time (milliseconds) '''
    return ((-1.0/TIME_AT_PEAK**2)* \
        ((elapsedTime-TIME_AT_PEAK)**2)+1)*JUMP_HEIGHT

def main():
    global FPSCLOCK, DISPLAYSURF, IMAGESDICT, BASICFONT, PLAYERIMAGES, currentImage
    # Pygame initialization and basic set up of the globalvariables
    pygame.init()
    FPSCLOCK = pygame.time.Clock() # Creates an object to keep track of time.

    DISPLAYSURF = pygame.display.set_mode((CONST.WINWIDTH, CONST.WINHEIGHT))

    pygame.display.set_caption('PyRun')
    BASICFONT = pygame.font.Font('freesansbold.ttf',18)

    # This is a global Dict object (or dictionary object) which
    # contains all of the images that we will use in the game
    IMAGESDICT = {
        'title': pygame.image.load('img/title.png'),
        'player': pygame.image.load('img/princess.png'),
        'soccerAI': pygame.image.load('img/soccer_ball.png')
        }    

    # PLAYERIMAGES is a list of all possible characters the player can be.
    # currentImage is the index of the player's current player image.
    currentImage = 0
    # PLAYERIMAGES = [IMAGESDICT['princess']]
    
    

    startScreen() # function which shows the start menu

    runGame()

def runGame():


    ''' set up initial player object
        This object contains the following keys:
            surface: the image of the player
            facing: the direction the player is facing
            x: the left edge coordinate of the player on the window
            y: the top edge coordinate of the player on the window
            width: the width of the player image
            height: the height of the player image
    '''
    # Initialize the player object
    p = player.Player(
        (CONST.HALF_WINWIDTH,CONST.HALF_WINHEIGHT),
        (30,80),
        IMAGESDICT['player']
        )

    IMGSCALE = pygame.transform.scale(IMAGESDICT['soccerAI'], SOCCER_BALL_SIZE)

    # Initialize the AI object
    soccerBall = AI.soccerBall(        
        SOCCER_BALL_POSITION,
        SOCCER_BALL_SIZE,
        IMGSCALE,
        'left'
        )    

    moveLeft  = False
    moveRight = False
    moveUp    = False
    moveDown  = False
	
    jumping = False    
	
    while True: # main game loop

        # Draw the background
        DISPLAYSURF.fill(CONST.BGCOLOR)

        # parse the level map
        level_map = tiledtmxloader.tmxreader.TileMapParser().parse_decode('textlevel.tmx')

        # load the images using pygame
        resources - tiledtmxloader.helperspygame.ResourceLoaderPygame()
        resources.load(level_map)

        # prepare map rendering
        assert level_map.orientation == "orthogonal"

        # renderer
        renderer = tiledtmxloader.helperspygame.RendererPygame()

        # retrieve the layers
        sprite_layers = tiledtmxloader.helperspygame.get_layers_from_map(resources)

        # filter layers
        sprite_layers = [layer for layer in sprite_layers if not layer.is_object_group]
        
        # Draw the player
        DISPLAYSURF.blit(p.image, p.get_rect())

        # This loop will handle all of the player input events
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                if event.key in (K_UP, K_w, K_SPACE):
                    moveDown = False
                    moveUp = True
                elif event.key in (K_DOWN, K_s):
                    moveUp = False
                    moveDown = True
                elif event.key in (K_LEFT, K_a):
                    moveRight = False
                    moveLeft = True
                elif event.key in (K_RIGHT, K_d):
                    moveLeft = False
                    moveRight = True

            elif event.type == KEYUP:
                # stop moving the player
                if event.key in (K_LEFT, K_a):
                    moveLeft = False
                elif event.key in (K_RIGHT, K_d):
                    moveRight = False
                elif event.key in (K_UP, K_w, K_SPACE):
                    moveUp = False
                elif event.key in (K_DOWN, K_s):
                    moveDown = False            
                elif event.key == K_ESCAPE:
                        terminate()

        if jumping:
            t = pygame.time.get_ticks() - jumpingStart
            if t > JUMPING_DURATION:
                jumping = False
                jumpHeight = 0
            else:
                jumpHeight = jumpHeightAtTime(t)
            p.y = floorY() - jumpHeight
        
        # actually move the player
        if moveLeft:
            p.x -= CONST.MOVERATE
        if moveRight:
            p.x += CONST.MOVERATE
        if moveUp:
            if not jumping:
                jumping = True
                jumpingStart = pygame.time.get_ticks()
        if moveDown:
            #p.y += MOVERATE
            pass

        # Preliminaries of soccer ball AI
        soccerBall.doSoccerBallAction(p, floorY() + (p.height/SOCCER_FLOOR_ADJUSTMENT_FACTOR), SOCCER_GRAVITY, WINWIDTH)
        ##################################
        

        # Draw the background
        DISPLAYSURF.fill(CONST.BGCOLOR)

        # Draw the player
        DISPLAYSURF.blit(p.image, p.get_rect())

        # Draw the soccer ball AI
        SOCCER_IMG_ROT = pygame.transform.rotate(soccerBall.image, soccerBall.soccerBallRotate(SOCCER_ROTATE_INCREMENT))
        DISPLAYSURF.blit(SOCCER_IMG_ROT, soccerBall.get_rect())
    
        pygame.display.update()
        FPSCLOCK.tick()

def startScreen():
    # Position the title image.
    titleRect = IMAGESDICT['title'].get_rect()
    topCoord = 50 # topCoord track where to position the top of the text
    titleRect.top = topCoord
    titleRect.centerx = CONST.HALF_WINWIDTH
    topCoord += titleRect.height

    # Unfortunately Pygame's font and text system only show one line at
    # a time, so we can't use string with the \n newline characters in them.
    # So we will use a list with each line in it,
    instructionText = ['Arrow keys or WASD to move',
                        'Esc to quit.']

    # Star with drawing a black color to the entire window
    DISPLAYSURF.fill(CONST.BGCOLOR)

    #Draw the title image to the window:
    DISPLAYSURF.blit(IMAGESDICT['title'], titleRect)

    # Position and draw the text.
    for i in range(len(instructionText)):
        instSurf = BASICFONT.render(instructionText[i], 1, CONST.TEXTCOLOR)
        instRect = instSurf.get_rect()
        topCoord += 10 # 10 pixels will go in between each line of text.
        instRect.top = topCoord
        instRect.centerx = CONST.HALF_WINWIDTH
        topCoord += instRect.height # Adjust for the height of the line.
        DISPLAYSURF.blit(instSurf, instRect)

    while True: # Main loop for the start screen.
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                return # user has pressed a key, so return.

        # Display the DISPLAYSURF contents to the actual screen.
        pygame.display.update()
        FPSCLOCK.tick()

def terminate():
    pygame.quit()
    sys.exit()

# Checks to see if the file being run is called main, i.e. main.py
# If so it runs the main() function.
if __name__ == '__main__':
    main()
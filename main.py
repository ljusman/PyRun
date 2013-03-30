import random, copy, os, pygame, sys, player, AI
from pygame.locals import *

FPS = 30 # frames per second to update the screen
WINWIDTH = 800 # width of the program's window, in pixels
WINHEIGHT = 600 # height in pixels
MOVERATE = 0.5 # How fast the player moves
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)

CAM_MOVE_SPEED = 5 # how many pixels per frame the camera moves

BRIGHTBLUE  = (  0, 170, 255)
WHITE       = (255, 255, 255)
BGCOLOR     = BRIGHTBLUE
TEXTCOLOR   = WHITE

LEFT    = 'left'
RIGHT   = 'right'

JUMPING_DURATION = 500      # milliseconds
HORZ_MOVE_INCREMENT = 4     # pixels
TIME_AT_PEAK = JUMPING_DURATION / 2
JUMP_HEIGHT = 200           # pixels


# Here is the place to define constants for AI implementation...
SOCCER_BALL_POSITION = ((WINWIDTH - 100), (HALF_WINHEIGHT - 100))
SOCCER_BALL_SIZE = (16, 16)
SOCCER_GRAVITY = 0.01
SOCCER_FLOOR_ADJUSTMENT_FACTOR = 2.6
SOCCER_ROTATE_INCREMENT = 2
aiMoveStarted = False

BANANA_PEEL_POSITION = ((WINWIDTH - 100), (HALF_WINHEIGHT))
BANANA_PEEL_SIZE = (50, 50)
BANANA_PEEL_INIT_SLIP_TIME = 0
BANANA_ROTATE_FIRST = -2
BANANA_ROTATE_SECOND = 0
BANANA_PEEL_FADE_DECREMENT = -4

SPIKES_POSITION = ((WINWIDTH - 200), (HALF_WINHEIGHT - 3))
SPIKES_SIZE = (128, 50)

def floorY():
    ''' The Y coordinate of the floor, where the man is placed '''
    return WINHEIGHT - HALF_WINHEIGHT

def jumpHeightAtTime(elapsedTime):
    ''' The height of the jump at the given elapsed time (milliseconds) '''
    return ((-1.0/TIME_AT_PEAK**2)* \
        ((elapsedTime-TIME_AT_PEAK)**2)+1)*JUMP_HEIGHT

'''
    Use this method for blitting images that are suppposed to be partially
    or wholly transparent. Apparently, Python does not provide a good
    method (not even set_alpha(), nor convert()/convert_alpha() in
    conjunction with this works) for blitting these types of images.
    You can have a look here:
    http://www.nerdparadise.com/tech/python/pygame/blitopacity/
'''
def blit_alpha(screenSurface, source, location, opacity):
        x = location[0]
        y = location[1]
        temp = pygame.Surface((source.get_width(), source.get_height())).convert()
        temp.blit(screenSurface, (-x, -y))
        temp.blit(source, (0, 0))
        temp.set_alpha(opacity)        
        screenSurface.blit(temp, location)

def makeObstacle(obstacleChoice, position, size, image, direction = 'left'):    
    if (obstacleChoice == 'Spikes'):
        return AI.spikes(position, size, image)
    elif (obstacleChoice == 'Giant rock'):
        return AI.soccerBall(position, size, image, direction)
    elif (obstacleChoice == 'Banana peel'):
        return AI.bananaPeel(position, size, image)
    else:
        return AI.Obstacle((0,0), (0,0), pygame.Surface((0, 0)))
            
    
def main():
    global FPSCLOCK, DISPLAYSURF, IMAGESDICT, BASICFONT, PLAYERIMAGES, currentImage
    # Pygame initialization and basic set up of the globalvariables
    pygame.init()
    FPSCLOCK = pygame.time.Clock() # Creates an object to keep track of time.

    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))

    pygame.display.set_caption('PyRun')
    BASICFONT = pygame.font.Font('freesansbold.ttf',18)

    # This is a global Dict object (or dictionary object) which
    # contains all of the images that we will use in the game
    IMAGESDICT = {
        'title': pygame.image.load('img/title.png'),
        'player': pygame.image.load('img/princess.png'),
        'spikes': pygame.image.load('img/spikes.png'),
        'soccerAI': pygame.image.load('img/soccer_ball.png'),
        'banana_peel': pygame.image.load('img/peel.png')        
        }    

    # PLAYERIMAGES is a list of all possible characters the player can be.
    # currentImage is the index of the player's current player image.
    currentImage = 0
    # PLAYERIMAGES = [IMAGESDICT['princess']]
    
    startScreen() # function which shows the start menu

    runGame()

def runGame():

    '''
        Set up initial player object
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
        (HALF_WINWIDTH,HALF_WINHEIGHT),
        (30,80),
        IMAGESDICT['player']
        )

    SOCCER_IMG_SCALE = pygame.transform.smoothscale(IMAGESDICT['soccerAI'], SOCCER_BALL_SIZE)
    BANANA_IMG_SCALE = pygame.transform.smoothscale(IMAGESDICT['banana_peel'], BANANA_PEEL_SIZE) 
    SPIKES_IMG_SCALE = pygame.transform.smoothscale(IMAGESDICT['spikes'], SPIKES_SIZE)
    
    # For storing our obstacles
    obstacleObjs = []

    # Append a soccer ball and banana peel object to our list of objects
    obstacleObjs.append(makeObstacle('Giant rock', SOCCER_BALL_POSITION, SOCCER_BALL_SIZE, SOCCER_IMG_SCALE))
    obstacleObjs.append(makeObstacle('Spikes', SPIKES_POSITION, SPIKES_SIZE, SPIKES_IMG_SCALE))    

    slipTimeElapsed = BANANA_PEEL_INIT_SLIP_TIME
    
    moveLeft  = False
    moveRight = False
    moveUp    = False
    moveDown  = False
	
    jumping = False    
	
    while True: # main game loop

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
            p.x -= MOVERATE
        if moveRight:
            p.x += MOVERATE
        if moveUp:
            if not jumping:
                jumping = True
                jumpingStart = pygame.time.get_ticks()
        if moveDown:
            #p.y += MOVERATE
            pass

        # Draw the background
        DISPLAYSURF.fill(BGCOLOR)

        # Draw the player
        DISPLAYSURF.blit(p.image, p.get_rect())

        ''' Collision debugging '''
        # pygame.draw.rect(DISPLAYSURF, (0, 0, 0), (p.x, p.y, p.width, p.height))
        # pygame.draw.rect(DISPLAYSURF, (255, 255, 255), (obstacleObjs[0].xPos, obstacleObjs[0].yPos, obstacleObjs[0].width, obstacleObjs[0].height))
        # pygame.draw.rect(DISPLAYSURF, (255, 0, 255), (obstacleObjs[1].xPos, obstacleObjs[1].yPos, obstacleObjs[1].width, obstacleObjs[1].height))

        '''
            We need specific drawing cases for different obstacles,
            since every obstacle could have different methods
            defined for drawing executions. This is what we do
            below.
        '''
        '''
            Here, we have backwards-list checking to avoid a common object
            deletion mistake.
        '''    
        for i in range(len(obstacleObjs) - 1, -1, -1):            
            # Checking if a particular object is a soccer ball.
            if isinstance(obstacleObjs[i], AI.soccerBall):                
                obstacleObjs[i].doSoccerBallAction(p, floorY() + (p.height/SOCCER_FLOOR_ADJUSTMENT_FACTOR), SOCCER_GRAVITY, WINWIDTH)
                SOCCER_IMG_ROT = pygame.transform.rotate(obstacleObjs[i].image, obstacleObjs[i].soccerBallRotate(SOCCER_ROTATE_INCREMENT))
                DISPLAYSURF.blit(SOCCER_IMG_ROT, obstacleObjs[i].get_rect())
            # Checking if a particular object is a banana peel.
            elif isinstance(obstacleObjs[i], AI.bananaPeel):
                obstacleObjs[i].doBananaPeelAction(p, floorY(), SOCCER_GRAVITY, WINWIDTH)
                BANANA_IMG_ROT = pygame.transform.rotate(obstacleObjs[i].image, obstacleObjs[i].slipRotate(floorY(), BANANA_ROTATE_FIRST, BANANA_ROTATE_SECOND))            
                blit_alpha(DISPLAYSURF, BANANA_IMG_ROT, obstacleObjs[i].get_rect(), obstacleObjs[i].doFadeOutBananaPeel(BANANA_PEEL_FADE_DECREMENT))
                # Has the banana peel faded to 0 after being slipped on?
                # (This check has been validated)
                if obstacleObjs[i].getBananaPeelFadeAmount() <= 0:                    
                    del obstacleObjs[i]            
            elif isinstance(obstacleObjs[i], AI.spikes):
                obstacleObjs[i].spikeBump(p)
                DISPLAYSURF.blit(obstacleObjs[i].image, obstacleObjs[i].get_rect())
                # Default for drawing any other obstacles
            else:
                DISPLAYSURF.blit(obstacleObjs[i].image, obstacleObjs[i].get_rect())
                
        pygame.display.update()
        FPSCLOCK.tick()

def startScreen():
    # Position the title image.
    titleRect = IMAGESDICT['title'].get_rect()
    topCoord = 50 # topCoord track where to position the top of the text
    titleRect.top = topCoord
    titleRect.centerx = HALF_WINWIDTH
    topCoord += titleRect.height

    # Unfortunately Pygame's font and text system only show one line at
    # a time, so we can't use string with the \n newline characters in them.
    # So we will use a list with each line in it,
    instructionText = ['Arrow keys or WASD to move',
                        'Esc to quit.']

    # Star with drawing a black color to the entire window
    DISPLAYSURF.fill(BGCOLOR)

    #Draw the title image to the window:
    DISPLAYSURF.blit(IMAGESDICT['title'], titleRect)

    # Position and draw the text.
    for i in range(len(instructionText)):
        instSurf = BASICFONT.render(instructionText[i], 1, TEXTCOLOR)
        instRect = instSurf.get_rect()
        topCoord += 10 # 10 pixels will go in between each line of text.
        instRect.top = topCoord
        instRect.centerx = HALF_WINWIDTH
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

import random, copy, os, pygame, sys, player, AI, tiledtmxloader
from pygame.locals import *

FPS = 30 # frames per second to update the SCREEN
WINWIDTH = 800 # width of the program's window, in pixels
WINHEIGHT = 600 # height in pixels
MOVERATE = 4 # How fast the player moves
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)

CAM_MOVE_SPEED = 5 # how many pixels per frame the camera moves

BRIGHTBLUE  = (  0, 170, 255)
WHITE       = (255, 255, 255)
BGCOLOR     = BRIGHTBLUE
TEXTCOLOR   = WHITE

LEFT    = 'left'
RIGHT   = 'right'

TILEMAP_WIDTH = 32
TILEMAP_LENGTH = 24
TILE_SIZE = 25

COLL_LAYER = 2 # The sprite layer which contains the collision map

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
    global FPSCLOCK, SCREEN, IMAGESDICT, BASICFONT, PLAYERIMAGES, currentImage
    # Pygame initialization and basic set up of the globalvariables
    pygame.init()
    FPSCLOCK = pygame.time.Clock() # Creates an object to keep track of time.

    SCREEN = pygame.display.set_mode((WINWIDTH, WINHEIGHT))

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
        (HALF_WINWIDTH,HALF_WINHEIGHT),
        (30,80),
        IMAGESDICT['player']
        )

    ballImage = pygame.transform.scale(IMAGESDICT['soccerAI'], SOCCER_BALL_SIZE)

    # Initialize the AI object
    soccerBall = AI.soccerBall(        
        SOCCER_BALL_POSITION,
        SOCCER_BALL_SIZE,
        ballImage,
        'left'
        )    

    moveLeft  = False
    moveRight = False
    moveUp    = False
    moveDown  = False
	
    while True: # main game loop

        # parse the level map
        level_map = tiledtmxloader.tmxreader.TileMapParser().parse_decode('testlevel.tmx')

        # load the images using pygame
        resources = tiledtmxloader.helperspygame.ResourceLoaderPygame()
        resources.load(level_map)

        # prepare map rendering
        assert level_map.orientation == "orthogonal"

        # renderer
        renderer = tiledtmxloader.helperspygame.RendererPygame()

        # retrieve the layers
        sprite_layers = tiledtmxloader.helperspygame.get_layers_from_map(resources)

        # filter layers
        sprite_layers = [layer for layer in sprite_layers if not layer.is_object_group]

        # add player to the right layer
        sprite_layers[1].add_sprite(p.get_sprite())

        cam_x = HALF_WINWIDTH
        cam_y = HALF_WINHEIGHT

        # set initial cam position and size
        renderer.set_camera_position_and_size(cam_x, cam_y,WINWIDTH, WINHEIGHT)

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

        if p.isJumping():
            t = pygame.time.get_ticks() - jumpingStart
            if t > JUMPING_DURATION:
                p.jumping = False
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
            if not p.isJumping():
                p.jumping = True
                jumpingStart = pygame.time.get_ticks()
        if moveDown:
            #p.y += MOVERATE
            pass

        step_y = MOVERATE

        step_y = check_collision(p,step_y,sprite_layers[COLL_LAYER])

        # Preliminaries of soccer ball AI
        soccerBall.doSoccerBallAction(p, floorY() + (p.height/SOCCER_FLOOR_ADJUSTMENT_FACTOR), SOCCER_GRAVITY, WINWIDTH)
        ##################################
        
        renderer.set_camera_position(HALF_WINWIDTH, HALF_WINHEIGHT)

        # Draw the background
        #SCREEN.fill(BGCOLOR)
        SCREEN.fill((0, 0, 0))

        # Draw the player
        SCREEN.blit(p.image, p.get_rect())

        # Draw the soccer ball AI
        SOCCER_IMG_ROT = pygame.transform.rotate(soccerBall.image, soccerBall.soccerBallRotate(SOCCER_ROTATE_INCREMENT))
        SCREEN.blit(SOCCER_IMG_ROT, soccerBall.get_rect())
        
        # render the map
        for sprite_layer in sprite_layers:
            if sprite_layer.is_object_group:
                # we dont draw the object group layers
                # you should filter them out if not needed
                continue
            else:
                renderer.render_layer(SCREEN, sprite_layer)

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
    SCREEN.fill(BGCOLOR)

    #Draw the title image to the window:
    SCREEN.blit(IMAGESDICT['title'], titleRect)

    # Position and draw the text.
    for i in range(len(instructionText)):
        instSurf = BASICFONT.render(instructionText[i], 1, TEXTCOLOR)
        instRect = instSurf.get_rect()
        topCoord += 10 # 10 pixels will go in between each line of text.
        instRect.top = topCoord
        instRect.centerx = HALF_WINWIDTH
        topCoord += instRect.height # Adjust for the height of the line.
        SCREEN.blit(instSurf, instRect)

    while True: # Main loop for the start screen.
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                return # user has pressed a key, so return.

        # Display the screen contents to the actual screen.
        pygame.display.update()
        FPSCLOCK.tick()

def terminate():
    pygame.quit()
    sys.exit()

# Checks to see if the file being run is called main, i.e. main.py
# If so it runs the main() function.
if __name__ == '__main__':
    main()
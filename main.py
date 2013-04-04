import random, copy, math, os, pygame, sys, player, AI, tiledtmxloader
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
GRAY_1      = (200, 200, 200)
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
ROCK_BALL_POSITION = ((WINWIDTH - 400), (HALF_WINHEIGHT - 200))
ROCK_BALL_SIZE = (256, 256)
ROCK_GRAVITY = 0.4
ROCK_FLOOR_ADJUSTMENT_FACTOR = 2.6
ROCK_ROTATE_INCREMENT = 4
ROCK_SPEED = 8
aiMoveStarted = False

'''
    Forward slip: BANANA_PEEL_HORI_RISE_SPEED = 20
                  BANANA_PEEL_VERT_RISE_SPEED = -20
                  BANANA_ROTATE_FIRST = 10
    Backward slip: BANANA_PEEL_HORI_RISE_SPEED = -20
                   BANANA_PEEL_VERT_RISE_SPEED = -20
                   BANANA_ROTATE_FIRST = -10
'''
BANANA_PEEL_POSITION = ((WINWIDTH - 500), (HALF_WINHEIGHT))
BANANA_PEEL_SIZE = (50, 50)
BANANA_PEEL_INIT_SLIP_TIME = 10
BANANA_PEEL_HORI_RISE_SPEED = -20
BANANA_PEEL_VERT_RISE_SPEED = -20
BANANA_PEEL_TIME_TO_RISE = 10
BANANA_ROTATE_FIRST = -10
BANANA_ROTATE_SECOND = 0
BANANA_PEEL_FADE_DECREMENT = -25

SPIKES_POSITION = ((WINWIDTH - 200), (HALF_WINHEIGHT - 3))
SPIKES_SIZE = (128, 50)

LOG_POSITION = ((WINWIDTH - 300), (HALF_WINHEIGHT))
LOG_SIZE = (256, 40)

SNAKE_POSITION = ((WINWIDTH - 400), (HALF_WINHEIGHT))
SNAKE_SIZE = (100, 64)
SNAKE_SIZE_2 = (128, 64)
SNAKE_SPEED = 4
SNAKE_FRAME_RATE = 7

BIRD_POSITION = ((WINWIDTH + 10), (HALF_WINHEIGHT - 200))
BIRD_SIZE = (150, 110)
BIRD_SPEED = 12
BIRD_FRAME_RATE = 2

SPIDER_POSITION = ((WINWIDTH - 200), (HALF_WINHEIGHT - 100))
SPIDER_SIZE = (64, 64)
SPIDER_SPEED = 5
SPIDER_FRAME_RATE = 5

MUD_POSITION = ((WINWIDTH - 600), (HALF_WINHEIGHT))
MUD_POSITION_2 = ((WINWIDTH - 600), (HALF_WINHEIGHT - 30))
MUD_SIZE = (150, 40)
MUD_SIZE_2 = (150, 70)
MUD_FRAME_RATE = 10

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

# A function for creating obstacles
def makeObstacle(obstacleChoice, position, size, image, direction = 'left'):    
    if (obstacleChoice == 'Spikes'):
        return AI.spikes(position, size, image)
    elif (obstacleChoice == 'Log'):
        return AI.treeLog(position, size, image)
    elif (obstacleChoice == 'Giant rock'):
        return AI.giantRock(position, size, image, direction)
    elif (obstacleChoice == 'Banana peel'):
        return AI.bananaPeel(position, size, image)
    elif (obstacleChoice == 'Snake'):
        return AI.snake(position, size, image)
    elif (obstacleChoice == 'Bird'):
        return AI.bird(position, size, image)
    elif (obstacleChoice == 'Spider'):
        return AI.spider(position, size, image)
    elif (obstacleChoice == 'Mud'):
        return AI.mud(position, size, image)
    else:
        return AI.Obstacle((0,0), (0,0), pygame.Surface((0, 0)))
            
    
def main():
    global FPSCLOCK, SCREEN, IMAGESDICT, BASICFONT, PLAYERIMAGES, currentImage
    # Pygame initialization and basic set up of the global variables
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
        'spikes': pygame.image.load('img/spikes.png'),
        'rock': pygame.image.load('img/RockRollingImages/00.png'),
        'rock2': pygame.image.load('img/RockRollingImages/01.png'),
        'rock3': pygame.image.load('img/RockRollingImages/02.png'),
        'rock4': pygame.image.load('img/RockRollingImages/03.png'),                                
        'banana_peel': pygame.image.load('img/peel.png'),
        'snake': pygame.image.load('img/SnakeMovingImages/snake.png'),
        'snake2': pygame.image.load('img/SnakeMovingImages/snake2.png'),
        'bird': pygame.image.load('img/BirdFlappingImages/00.png'),
        'bird2': pygame.image.load('img/BirdFlappingImages/01.png'),
        'spider': pygame.image.load('img/SpiderImages/00.png'),
        'spider2': pygame.image.load('img/SpiderImages/01.png'),
        'log': pygame.image.load('img/log.png'),
        'mud': pygame.image.load('img/MudSplashingImages/mud.png'),
        'mud2': pygame.image.load('img/MudSplashingImages/mud_sp.png')
        }    

    # PLAYERIMAGES is a list of all possible characters the player can be.
    # currentImage is the index of the player's current player image.
    currentImage = 0
    # PLAYERIMAGES = [IMAGESDICT['princess']]
    
    

    startScreen() # function which shows the start menu

    runGame()

def runGame():
    '''
        Set up initial player object.    
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
        (25,25),
        IMAGESDICT['player']
        )
    
    ROCK_IMG_SCALE = pygame.transform.smoothscale(IMAGESDICT['rock'], ROCK_BALL_SIZE)
    ROCK_IMG_SCALE_2 = pygame.transform.smoothscale(IMAGESDICT['rock2'], ROCK_BALL_SIZE)
    ROCK_IMG_SCALE_3 = pygame.transform.smoothscale(IMAGESDICT['rock3'], ROCK_BALL_SIZE)
    ROCK_IMG_SCALE_4 = pygame.transform.smoothscale(IMAGESDICT['rock4'], ROCK_BALL_SIZE)
    BANANA_IMG_SCALE = pygame.transform.smoothscale(IMAGESDICT['banana_peel'], BANANA_PEEL_SIZE) 
    SPIKES_IMG_SCALE = pygame.transform.smoothscale(IMAGESDICT['spikes'], SPIKES_SIZE)
    SNAKE_IMG_SCALE = pygame.transform.smoothscale(IMAGESDICT['snake'], SNAKE_SIZE)
    SNAKE_IMG_SCALE_2 = pygame.transform.smoothscale(IMAGESDICT['snake2'], SNAKE_SIZE_2)
    BIRD_IMG_SCALE = pygame.transform.smoothscale(IMAGESDICT['bird'], BIRD_SIZE)
    BIRD_IMG_SCALE_2 = pygame.transform.smoothscale(IMAGESDICT['bird2'], BIRD_SIZE)
    SPIDER_IMG_SCALE = pygame.transform.smoothscale(IMAGESDICT['spider'], SPIDER_SIZE)
    SPIDER_IMG_SCALE_2 = pygame.transform.smoothscale(IMAGESDICT['spider2'], SPIDER_SIZE)
    LOG_IMG_SCALE = pygame.transform.smoothscale(IMAGESDICT['log'], LOG_SIZE)
    MUD_IMG_SCALE = pygame.transform.smoothscale(IMAGESDICT['mud'], MUD_SIZE)
    MUD_IMG_SCALE_2 = pygame.transform.smoothscale(IMAGESDICT['mud2'], MUD_SIZE_2)

    # Animations for various AI    
    snakeAnimation = [SNAKE_IMG_SCALE, SNAKE_IMG_SCALE_2]
    birdAnimation = [BIRD_IMG_SCALE, BIRD_IMG_SCALE_2]
    spiderAnimation = [SPIDER_IMG_SCALE, SPIDER_IMG_SCALE_2]
    rockAnimation = [ROCK_IMG_SCALE, ROCK_IMG_SCALE_2, ROCK_IMG_SCALE_3, ROCK_IMG_SCALE_4]
    mudAnimation = [MUD_IMG_SCALE, MUD_IMG_SCALE_2]

    giantRock = AI.giantRock(
        ROCK_BALL_POSITION,
        ROCK_BALL_SIZE,
        ROCK_IMG_SCALE,
        LEFT
        )
    
    # For storing our obstacles
    obstacleObjs = []

    # Append a ROCK ball and banana peel object to our list of objects
    obstacleObjs.append(makeObstacle('Giant rock', ROCK_BALL_POSITION, ROCK_BALL_SIZE, ROCK_IMG_SCALE))
    obstacleObjs.append(makeObstacle('Spikes', SPIKES_POSITION, SPIKES_SIZE, SPIKES_IMG_SCALE))
    obstacleObjs.append(makeObstacle('Snake', SNAKE_POSITION, SNAKE_SIZE, SNAKE_IMG_SCALE))
    obstacleObjs.append(makeObstacle('Bird', BIRD_POSITION, BIRD_SIZE, BIRD_IMG_SCALE))
    obstacleObjs.append(makeObstacle('Spider', SPIDER_POSITION, SPIDER_SIZE, SPIDER_IMG_SCALE))
    obstacleObjs.append(makeObstacle('Log', LOG_POSITION, LOG_SIZE, LOG_IMG_SCALE))
    obstacleObjs.append(makeObstacle('Banana peel', BANANA_PEEL_POSITION, BANANA_PEEL_SIZE, BANANA_IMG_SCALE))
    obstacleObjs.append(makeObstacle('Mud', MUD_POSITION, MUD_SIZE, MUD_IMG_SCALE))

    ballImage = pygame.transform.scale(IMAGESDICT['rock'], ROCK_BALL_SIZE)   

    slipTimeElapsed = BANANA_PEEL_INIT_SLIP_TIME
    
    moveLeft  = False
    moveRight = False
    moveUp    = False
    moveDown  = False

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

    # craete player sprite with which we'll work with
    player_sprite = p.get_sprite()

    # add player to the right layer
    sprite_layers[1].add_sprite(player_sprite)

    cam_x = HALF_WINWIDTH
    cam_y = HALF_WINHEIGHT

    # set initial cam position and size
    renderer.set_camera_position_and_size(cam_x, cam_y, WINWIDTH, WINHEIGHT)

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

        # this should simulate constant gravity
        # step_y = MOVERATE

        step_y = check_collision(p,12,sprite_layers[COLL_LAYER])
        p.y += step_y

        player_sprite.rect.midbottom = (p.x, p.y)        
        
        renderer.set_camera_position(HALF_WINWIDTH, HALF_WINHEIGHT)

        # Draw the background
        SCREEN.fill((0, 0, 0))    
                    
        
        # render the map including the player
        for sprite_layer in sprite_layers:
            if sprite_layer.is_object_group:
                # we dont draw the object group layers
                # you should filter them out if not needed
                continue
            else:
                renderer.render_layer(SCREEN, sprite_layer)
        
        ''' Collision debugging '''
        # pygame.draw.rect(SCREEN, (0, 0, 0), (p.x, p.y, p.width, p.height))
        # pygame.draw.rect(SCREEN, (0, 0, 0), (obstacleObjs[0].xPos, obstacleObjs[0].yPos, obstacleObjs[0].width, obstacleObjs[0].height))
        # pygame.draw.rect(SCREEN, (255, 0, 255), (obstacleObjs[1].xPos, obstacleObjs[1].yPos, obstacleObjs[1].width, obstacleObjs[1].height))

                
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
            # Player collision checking with the obstacles.
            if p.isTouching(obstacleObjs[i].xPos, obstacleObjs[i].yPos, obstacleObjs[i].yPos + obstacleObjs[i].height):
                soundObj = pygame.mixer.Sound('Sounds/Spikes.wav')
                soundObj.play()
            ''' Collision boundary drawing (for debug) '''
            # pygame.draw.rect(SCREEN, GRAY_1, (obstacleObjs[i].xPos, obstacleObjs[i].yPos, obstacleObjs[i].width, obstacleObjs[i].height))
            # Checking if a particular object is a rock.
            if isinstance(obstacleObjs[i], AI.giantRock):
                obstacleObjs[i].setSpeed(ROCK_SPEED)
                obstacleObjs[i].doGiantRockAction(p, floorY(), ROCK_GRAVITY, WINWIDTH)
                # CHOPPED_ROCK = pygame.transform.rotozoom(obstacleObjs[i].image, obstacleObjs[i].giantRockRotate(ROCK_ROTATE_INCREMENT), 2.0)               
                # CHOPPED_ROCK = pygame.transform.scale(CHOPPED_ROCK, obstacleObjs[i].image.get_size())                                
                SCREEN.blit(rockAnimation[obstacleObjs[i].animateToNext(2, 8)], obstacleObjs[i].get_rect())                            
            # Checking if a particular object is a banana peel.
            elif isinstance(obstacleObjs[i], AI.bananaPeel):
                obstacleObjs[i].setHoriAndVertRiseSpeeds(BANANA_PEEL_HORI_RISE_SPEED, BANANA_PEEL_VERT_RISE_SPEED)
                obstacleObjs[i].doBananaPeelAction(p, floorY(), ROCK_GRAVITY, BANANA_PEEL_TIME_TO_RISE, WINWIDTH)
                BANANA_IMG_ROT = pygame.transform.rotate(obstacleObjs[i].image, obstacleObjs[i].slipRotate(floorY(), BANANA_ROTATE_FIRST, BANANA_ROTATE_SECOND))            
                blit_alpha(SCREEN, BANANA_IMG_ROT, obstacleObjs[i].get_rect(), obstacleObjs[i].doFadeOutBananaPeel(BANANA_PEEL_FADE_DECREMENT))
                # Has the banana peel faded to 0 after being slipped on?
                # (This check has been validated)
                if obstacleObjs[i].getBananaPeelFadeAmount() <= 0:                    
                    del obstacleObjs[i]
            # Checking if a particular object represents the spikes
            elif isinstance(obstacleObjs[i], AI.spikes):
                obstacleObjs[i].spikeBump(p)
                SCREEN.blit(obstacleObjs[i].image, obstacleObjs[i].get_rect())
            # Checking if the object is a tree log
            elif isinstance(obstacleObjs[i], AI.treeLog):
                obstacleObjs[i].collidedHardWith(p)
                SCREEN.blit(obstacleObjs[i].image, obstacleObjs[i].get_rect())
            # Checking if the object is a snake
            elif isinstance(obstacleObjs[i], AI.snake):
                obstacleObjs[i].setFrameRate(SNAKE_FRAME_RATE)
                if (obstacleObjs[i].doSnakeAction(SNAKE_SPEED)):
                    SCREEN.blit(snakeAnimation[0], obstacleObjs[i].get_rect())
                else:
                    SCREEN.blit(snakeAnimation[1], obstacleObjs[i].get_rect())
                if (obstacleObjs[i].xPos + obstacleObjs[i].width < 0):
                    del obstacleObjs[i]
            # Checking if the object is a bird
            elif isinstance(obstacleObjs[i], AI.bird):
                obstacleObjs[i].setFrameRate(BIRD_FRAME_RATE)
                if (obstacleObjs[i].doBirdAction(BIRD_SPEED)):
                    SCREEN.blit(birdAnimation[0], obstacleObjs[i].get_rect())
                else:
                    SCREEN.blit(birdAnimation[1], obstacleObjs[i].get_rect())
                if (obstacleObjs[i].xPos + obstacleObjs[i].width < 0):
                    del obstacleObjs[i]
            # Checking if the object is a spider
            elif isinstance(obstacleObjs[i], AI.spider):
                obstacleObjs[i].setFrameRate(SPIDER_FRAME_RATE)
                if (obstacleObjs[i].doSpiderAction(SPIDER_SPEED)):
                    SCREEN.blit(spiderAnimation[0], obstacleObjs[i].get_rect())                    
                else:
                    SCREEN.blit(spiderAnimation[1], obstacleObjs[i].get_rect())                
                pygame.draw.rect(SCREEN, GRAY_1, obstacleObjs[i].getWebStringRect())
            elif isinstance(obstacleObjs[i], AI.mud):
                obstacleObjs[i].setFrameRate(MUD_FRAME_RATE)
                if (obstacleObjs[i].doMudAction(MUD_FRAME_RATE)):
                    SCREEN.blit(mudAnimation[0], obstacleObjs[i].get_rect())                    
                else:
                    SCREEN.blit(mudAnimation[1], obstacleObjs[i].get_rect()) 
            # Default for drawing any other obstacles
            else:
                SCREEN.blit(obstacleObjs[i].image, obstacleObjs[i].get_rect())                                        
                
            
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

def check_collision(player,step_y,coll_layer):
    # find the tile location of the player
    tile_x = int((player.x) // coll_layer.tilewidth)
    tile_y = int((player.y) // coll_layer.tileheight)
    
    # find the tiles around the hero and extract their rects for collision
    tile_rects = []
    for diry in (-1,0, 1):
        for dirx in (-1,0,1):
            if coll_layer.content2D[tile_y + diry][tile_x + dirx] is not None:
                tile_rects.append(coll_layer.content2D[tile_y + diry][tile_x + dirx].rect)

    # save the original steps and return them if not canceled
    #res_step_x = step_x
    res_step_y = step_y

    # y direction, floor or ceil depending on the sign of the step
    step_y = special_round(step_y)

    # detect a collision and dont move in y direction if colliding
    if player.get_rect().move(0, step_y).collidelist(tile_rects) > -1:
        res_step_y = 0

    # return the step the hero should do
    return res_step_y

def special_round(value):
    """
    For negative numbers it returns the value floored,
    for positive numbers it returns the value ceiled.
    """
    # same as:  math.copysign(math.ceil(abs(x)), x)
    # OR:
    # ## versus this, which could save many function calls
    # import math
    # ceil_or_floor = { True : math.ceil, False : math.floor, }
    # # usage
    # x = floor_or_ceil[val<0.0](val)

    if value < 0:
        return math.floor(value)
    return math.ceil(value)

def terminate():
    pygame.quit()
    sys.exit()

# Checks to see if the file being run is called main, i.e. main.py
# If so it runs the main() function.
if __name__ == '__main__':
    main()

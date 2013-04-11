import random, copy, math, os, pygame, sys, player, AI, tiledtmxloader, MENU
from pygame.locals import *

FPS = 30 # frames per second to update the SCREEN
WINWIDTH = 800 # width of the program's window, in pixels
WINHEIGHT = 600 # height in pixels
MOVERATE = 6 # How fast the player moves
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
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 105

PLAYER_LAYER = 12
COLL_LAYER = 2 # The sprite layer which contains the collision map
DEATH_LAYER = 3
WIN_LAYER = 4

JUMPING_DURATION = 500      # milliseconds
HORZ_MOVE_INCREMENT = 4     # pixels
TIME_AT_PEAK = JUMPING_DURATION / 2
JUMP_HEIGHT = 10           # pixels

# Here is the place to define constants for AI implementation...
ROCK_BALL_POSITION = ((WINWIDTH - 400), (HALF_WINHEIGHT - 200))
ROCK_BALL_SIZE = (256, 256)
ROCK_GRAVITY = 0.4
ROCK_FLOOR_ADJUSTMENT_FACTOR = 2.6
ROCK_ROTATE_INCREMENT = 4
ROCK_SPEED = 8
aiMoveStarted = False

TIDAL_WAVE_POSITION = ((-30), (HALF_WINHEIGHT - 100))
TIDAL_WAVE_SIZE = (500, 600)

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
    elif (obstacleChoice == 'Tidal wave'):
        return AI.tidalWave(position, size, image)
    else:
        return AI.Obstacle((0,0), (0,0), pygame.Surface((0, 0)))


def main():
    global FPSCLOCK, SCREEN, IMAGESDICT, BASICFONT, PLAYERIMAGES, currentImage
    # Pygame initialization and basic set up of the global variables
    pygame.init()
    pygame.mixer.init()
    FPSCLOCK = pygame.time.Clock() # Creates an object to keep track of time.

    SCREEN = pygame.display.set_mode((WINWIDTH, WINHEIGHT))

    pygame.display.set_caption('PyRun')
    BASICFONT = pygame.font.Font('freesansbold.ttf',18)

    # This is a global Dict object (or dictionary object) which
    # contains all of the images that we will use in the game
    IMAGESDICT = {
        'title': pygame.image.load('img/title.png'),
        'player': pygame.image.load('img/run_01.png'),
        'jump1': pygame.image.load('img/jump_01.png'),
        'jump2': pygame.image.load('img/jump_02.png'),
        'jump3': pygame.image.load('img/jump_03.png'),
        'jump4': pygame.image.load('img/jump_04.png'),
        'run1': pygame.image.load('img/run_01.png'),
        'run2': pygame.image.load('img/run_02.png'),
        'run3': pygame.image.load('img/run_03.png'),
        'run4': pygame.image.load('img/run_04.png'),
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
        'mud2': pygame.image.load('img/MudSplashingImages/mud_sp.png'),
        'tidalWave': pygame.image.load('img/TidalWave.png')
        }

    # PLAYERIMAGES is a list of all possible characters the player can be.
    # currentImage is the index of the player's current player image.
    currentImage = 0
    # PLAYERIMAGES = [IMAGESDICT['princess']]

    Map_Num = startScreen() # function which shows the start menu

    runGame(Map_Num) # run the game

def initializeLevel(file_name, player_layer, player):

     # parse the level map
    level_map = tiledtmxloader.tmxreader.TileMapParser().parse_decode(file_name)

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
    player_sprite = player.get_sprite()

    # add player to the right layer
    sprite_layers[player_layer].add_sprite(player_sprite)

    cam_x = HALF_WINWIDTH
    cam_y = HALF_WINHEIGHT

    # set initial cam position and size
    renderer.set_camera_position_and_size(cam_x, cam_y, WINWIDTH, WINHEIGHT)

    return sprite_layers, player_sprite, player_layer, renderer

def runGame(MAP_NUMBER):
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
        (PLAYER_WIDTH,PLAYER_HEIGHT),
        IMAGESDICT['player']
        )

    # initialize camera variables
    cam_x = HALF_WINWIDTH
    cam_y = HALF_WINHEIGHT

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
    TIDAL_WAVE_IMG_SCALE = pygame.transform.smoothscale(IMAGESDICT['tidalWave'], TIDAL_WAVE_SIZE)

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

    # obstacleObjs.append(makeObstacle('Giant rock', ROCK_BALL_POSITION, ROCK_BALL_SIZE, ROCK_IMG_SCALE))
    # obstacleObjs.append(makeObstacle('Tidal wave', TIDAL_WAVE_POSITION, TIDAL_WAVE_SIZE, TIDAL_WAVE_IMG_SCALE))
    '''
    obstacleObjs.append(makeObstacle('Giant rock', ROCK_BALL_POSITION, ROCK_BALL_SIZE, ROCK_IMG_SCALE))
    obstacleObjs.append(makeObstacle('Spikes', SPIKES_POSITION, SPIKES_SIZE, SPIKES_IMG_SCALE))
    obstacleObjs.append(makeObstacle('Snake', SNAKE_POSITION, SNAKE_SIZE, SNAKE_IMG_SCALE))
    obstacleObjs.append(makeObstacle('Bird', BIRD_POSITION, BIRD_SIZE, BIRD_IMG_SCALE))
    obstacleObjs.append(makeObstacle('Spider', SPIDER_POSITION, SPIDER_SIZE, SPIDER_IMG_SCALE))
    obstacleObjs.append(makeObstacle('Log', LOG_POSITION, LOG_SIZE, LOG_IMG_SCALE))
    obstacleObjs.append(makeObstacle('Banana peel', BANANA_PEEL_POSITION, BANANA_PEEL_SIZE, BANANA_IMG_SCALE))
    obstacleObjs.append(makeObstacle('Mud', MUD_POSITION, MUD_SIZE, MUD_IMG_SCALE))
    '''
    ballImage = pygame.transform.scale(IMAGESDICT['rock'], ROCK_BALL_SIZE)

    slipTimeElapsed = BANANA_PEEL_INIT_SLIP_TIME

    # Initialize moving variables
    moveLeft  = False
    moveRight = False
    moveUp    = False
    moveDown  = False

    pygame.mixer.init()
    if MAP_NUMBER == 0:
        sprite_layers, player_sprite, player_layer, renderer = initializeLevel('ForestLevel.tmx',PLAYER_LAYER,p)        
        pygame.mixer.music.load('Sounds/Level2.mp3')
        obstacleObjs.append(makeObstacle('Giant rock', ROCK_BALL_POSITION, ROCK_BALL_SIZE, ROCK_IMG_SCALE))
    elif MAP_NUMBER == 1:        
        sprite_layers, player_sprite, player_layer, renderer = initializeLevel('SandLevel.tmx',PLAYER_LAYER,p)
        pygame.mixer.music.load('Sounds/NeroNewLifeCut.mp3')
        obstacleObjs.append(makeObstacle('Tidal wave', TIDAL_WAVE_POSITION, TIDAL_WAVE_SIZE, TIDAL_WAVE_IMG_SCALE))
        
    pygame.mixer.music.play(0)        
    frame_count = 0

    while True: # main game loop

        # update player sprite
        sprite_layers[PLAYER_LAYER].remove_sprite(player_sprite)
        player_sprite = p.get_sprite()
        sprite_layers[PLAYER_LAYER].add_sprite(player_sprite)

        # reset applicable variables
        step_x = 0
        step_y = 0

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
        '''
            All the jumping and gravity is handled here.
            If the player is jumping we move them up, otherwise they are moving down (gravity).
            We can alter how quickly the player jumps by altering the moverate or jump duration.
        '''
        if p.isJumping():
            t = pygame.time.get_ticks() - jumpingStart
            if t > JUMPING_DURATION:
                p.jumping = False
                p.change_sprite(
                IMAGESDICT['jump1']
                )
            elif t > JUMPING_DURATION / 2:
                p.change_sprite(
                IMAGESDICT['jump4']
                )
            if t < JUMPING_DURATION and t > 0:
                step_y -= MOVERATE
        elif not p.isJumping():
            step_y += MOVERATE

        # actually move the player
        if moveLeft:
            step_x -= MOVERATE
        if moveRight:
            step_x += MOVERATE
            if not p.isJumping():
                if frame_count is 20:
                    p.change_sprite(
                    IMAGESDICT['run1']
                    )
                elif frame_count is 40:
                    p.change_sprite(
                    IMAGESDICT['run2']
                    )
                elif frame_count is 60:
                    p.change_sprite(
                    IMAGESDICT['run3']
                    )
                elif frame_count is 80:
                    p.change_sprite(
                    IMAGESDICT['run4']
                    )
                if frame_count > 80:
                    frame_count = 0
        if moveUp:
            if not p.isJumping() and p.isOnGround():
                p.jumping = True
                p.onGround = False
                p.change_sprite(
                IMAGESDICT['jump2']
                )
                jumpingStart = pygame.time.get_ticks()
                step_y -= 60               


        if check_game_end(p,step_x,step_y,sprite_layers[DEATH_LAYER]):
            print 'Collided with death layer'
        elif check_game_end(p,step_x,step_y,sprite_layers[WIN_LAYER]):
            print 'Collided with win layer'
        elif p.get_rect().left <= (cam_x-HALF_WINWIDTH*2):
            print 'Collided with left end of screen'
        step_x, step_y = check_collision(p,step_x,step_y,sprite_layers[COLL_LAYER])



        # Apply the steps to the player and the player rect
        p.x += step_x
        p.y += step_y

        player_sprite.rect.midbottom = (p.x, p.y)

        # Set the new camera position
        renderer.set_camera_position_and_size(cam_x, cam_y, WINWIDTH, WINHEIGHT)

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

        # Collision debugging
        # pygame.draw.rect(SCREEN, (0, 0, 0), (p.x, p.y, p.width, p.height))
        # pygame.draw.rect(SCREEN, (0, 0, 0), (obstacleObjs[0].xPos, obstacleObjs[0].yPos, obstacleObjs[0].width, obstacleObjs[0].height))
        # pygame.draw.rect(SCREEN, (255, 0, 255), (obstacleObjs[1].xPos, obstacleObjs[1].yPos, obstacleObjs[1].width, obstacleObjs[1].height))

        obstacleChoice = random.randint(1, 4)

        if (cam_x % 100 == 0):
            if (obstacleChoice == 1):
                obstacleObjs.append(makeObstacle('Bird', BIRD_POSITION, BIRD_SIZE, BIRD_IMG_SCALE))
            elif (obstacleChoice == 2):
                obstacleObjs.append(makeObstacle('Snake', SNAKE_POSITION, SNAKE_SIZE, SNAKE_IMG_SCALE))
            elif (obstacleChoice == 3):
                obstacleObjs.append(makeObstacle('Banana peel', BANANA_PEEL_POSITION, BANANA_PEEL_SIZE, BANANA_IMG_SCALE))
            else:
                obstacleObjs.append(makeObstacle('Spider', SPIDER_POSITION, SPIDER_SIZE, SPIDER_IMG_SCALE))
                        
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
            # Collision boundary drawing (for debug)
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
            # elif isinstance(obstacleObjs[i], AI.spikes):
                # obstacleObjs[i].spikeBump(p)
                # SCREEN.blit(obstacleObjs[i].image, obstacleObjs[i].get_rect())
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
            # Checking if the object represents the mud
            elif isinstance(obstacleObjs[i], AI.mud):
                obstacleObjs[i].setFrameRate(MUD_FRAME_RATE)
                if (obstacleObjs[i].doMudAction(MUD_FRAME_RATE)):
                    SCREEN.blit(mudAnimation[0], obstacleObjs[i].get_rect())
                else:
                    SCREEN.blit(mudAnimation[1], obstacleObjs[i].get_rect())
            # Default for drawing any other obstacles
            elif isinstance(obstacleObjs[i], AI.tidalWave):
                SCREEN.blit(obstacleObjs[i].image, obstacleObjs[i].get_rect())        

        cam_x += CAM_X_INCREMENT        
        frame_count += 1

        pygame.display.update()
        FPSCLOCK.tick()

def startScreen():
    # Position the title image.
    titleRect = IMAGESDICT['title'].get_rect()
    topCoord = 50 # topCoord track where to position the top of the text
    titleRect.top = topCoord
    titleRect.centerx = HALF_WINWIDTH
    topCoord += titleRect.height
    
    pygame.mixer.init()

    pygame.mixer.music.load('Sounds/Menu.mp3')



    # Star with drawing a black color to the entire window
    SCREEN.fill(BGCOLOR)

    #Draw the title image to the window:
    SCREEN.blit(IMAGESDICT['title'], (0,0))

    menu = MENU.Menu()#necessary
    menu.set_colors((255,255,255), (0,0,255), (0,255,255))#optional
    menu.set_fontsize(40)#optional
    #menu.set_font('data/couree.fon')#optional
    #menu.move_menu(0, 0)#optional, moves the list of choices BY (x,y)
    menu.init(['Level 1','Level 2','Quit'], SCREEN)#necessary
    #menu.move_menu(0, 0)#optional, moves the choice list TO (x,y)
    menu.draw()#necessary

    pygame.key.set_repeat(199,69)#(delay,interval)
    pygame.display.update()
    pygame.mixer.music.play(0)
    #sound.play()
    while 1:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    menu.draw(-1) #here is the Menu class function
                if event.key == K_DOWN:
                    menu.draw(1) #here is the Menu class function
                if event.key == K_RETURN:
                    if menu.get_position() == 0:#here is the Menu class function
                        return 0;
                    elif menu.get_position() == 1:#here is the Menu class function
                        return 1;
                    elif menu.get_position() == 2:#here is the Menu class function
                        pygame.display.quit()
                        sys.exit()
                if event.key == K_ESCAPE:
                    pygame.display.quit()
                    sys.exit()
                pygame.display.update()
            elif event.type == QUIT:
                pygame.display.quit()
                sys.exit()
        pygame.time.wait(8)


def check_game_end(player, step_x, step_y, coll_layer):
    isColliding = False
    # find the tile location of the player
    tile_x_left = int((player.get_rect().left) // coll_layer.tilewidth)
    tile_x_right = int((player.get_rect().right) // coll_layer.tilewidth)
    tile_y_bottom = int((player.get_rect().bottom) // coll_layer.tileheight)
    tile_y_top = int((player.get_rect().top) // coll_layer.tileheight)

    # Create local player rect to work with
    rect = player.get_rect()
    # find the tiles around the hero and extract their rects for collision
    tile_rects = []
    for tile_x in (tile_x_left,tile_x_right):
        for tile_y in (tile_y_top, tile_y_bottom):
            for diry in (-1,0, 1):
                for dirx in (-1,0,1):
                    if coll_layer.content2D[tile_y + diry][tile_x + dirx] is not None:
                        tile_rects.append(coll_layer.content2D[tile_y + diry][tile_x + dirx].rect)
                    if coll_layer.content2D[tile_y + diry][tile_x + dirx] is not None:
                        tile_rects.append(coll_layer.content2D[tile_y+ diry][tile_x + dirx].rect)

    step_x  = special_round(step_x)
    if step_x != 0 and rect.move(step_x, 0).collidelist(tile_rects) > -1:
        isColliding = True

    # reset player rect
    rect = player.get_rect()
    # y direction, floor or ceil depending on the sign of the step
    step_y = special_round(step_y)

    # detect a collision and dont move in y direction if colliding
    if step_y != 0 and rect.move(0, step_y).collidelist(tile_rects) > -1:
        isColliding = True

    # return the step the hero should do
    return isColliding

def check_collision(player,step_x,step_y,coll_layer):
    # find the tile location of the player
    tile_x_left = int((player.get_rect().left) // coll_layer.tilewidth)
    tile_x_right = int((player.get_rect().right) // coll_layer.tilewidth)
    tile_y_bottom = int((player.get_rect().bottom) // coll_layer.tileheight)
    tile_y_top = int((player.get_rect().top) // coll_layer.tileheight)

    # Create local player rect to work with
    rect = player.get_rect()
    # find the tiles around the hero and extract their rects for collision
    tile_rects = []
    for tile_x in (tile_x_left,tile_x_right):
        for tile_y in (tile_y_top, tile_y_bottom):
            for diry in (-1,0, 1):
                for dirx in (-1,0,1):
                    if coll_layer.content2D[tile_y + diry][tile_x + dirx] is not None:
                        tile_rects.append(coll_layer.content2D[tile_y + diry][tile_x + dirx].rect)
                    if coll_layer.content2D[tile_y + diry][tile_x + dirx] is not None:
                        tile_rects.append(coll_layer.content2D[tile_y+ diry][tile_x + dirx].rect)

    # save the original steps and return them if not canceled
    res_step_x = step_x
    res_step_y = step_y

    step_x  = special_round(step_x)
    if step_x != 0 and rect.move(step_x, 0).collidelist(tile_rects) > -1:
        res_step_x = 0
    elif step_x == 0 and rect.move(0, 0).collidelist(tile_rects) > -1:
        res_step_x = -10
    elif step_x == 0 and rect.move(0, 0).collidelist(tile_rects) > -1:
        res_step_x = 10

    # reset player rect
    rect = player.get_rect()
    # y direction, floor or ceil depending on the sign of the step
    step_y = special_round(step_y)

    # detect a collision and dont move in y direction if colliding
    if step_y != 0 and rect.move(0, step_y).collidelist(tile_rects) > -1:
        if player.isJumping():
            player.jumping = False;
        elif step_y > 0:
            player.change_sprite(IMAGESDICT['player'])
            player.onGround = True;
        else:
            print 'Collision detected, not ground, not jumping'
        res_step_y = 0
    elif rect.move(0, 0).collidelist(tile_rects) > -1:
        # Force the player to move up if stuck in an object
        res_step_y = -15

    # return the step the hero should do
    return res_step_x, res_step_y

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

import random, copy, os, pygame, sys, tiledtmxloader
from pygame.locals import *

DEGREES_IN_CIRCLE = 360

class Obstacle:
    '''
        In order to initialize the AI object you must give in the
        position the AI will start in, size of the AI's image,
        the image that represents the AI, and the damage that
        the obstacle is capable of dealing.

        Both the size and pos paramaters must be ordered pairs (tuples). 
        e.g. (0,0), (50,50), etc
    '''	    	
	
    def __init__(self,pos,size,image):
        self.image = image
        self.facing = 'right'

        self.xPos = pos[0]
        self.yPos = pos[1]
        self.width = size[0]
        self.height = size[1]        
		
    # We obtain collision boundaries with this method
    def get_rect(self):
        return pygame.Rect((self.xPos, self.yPos, self.width, self.height))

    def set_rect(self, rect):
        self.xPos = rect[0]
        self.yPos = rect[1]
        self.width = rect[2]
        self.height = rect[3]

    def getPosition(self):        
        return (int(self.xPos), int(self.yPos))

    def get_sprite(self):
        return tiledtmxloader.helperspygame.SpriteLayer.Sprite(self.image, self.get_rect())

    # Is the obstacle touching a particular object?
    def isTouching(self, x, y, endYRange):
        '''
            Here, we are fundamentally checking to see
            whether or not the obstacle is in a certain
            rectangular boundary (x, y, width, height) of
            the target object.
        '''
        '''
            The first check checks whether or not the object
            is within the horizontal boundaries of the obstacle itself.
        '''    
        if (int(x) in range(int(self.xPos), int(self.xPos + self.width))):
            '''
                Here, we check for whether or not the object's bottom is at
                the same level as (or below) the obstacle's top y coordinate.
            '''    
            if (int(endYRange) >= int(self.yPos)):
                return True        
        return False

# Stationary obstacles
class stationaryObstacle(Obstacle):
    
    def __init__(self,pos,size,image):
        return Obstacle.__init__(self, pos, size, image)

class spikes(stationaryObstacle):

    def __init__(self,pos,size,image):
        self.collidedHit = False
        return stationaryObstacle.__init__(self, pos, size, image)

    def spikeBump(self, obj):
        '''
            We want to ensure that the first time the obstacle is hit
            by another object, it emits a "clang" sound. But after that,
            we want it so that as long as the object is touching the spikes,
            the spikes make no sound.
        '''
        if self.isTouching(obj.x + obj.width, obj.y, obj.y + obj.height) or self.isTouching(obj.x, obj.y, obj.y + obj.height):                        
            if (not self.collidedHit):                
                soundObj = pygame.mixer.Sound('Sounds/Spikes.wav')
                soundObj.play()
                self.collidedHit = True
        else:
            if (self.collidedHit):            
                self.collidedHit = False

# It's a log.
class treeLog(stationaryObstacle):

    def __init__(self,pos,size,image):
        return stationaryObstacle.__init__(self, pos, size, image)

    def collidedHardWith(self, obj):        
        if (self.isTouching(obj.x + obj.width, obj.y, obj.y + obj.height)):
            '''
                This checks that the most front position
                of the object is less than or equal to the
                x position of the log (indicating a
                collision at the left side.)

                * This works - it has been tested
            '''    
            if (int(obj.x + obj.width) <= int(self.xPos + (self.width/10))):                
                return True
        return False

# Obstacles that are set into motion when triggered
class triggeredObstacle(Obstacle):

    def __init__(self,pos,size,image):
        self.triggerDelay = 0
        self.timeToChangeFrame = 0
        self.timeSinceLastFrame = 0
        self.haveSetFrameRate = True
        self.animateToSecondFrame = True
        return Obstacle.__init__(self, pos, size, image)

    def move(self, xIncrement, yIncrement): 
        self.xPos += xIncrement
        self.yPos += yIncrement

    def setFrameRate(self, framerate):
        # We only want to set the frame rate once
        if (self.haveSetFrameRate):
            self.timeToChangeFrame = framerate
            self.haveSetFrameRate = False    

class bananaPeel(triggeredObstacle):

    def __init__(self,pos,size,image):
        self.xSpeed = -2.5
        self.ySpeed = -2.5
        self.haveSetSpeeds = False
        self.rotation = 0
        self.slippedOn = False
        # Properties of time concerned with the last slip with this object
        self.slipTimeCounter = 0
        self.slipRiseTime = 50
        self.slipAlpha = 255        
        # Properties of gravity that dictate the banana peel's triggered movement
        self.gravityForce = 1
        self.gravityXCarry = -1
        return triggeredObstacle.__init__(self, pos, size, image)

    def setHoriAndVertRiseSpeeds(self, hori, vert):
        if (not self.haveSetSpeeds):
            self.xSpeed = hori
            self.ySpeed = vert
            self.haveSetSpeeds = True        

    '''
        The banana peel will rotate as it is reaching its peak height (to
        create the effect that it's been slipped on.
    '''    

    # Returns the value for the fade-out of the banana peel
    def doFadeOutBananaPeel(self, alphaDecrement):        
        if self.slipAlpha > 0 and self.slipTimeCounter >= self.slipRiseTime:
            self.slipAlpha += alphaDecrement
        return self.getBananaPeelFadeAmount()

    def getBananaPeelFadeAmount(self):
        return self.slipAlpha
 
    '''
        When an object (like you for example) slips on a banana peel,
        the banana peel will fly a certain direction (defualt right now
        is backwards), and rotate 90 degrees while it's reaching its max
        height. Then, it will maintain its rotation once it has reached
        that height, and simply be under the influence of gravity.
    '''
    def slipRotate(self, gameFloor, rotateIncrementInit, rotateIncrementFall):
        if (self.slipTimeCounter < self.slipRiseTime and self.slippedOn):
            self.rotation += rotateIncrementInit
            return (self.rotation)
        else:
            # Did we already hit the floor?
            if (self.yPos >= gameFloor):
                self.rotation = 0
            else:            
                self.rotation += rotateIncrementFall                
            return (self.rotation)

    def doBananaPeelGravity(self, obj, floor, downAccel):
        if self.yPos < floor:
            self.move(self.gravityXCarry, 0)
            # Settings on the gravity, so we have acceleration
            self.gravityForce += (self.gravityForce * downAccel)
            self.move(0, self.gravityForce)

    def doBananaPeelAction(self, obj, gameFloor, gravAccel, counterIncrement, winWidth):        
        # The first time the body actually slips on the banana peel
        if (self.isTouching(obj.x, obj.y, obj.y + obj.height) and self.slippedOn == False):
            self.slippedOn = True

        if (self.slippedOn and self.slipTimeCounter < self.slipRiseTime):            
            self.slipTimeCounter += counterIncrement            
            self.move(self.xSpeed, self.ySpeed)
        else:
            # The point where the banana peel reaches its maximum height
            if (self.slipTimeCounter >= self.slipRiseTime):                
                self.doBananaPeelGravity(obj, gameFloor, gravAccel)                
                if (self.yPos >= gameFloor):
                    self.slippedOn = False
                    self.slipTimeCounter = 0
                    self.gravityForce = 1

class mud(triggeredObstacle):

    def __init__(self, pos, size, image):        
        return triggeredObstacle.__init__(self, pos, size, image)

    def animateToSecond(self):
        if (self.timeSinceLastFrame == self.timeToChangeFrame):
            self.timeSinceLastFrame = 0
            self.animateToSecondFrame = (not self.animateToSecondFrame)            
        else:
            self.timeSinceLastFrame += 1

        return self.animateToSecondFrame
    
    def doMudAction(self, speed):                
        return self.animateToSecond()
    
class coconut(triggeredObstacle):

    def __init__(self, pos, size, image):
        return triggeredObstacle.__init__(self, pos, size, image)

class sandCastle(triggeredObstacle):

    def __init__(self, pos, size, image):
        return triggeredObstacle.__init__(self, pos, size, image)

# Obstacles capable of moving on their own
class movingObstacle(Obstacle):

    def __init__(self,pos,size,image):
        self.speed = 0
        return Obstacle.__init__(self, pos, size, image)

    # Accepts a surface image to flip. "hori" and "vert" are booleans.
    def reflectOff(self, display, image, hori, vert):
        pygame.transform.flip(image, hori, vert)

    def move(self, xIncrement, yIncrement): 
        self.xPos += xIncrement
        self.yPos += yIncrement

    def setSpeed(self, speedAmount):
        self.speed = speedAmount


class giantRock(movingObstacle):        
    
    def __init__(self,pos,size,image,moveMode):
        self.giantRockMoveMode = moveMode        
        self.gravityForce = 1
        self.rotation = 0    
        self.timeToChangeFrame = 20
        self.timeSinceLastFrame = 1
        self.frameNumber = 0
        return movingObstacle.__init__(self, pos, size, image)    

    '''
        Rotate the soccer ball every certain amount of degree specified,
        depending on what direction the soccer ball is currently moving.
    '''    
    def giantRockRotate(self, rotateIncrement):        
        if self.giantRockMoveMode == 'left':            
            self.rotation += rotateIncrement            
            if self.rotation >= DEGREES_IN_CIRCLE:
                self.rotation = 0
        elif self.giantRockMoveMode == 'right':            
            self.rotation -= rotateIncrement
            if self.rotation <= -DEGREES_IN_CIRCLE:
                self.rotation = 0
        return self.rotation

    def animateToNext(self, sectionOfTime, timeToChangeFrame):        
        if (self.timeSinceLastFrame % sectionOfTime == 0):            
            self.frameNumber = (self.timeSinceLastFrame / sectionOfTime - 1)
            if (self.timeSinceLastFrame >= timeToChangeFrame):                
                self.timeSinceLastFrame = 1                
            else:
                self.timeSinceLastFrame += 1            
        else:
            self.timeSinceLastFrame += 1
        return self.frameNumber

    def doGiantRockPhysics(self, obj, floor, downAccel):
        if self.yPos < floor:
            self.move(0, self.speed)
            # Settings on the gravity, so we have acceleration.
            self.gravityForce += (self.gravityForce * downAccel)
            self.move(0, self.gravityForce)
        else:
            self.gravityForce = 1

    def doGiantRockAction(self, obj, gameFloor, gravAccel, winWidth):        
       
        # Soccer ball physics includes the gravity aspect of the ball.
        self.doGiantRockPhysics(obj, gameFloor, gravAccel)

        # Testing for when to switch direction of the ball.
        if self.xPos <= 0:
            self.giantRockMoveMode = 'right'
        elif self.giantRockMoveMode == 'left' and self.isTouching(obj.x + obj.width, obj.y, obj.y + obj.height):
            self.giantRockMoveMode = 'right'
        elif self.xPos >= winWidth:
            self.giantRockMoveMode = 'left'
        elif self.giantRockMoveMode == 'right' and self.isTouching(obj.x, obj.y, obj.y + obj.height):
            self.giantRockMoveMode = 'left'

        # Move the soccer ball in accordance to the current direction it has on now.
        if self.giantRockMoveMode == 'right':            
            self.move(self.speed, 0)
        elif self.giantRockMoveMode == 'left':
            self.move(-self.speed, 0)

class tidalWave(movingObstacle):
    
    def __init__(self,pos,size,image):
        return movingObstacle.__init__(self, pos, size, image)
'''
    It is convenient to define an animal sub-class for the class of
    moving obstacles, since animals are usually animated.
'''
class animal(movingObstacle):
    def __init__(self,pos,size,image):
        self.timeToChangeFrame = 0
        self.timeSinceLastFrame = 0
        self.haveSetFrameRate = True        
        return movingObstacle.__init__(self, pos, size, image)

    def setFrameRate(self, framerate):
        # We only want to set the frame rate once
        if (self.haveSetFrameRate):
            self.timeToChangeFrame = framerate
            self.haveSetFrameRate = False

class bird(animal):

    def __init__(self,pos,size,image):        
        self.animateToSecondFrame = True
        return animal.__init__(self, pos, size, image)

    def animateToSecond(self):
        if (self.timeSinceLastFrame == self.timeToChangeFrame):
            self.timeSinceLastFrame = 0
            self.animateToSecondFrame = (not self.animateToSecondFrame)            
        else:
            self.timeSinceLastFrame += 1

        return self.animateToSecondFrame

    def doBirdAction(self, speed):        
        self.move(-speed, 0)
        return self.animateToSecond()

class crocodile(animal):

    def __init__(self,pos,size,image):        
        return movingObstacle.__init__(self, pos, size, image)

class spider(animal):

    def __init__(self,pos,size,image):
        self.animateToSecondFrame = True
        self.webStringX = pos[0] + (size[0]/2)
        self.webStringY = pos[1] - 50
        self.webStringWidth = 2
        self.webStringHeight = 50
        return animal.__init__(self, pos, size, image)

    def animateToSecond(self):
        if (self.timeSinceLastFrame == self.timeToChangeFrame):
            self.timeSinceLastFrame = 0
            self.animateToSecondFrame = (not self.animateToSecondFrame)            
        else:
            self.timeSinceLastFrame += 1

        return self.animateToSecondFrame

    def setWebStringRect(self, x, y, width, height):
        self.webStringX = x
        self.webStringY = y
        self.webStringWidth = width
        self.webStringHeight = height

    def getWebStringRect(self):
        return (self.webStringX, self.webStringY, self.webStringWidth, self.webStringHeight)
    
    def doSpiderAction(self, speed):                
        return self.animateToSecond()

class snake(animal):

    def __init__(self,pos,size,image):
        self.animateToSecondFrame = True
        return animal.__init__(self, pos, size, image)    
    
    def animateToSecond(self):
        if (self.timeSinceLastFrame == self.timeToChangeFrame):
            self.timeSinceLastFrame = 0
            self.animateToSecondFrame = (not self.animateToSecondFrame)            
        else:
            self.timeSinceLastFrame += 1

        return self.animateToSecondFrame

    def doSnakeAction(self, speed):        
        self.move(-speed, 0)
        return self.animateToSecond()
        
    

            

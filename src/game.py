
import pygame
from pygame.locals import *

import random
import math
import time

from Vect2d import Vect2d 

# TODO: add game over on collision

SCREEN_TILE_SIZE = Vect2d(11, 11)
BOARD_TILE_SIZE = SCREEN_TILE_SIZE - Vect2d(2, 2)
TILE_PIXEL_SIZE = Vect2d(64, 64)

SCREEN_PIXEL_SIZE = SCREEN_TILE_SIZE * TILE_PIXEL_SIZE
BOARD_PIXEL_SIZE = BOARD_TILE_SIZE * TILE_PIXEL_SIZE

ZERO_TUPLE = (0, 0)

TICKS_PER_SECOND = 4

BACKGROUND_COLOR = (65, 65, 255)

class Direction: 
    def __init__(self, vect2d, angle):
        self.vect2d = vect2d
        self.angle = angle

DIRECTION_UP = Direction(Vect2d(0, -1), 0)
DIRECTION_LEFT = Direction(Vect2d(-1, 0), 90)
DIRECTION_DOWN = Direction(Vect2d(0, 1), 180)
DIRECTION_RIGHT = Direction(Vect2d(1, 0), 270)

KEY_DIRECTION_MAP = {
    pygame.locals.K_UP: DIRECTION_UP,
    pygame.locals.K_RIGHT: DIRECTION_RIGHT,
    pygame.locals.K_DOWN: DIRECTION_DOWN,
    pygame.locals.K_LEFT: DIRECTION_LEFT
}
DIRECTION_OPPISITES = {
    DIRECTION_UP: DIRECTION_DOWN,
    DIRECTION_DOWN: DIRECTION_UP,
    DIRECTION_LEFT: DIRECTION_RIGHT,
    DIRECTION_RIGHT: DIRECTION_LEFT
}

def extractSprites(spritesheet, tile_pixel_size):
    def extractSprite(sprite_pos): 
        pixel_pos = sprite_pos * tile_pixel_size
        rect = pygame.Rect(pixel_pos.to_tuple() + tile_pixel_size.to_tuple())
        sprite = pygame.Surface(rect.size, pygame.SRCALPHA)
        sprite.blit(spritesheet, ZERO_TUPLE, rect)
        return sprite

    sprite_positions = Vect2d.from_tuple(spritesheet.get_size()) / tile_pixel_size
    return sprite_positions.interate(lambda sprite_pos : extractSprite(sprite_pos))

def draw(surface, position, sprite): 
    pixel_pos = position * TILE_PIXEL_SIZE
    surface.blit(sprite, pixel_pos.to_tuple())

spritesheet = pygame.image.load("assets/snake_spritesheet.png")

HEAD_SPRITE, BODY_0_SPRITE, BODY_1_SPRITE, BODY_2_SPRITE, \
END_SPRITE, TARGET_SPRITE, BORDER_SPRITE, DEBUG_ARROW = extractSprites(spritesheet, TILE_PIXEL_SIZE)

bodySprites = [BODY_0_SPRITE, BODY_1_SPRITE, BODY_2_SPRITE]

class SnakeSegment: 
    def __init__(self, position, direction, openPosMap, isStart):
        self.position = position
        self.direction = direction
        self.next = None
        self.sprite = HEAD_SPRITE if isStart else END_SPRITE
        self.openPosMap = openPosMap
        
        openPosMap[position.serialize()] = False

    def traverse(self, callback):
        callback(self)
        if self.next is not None:
            self.next.traverse(callback)
    
    def draw(self, surface):
        rotatedSprite = pygame.transform.rotate(self.sprite, self.direction.angle)
        draw(surface, self.position, rotatedSprite)
       
    def growMove(self, inputDirection):
        self.direction = inputDirection
        nextPosition = self.direction.vect2d + self.position
        self._growMove(nextPosition, self.direction)

        self.openPosMap[nextPosition.serialize()] = False

    def _growMove(self, position, direction):
        if self.next is not None:
            self.next._growMove(self.position, self.direction)
        else:
            if self.sprite is not HEAD_SPRITE:
                self.sprite = random.choice(bodySprites)
            self.next = SnakeSegment(self.position, self.direction, self.openPosMap, False)
            
        self.position = position
        self.direction = direction

    def move(self, inputDirection):
        self.direction = inputDirection
        nextPosition = inputDirection.vect2d + self.position
        self._move(nextPosition, inputDirection)

        self.openPosMap[nextPosition.serialize()] = False

    def _move(self, position, direction):
        if self.next is not None:
            self.next._move(self.position, self.direction)
        else: 
            self.openPosMap[self.position.serialize()] = True
        
        self.direction = direction
        self.position = position


class Game: 
    def __init__(self):
        self._openPosMap = None
        self._snake = None
        self._targetPosition = None
        self._inputDirection = None

    def new(self, snakePosition, snakeDirection):
        self._openPosMap = { 
            vect2d.serialize(): True for vect2d in BOARD_TILE_SIZE.interate() 
        }
        self._snake = SnakeSegment(snakePosition, snakeDirection, self._openPosMap, True)
        self._inputDirection = snakeDirection

        self._snake.growMove(DIRECTION_RIGHT)
        self._createTarget()
    
    def _createTarget(self):
        openPosKeys = [value[0] for value in filter(
            lambda item: item[1], self._openPosMap.items()
        )]
        randomPosKey = random.choice(openPosKeys)
        self._targetPosition = Vect2d.deserialize(randomPosKey)

    def handleDirectionInput(self, inputDirection):
        # prevent recording oppisite direction input
        if DIRECTION_OPPISITES[self._snake.direction] is not inputDirection:
            self._inputDirection = inputDirection

    def tick(self):
        nextPosition = self._snake.position + self._inputDirection.vect2d
        nextPositionKey = nextPosition.serialize()
        if(
            nextPositionKey not in self._openPosMap
            or not self._openPosMap[nextPositionKey]
        ):
            pass
        elif nextPosition == self._targetPosition:
            self._snake.growMove(self._inputDirection)
            self._createTarget()
        else:
            self._snake.move(self._inputDirection)

    def draw(self, surface):
        self._snake.traverse(lambda segment: segment.draw(surface))
        draw(surface, self._targetPosition, TARGET_SPRITE)


# init pygame
pygame.init()

# draw border
screen = pygame.display.set_mode(SCREEN_PIXEL_SIZE.to_tuple())
screen.fill(BACKGROUND_COLOR)

SCREEN_TILE_SIZE.interate(lambda pos: draw(screen, pos, BORDER_SPRITE))

boardRect = pygame.Rect(ZERO_TUPLE + BOARD_PIXEL_SIZE.to_tuple())
boardSurface = pygame.Surface(boardRect.size)

game = Game()
game.new(Vect2d(0, 0), DIRECTION_RIGHT)

# game loop
lastFrameTime = 0

running = True
while running:
    currentTime = time.time()
    deltaTime = currentTime - lastFrameTime
    sleepTime = (1. / TICKS_PER_SECOND) - deltaTime

    if sleepTime > 0:
        time.sleep(sleepTime)
    else:
        lastFrameTime = currentTime

        # handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key in KEY_DIRECTION_MAP:
                game.handleDirectionInput(KEY_DIRECTION_MAP[event.key])

        #game logic
        game.tick()
        
        # draw 
        boardSurface.fill(BACKGROUND_COLOR)
        game.draw(boardSurface)
        screen.blit(boardSurface, TILE_PIXEL_SIZE.to_tuple())
        pygame.display.flip()
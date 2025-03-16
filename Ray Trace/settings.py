import pygame, sys, math, json, csv
from os.path import join
from pygame import gfxdraw

# Screen dimensions
WIDTH, HEIGHT = 1024, 768

# Frames per second (controls the game speed)
FPS = 60

# Create the display window
DISPLAY = pygame.display.set_mode((WIDTH, HEIGHT))

# Size of each grid tile
TILE_SIZE = 64

# Calculate how many tiles fit into the screen (in terms of width and height)
GRID_WIDTH, GRID_HEIGHT = WIDTH // TILE_SIZE, HEIGHT // TILE_SIZE

class Tile():
    def __init__(self, image, x,y):
        self.image = pygame.image.load(join('assets', 'tiles', f'{image}')).convert_alpha()
        self.rect = self.image.get_frect(center = (x,y))
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.pos = self.rect.center
    
    def draw(self):
        DISPLAY.blit(self.image, self.pos)

# Load Tilemap
with open(join('assets', 'tilemap.csv')) as file:
    TILE_MAP = list(csv.reader(file))

TILES = []

TILES.extend(
    Tile('Grass0 - 0.png', x * TILE_SIZE, y * TILE_SIZE)
    for y, tiles in enumerate(TILE_MAP)
    for x, tile in enumerate(tiles)
)

TILES.extend(
    Tile('Tree - 0.png', x * TILE_SIZE, y * TILE_SIZE)
    for y, tiles in enumerate(TILE_MAP)
    for x, tile in enumerate(tiles)
    if int(tile) == 2
)



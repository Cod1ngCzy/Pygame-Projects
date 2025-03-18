import pygame, sys, math, json, csv, os
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

class Tile:
    def __init__(self, image, x, y, size=None, tile_number=None):
        if size is None:
            size = TILE_SIZE
            
        # Load and scale the tile image
        self.image = pygame.image.load(join('assets', 'tiles', 'grass', f'{image}')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (size, size))
        
        # Create a rect for the tile and center it at (x, y)
        self.rect = self.image.get_frect(center=(x, y))
        self.tile_number = tile_number
    
    def draw(self):
        DISPLAY.blit(self.image, self.rect)

# RESET TILE
"""
TILE_MAP = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
with open(join('assets', 'tilemap.csv'), 'w', newline='') as file:
    writer = csv.writer(file)
    for row in TILE_MAP:
        writer.writerow(row)
""" # If Tile Map Needs Ovveride

# Load Tilemap
with open(join('assets', 'tilemap.csv')) as file:
    TILE_MAP = list(csv.reader(file))

TILES = []
SPRITES = []
sprites_dir = join('assets', 'sprites','player')
for sprite_file in sorted(os.listdir(sprites_dir)):
    if sprite_file.endswith('.png'):
        sprite_img = pygame.image.load(join(sprites_dir, sprite_file)).convert_alpha()
        SPRITES.append(sprite_img)

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




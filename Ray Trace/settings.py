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
        self.rect = self.image.get_frect(topleft=(x, y))
        self.tile_number = tile_number
    
    def draw(self, pos=None):
        if pos is None:
            pos = self.rect
        DISPLAY.blit(self.image, pos)

def get_image(file_path, current_tile_num=0):
    file_names = [file for file in os.listdir(file_path)]
    tile_num = current_tile_num
    image_data = {}
    image_tiles = []

    for image in file_names:
        tile_num += 1
        image_data[tile_num] = image

    # Default Image Tile
    image_data[0] = 'Grass0 - 0.png'

    for y, tiles in enumerate(TILE_MAP):
        for x, tile in enumerate(tiles):
            tile_num = int(tile)

            image = image_data.get(tile_num, image_data[0])

            image_tiles.append(Tile(image, x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE))
    
    return image_tiles


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


SPRITES = []
FILE_PATH = 'assets/tiles/grass'
TILES = get_image(FILE_PATH)

sprites_dir = join('assets', 'sprites','player')
for sprite_file in sorted(os.listdir(sprites_dir)):
    if sprite_file.endswith('.png'):
        sprite_img = pygame.image.load(join(sprites_dir, sprite_file)).convert_alpha()
        SPRITES.append(sprite_img)


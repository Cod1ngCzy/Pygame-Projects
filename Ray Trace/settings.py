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
    def __init__(self, image_file_path, x, y, size=None, tile_number=None, display=None):
        if size is None:
            size = TILE_SIZE
            
        # Load and scale the tile image
        self.image = pygame.image.load(image_file_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (size, size))
        self.display = display
        
        # Create a rect for the tile and center it at (x, y)
        self.rect = self.image.get_frect(topleft=(x, y))
        self.tile_number = tile_number
    
    def draw(self, pos=None):
        if pos is None:
            pos = self.rect
        
        if self.display  is None:
            self.display  = DISPLAY
            
        self.display.blit(self.image, pos)

class TileMap:
    def __init__(self, file_path_csv=None, file_path=None):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Passed Argument Assumes a STRUCTURED folder. \nExample: \n📂 assets\n└── 📂 tiles")
        
        if not os.path.exists(file_path_csv):
            raise FileNotFoundError(f"{file_path_csv} is not found. \n Passed Argument Assumes an ASSETS folder. \nExample: \n.\ 📂 assets ")
        
        self.tile_map = self.load_from_csv(file_path_csv)
        self.file_path = file_path
        self.folder_directories = [join(file_path, folder_dir) for folder_dir in sorted(os.listdir(file_path)) if os.path.isdir(join(file_path, folder_dir))]
        self.image_data = {} 
        self.image = {}
        for directory in self.folder_directories:
            folder_name = os.path.basename(directory)
            self.image[folder_name] = list(map(lambda image: join(directory, image), os.listdir(directory)))
        
        tile_num = 0
        for folder in self.folder_directories:
            folder = os.path.basename(folder)
            for image in self.image[folder]:  # folder becomes the key
                tile_num += 1
                self.image_data[tile_num] = image
        
        self.tiles = self.load_image_object()

    def load_from_csv(self, file_path=str):    
        map = []
        with open(file_path) as file:
            tile = csv.reader(file, delimiter=',')
            for row in tile:
                map.append(list(row))
        return map

    def load_image_object(self):
        image_objects = []
        for y, tiles in enumerate(self.tile_map):
            for x, tile in enumerate(tiles):
                tile_num = int(tile)

                image = self.image_data.get(tile_num)

                image_objects.append(Tile(image, x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE))
        
        return image_objects

    def load_map(self):
        for tile in self.tiles:
            tile.draw()

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
FILE_PATH_T0_CSV = 'assets/tilemap.csv'
FILE_PATH = 'assets/tiles'
TILES = TileMap(FILE_PATH_T0_CSV, FILE_PATH)

sprites_dir = join('assets', 'sprites','player')
for sprite_file in sorted(os.listdir(sprites_dir)):
    if sprite_file.endswith('.png'):
        sprite_img = pygame.image.load(join(sprites_dir, sprite_file)).convert_alpha()
        SPRITES.append(sprite_img)


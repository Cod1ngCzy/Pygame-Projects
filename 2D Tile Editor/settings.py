import pygame, sys, math, json, csv, os
from os.path import join

class Tile:
    def __init__(self, image_file_path, x, y, size=None, tile_number=None, display=None):
        # Load the tile image
        self.image = pygame.image.load(image_file_path).convert_alpha()
        
        # Use the provided size or default to 64
        self.size = size if size is not None else 64
        
        # Scale the image once during initialization
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.display = display
        
        # Create a rect for the tile and center it at (x, y)
        self.rect = self.image.get_frect(topleft=(x, y))
        self.tile_number = tile_number
        self.is_collision = False
        self.image_name = os.path.basename(image_file_path)

    def draw(self, pos=None, display=None):
        if pos is None:
            pos = self.rect
        
        if display == None:
            display = pygame.Surface((0,0))
            
        # No need to rescale every time - only blit the image
        display.blit(self.image, pos)
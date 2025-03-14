import pygame, sys, math, json
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
GRID_WIDTH, GRID_HEIGHT = WIDTH / TILE_SIZE, HEIGHT / TILE_SIZE

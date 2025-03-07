import pygame, sys, math, json
from os.path import join
from pygame import gfxdraw

WIDTH, HEIGHT = 1024,768
FPS = 60
DISPLAY = pygame.display.set_mode((WIDTH, HEIGHT))
TILE_SIZE = 30
GRID_WIDTH, GRID_HEIGHT =  WIDTH / TILE_SIZE, HEIGHT / TILE_SIZE

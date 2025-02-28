import pygame, sys
from os.path import join

# Game Color (R,G,B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHTGREY = (100,100,100)

# ==============================
# SCREEN SIZE & TILE FIT CHART
# ==============================
# Use this chart to select the best TILESIZE
# that fits perfectly in common screen widths.

# Screen Width × Height | 16px Tiles | 32px Tiles | 64px Tiles
# -------------------------------------------------------------
#  800  ×  600         |  50 × 37   |  25 × 18   |  12 × 9   
# 1024  ×  768         |  64 × 48   |  32 × 24   |  16 × 12  
# 1280  ×  720         |  80 × 45   |  40 × 22   | ❌ (Doesn’t fit evenly)
# 1280  ×  960         |  80 × 60   |  40 × 30   |  20 × 15  
# 1366  ×  768         | ❌ (No fit) |  42 × 24   | ❌ (No fit)
# 1440  ×  900         |  90 × 56   |  45 × 28   |  22 × 14  
# 1600  ×  900         | 100 × 56   |  50 × 28   |  25 × 14  
# 1920  × 1080         | 120 × 67   |  60 × 33   |  30 × 16  
# 2560  × 1440         | 160 × 90   |  80 × 45   |  40 × 22  
# -------------------------------------------------------------
# ✅ = Fits perfectly | ❌ = Doesn’t fit evenly (may cause gaps)
# To avoid black borders, choose a TILESIZE that evenly divides
# both WIDTH and HEIGHT.

# Game Settings
HEIGHT = 768 
WIDTH = 1024 
FPS = 60
TILE_SIZE = 64
GRID_WIDTH = WIDTH / TILE_SIZE
GRID_HEIGHT = HEIGHT / TILE_SIZE



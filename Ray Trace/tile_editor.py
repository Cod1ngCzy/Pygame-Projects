from settings import *

pygame.init()
display = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('Tile Editor')

running = True
clock = pygame.time.Clock()

class Tilemap():
    def __init__(self):
        self.tilemap = self.load_map()
        self.tilesize = TILE_SIZE
        self.rows = GRID_WIDTH 
        self.cols = GRID_HEIGHT
        self.tiles = []
    
    def load_tiles(self):
        for y, tiles in enumerate(self.tilemap):
            for x, tile in enumerate(tiles):
                if int(tile) == 1:
                    pygame.draw.rect(display, 'blue', (x * self.tilesize, y * self.tilesize, self.tilesize, self.tilesize))

    def load_map(self):
        map = []
        with open(join('assets', 'tilemap.csv')) as file:
            tile = csv.reader(file, delimiter=',')
            for row in tile:
                map.append(list(row))
        return map
    
    def save_map(self):
        with open(join('assets', 'tilemap.csv'), 'w', newline='') as file:
            writer = csv.writer(file)
            for row in self.tilemap:
                writer.writerow(row)
    
    def load_tiles_image(self):
        self.tiles.extend(
            Tile('Grass0 - 0.png', x * self.tilesize, y * self.tilesize)
            for y, tiles in enumerate(self.tilemap)
            for x, tile in enumerate(tiles)
            if int(tile) == 1
        )

        self.tiles.extend(
            Tile('Tree - 0.png', x * self.tilesize, y * self.tilesize)
            for y, tiles in enumerate(self.tilemap)
            for x, tile in enumerate(tiles)
            if int(tile) == 2
        )

        for tile in self.tiles:
            tile.draw()

    def show_grid(self):
        for cols in range(self.cols):
            for rows in range(self.rows):
                pygame.draw.rect(display, 'grey', (rows * self.tilesize, cols * self.tilesize, self.tilesize, self.tilesize), 1)
    
    def edit_tiles(self):
        self.load_tiles_image()

        mouse_pos = pygame.Vector2(
            min(max(pygame.mouse.get_pos()[0] // self.tilesize, 0), len(self.tilemap[0]) - 1),
            min(max(pygame.mouse.get_pos()[1] // self.tilesize, 0), len(self.tilemap) - 1)
        )

        mdx = round(mouse_pos.x)
        mdy = round(mouse_pos.y)

        if pygame.mouse.get_pressed()[0]:
            self.tilemap[mdy][mdx] = 1
        elif pygame.mouse.get_pressed()[2]:
            self.tilemap[mdy][mdx] = 0
        
tile = Tilemap()

while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                tile.save_map()
                print('Tilemap Saved')
                

    display.fill('black')

    tile.edit_tiles()

    pygame.display.update()
pygame.quit()
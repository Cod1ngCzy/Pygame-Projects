from settings import *

pygame.init()
offset = 300
display = pygame.display.set_mode((WIDTH + offset,HEIGHT))
pygame.display.set_caption('Tile Editor')

running = True
clock = pygame.time.Clock()

class Tilemap():
    def __init__(self):
        global TILES

        self.tilemap = self.load_map()
        self.tilesize = TILE_SIZE
        self.rows = GRID_WIDTH 
        self.cols = GRID_HEIGHT
        self.tiles = []

        # Load Images from folder
        self.grass_images = self.get_images('assets/tiles/grass')

        # Edit Tile Properties
        self.selected_tile = None
        self.updated_tiles = []

    def handle_tiles(self, tile_list):
        
        pass
    
    def get_images(self, file_path, current_tile_num=0):
        file_names = [file for file in os.listdir(file_path)]
        images = []
        tile_num = current_tile_num

        # Iteration Properties
        col = 0
        row = 0
        row_gap = 75
        for i, image in enumerate(file_names):
            tile_num += 1
            images.append(Tile(image, WIDTH + (row_gap * col) + 50, row_gap * row + 50, 60, tile_num))
            col += 1
            if col == 3:
                row += 1
                col = 0

        return images
    
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
        )

        self.tiles.extend(
            Tile('Road0.png', x * self.tilesize, y * self.tilesize)
            for y, tiles in enumerate(self.tilemap)
            for x, tile in enumerate(tiles)
            if int(tile) == 1
        )

        for tile in self.tiles:
            tile.draw()

    def show_grid(self, tile_pos, images):
        for cols in range(self.cols):
            for rows in range(self.rows):
                pygame.draw.rect(display, 'grey', (rows * self.tilesize, cols * self.tilesize, self.tilesize, self.tilesize), 1)
        
        add_tile, remove_tile = pygame.mouse.get_pressed()[0], pygame.mouse.get_pressed()[1]

        # Pick Tile 
        for image in images:
            image.draw()
            if image.rect.collidepoint(pygame.mouse.get_pos()) and add_tile:
                    self.selected_tile = image.tile_number
        
                # Unpack only if within bounds
        if tile_pos[0] < len(self.tilemap) and tile_pos[1] < len(self.tilemap[0]):
            x, y = tile_pos
            if add_tile and self.selected_tile:
                self.tilemap[y][x] = self.selected_tile
                self.updated_tiles.append((y, x))
        
        print(self.updated_tiles)
       
    # Main Class Loop
    def edit_tiles(self):
        mouse_pos = pygame.Vector2(
            min(max(pygame.mouse.get_pos()[0] // self.tilesize, 0), len(self.tilemap[0]) - 1),
            min(max(pygame.mouse.get_pos()[1] // self.tilesize, 0), len(self.tilemap) - 1)
        )
        mdx, mdy = round(mouse_pos.x), round(mouse_pos.y)

        self.show_grid([mdx,mdy], self.grass_images)

        
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

    tile.edit_tiles()

    pygame.display.update()
pygame.quit()
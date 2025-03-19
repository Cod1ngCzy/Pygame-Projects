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
        self.grid_init = False
        self.redraw = False
        self.load_tile = False

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
            images.append(Tile(image, WIDTH + (row_gap * col) + 50, row_gap * row + 20, 60, tile_num))
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
        pass

    def show_updated_tiles(self):
        if self.redraw:
            for x,y, num in self.updated_tiles:
                pygame.draw.rect(DISPLAY, 'blue', (x * TILE_SIZE,y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            self.redraw = False
            
        if self.load_tile:
            for x,y,num in self.updated_tiles:
                pygame.draw.rect(DISPLAY, 'black', (x * TILE_SIZE,y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                for image in self.grass_images:
                    if image.tile_number == num:
                        image.draw((x * TILE_SIZE, y * TILE_SIZE))
            self.grid_init = False
            self.show_grid(self.grass_images)
            self.updated_tiles.clear()
            self.load_tile = False
           
    def show_grid(self, images):
        # Grid Intialized Only Once
        if not self.grid_init:
            for cols in range(self.cols):
                for rows in range(self.rows):
                    pygame.draw.rect(display, 'grey', (rows * self.tilesize, cols * self.tilesize, self.tilesize, self.tilesize), 1)

            for image in images:
                image.draw()

            self.grid_init = True


    def handle_tiles(self, tile_pos, images):        
        add_tile, remove_tile = pygame.mouse.get_pressed()[0], pygame.mouse.get_pressed()[1]
        mouse_pos = pygame.mouse.get_pos()

        # First handle tile selection from palette (outside grid)
        for image in images:
            if image.rect.collidepoint(mouse_pos) and add_tile:
                self.selected_tile = image.tile_number
                return  # Return early to avoid placing a tile in the same click
        
        # Then handle tile placement (inside grid)
        if tile_pos is not None:  # Make sure we have valid coordinates
            x, y = tile_pos
            
            # Check if within bounds of the tilemap
            if 0 <= x < len(self.tilemap[0]) and 0 <= y < len(self.tilemap):
                if add_tile and self.selected_tile is not None:
                    if self.tilemap[y][x] != self.selected_tile:
                        self.updated_tiles.append((x,y,self.selected_tile))
                        self.tilemap[y][x] = self.selected_tile
                        self.redraw = True

        self.show_grid(images)
        self.show_updated_tiles()
        

    # Main Class Loop
    def edit_tiles(self):
        mouse_pos = pygame.Vector2(
            min(max(pygame.mouse.get_pos()[0] // self.tilesize, 0), len(self.tilemap[0]) - 1),
            min(max(pygame.mouse.get_pos()[1] // self.tilesize, 0), len(self.tilemap) - 1)
        )
        mdx, mdy = round(mouse_pos.x), round(mouse_pos.y)

        self.handle_tiles([mdx,mdy], self.grass_images)
       
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
            if event.key == pygame.K_l:
                tile.load_tile = True

    tile.edit_tiles()

    pygame.display.update()
pygame.quit()
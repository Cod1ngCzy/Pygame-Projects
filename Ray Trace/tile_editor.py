from settings import *

pygame.init()
offset = 300
display = pygame.display.set_mode((WIDTH + offset,HEIGHT))
pygame.display.set_caption('Tile Editor')

running = True
clock = pygame.time.Clock()

class TileEditor():
    def __init__(self, tile_size=int, tile_map=str, tile_file_path=(join('assets','tiles'))):
        # Class Variables (*Required)
        self.tile_map = self.load_from_csv(tile_map)
        self.tile_rows, self.tile_cols = (len(self.tile_map) - 1), (len(self.tile_map[0]) - 1)
        self.tile_size = tile_size
        self.rows, self.cols = GRID_WIDTH, GRID_HEIGHT
        self.tile_screen = pygame.Surface((300, HEIGHT), pygame.SRCALPHA)

        # Load Images from folder
        if not os.path.exists(tile_file_path):
            raise FileNotFoundError(f"Passed Argument Assumes a STRUCTURED folder. \nExample: \n📂 assets\n└── 📂 tiles")
        
        self.images_folder = [join(tile_file_path, folder_dir) for folder_dir in sorted(os.listdir(tile_file_path)) if os.path.isdir(join(tile_file_path, folder_dir))]
        self.images = {} # Variable containing all images object
        # Load Images into a dictionary
        for file_path in self.images_folder:
            folder_name = os.path.basename(file_path)
            self.images[folder_name] = list(filter(None, map( lambda file: self.create_image_object(join(file_path, file)), os.listdir(file_path))))
        
        # Tile Category Variables
        self.catergory_index = 0
        self.current_category = list(self.images.keys())[self.catergory_index]
        self.set_image_tilenum()

        self.tiles = []

        # Edit Tile Properties
        self.selected_tile = None
        self.updated_tiles = []
        self.grid_init = False
        self.redraw = False
        self.load_tile = False

        self.draw_image_object()


    def create_image_object(self, image_file_path, tile_size=None):
        try:
            return Tile(image_file_path, 0,0, tile_size)
        except Exception as e:
            print(f"Error loading image '{image_file_path}': {e}")
    
    def set_image_tilenum(self, prevous_list_length=0):
        if self.catergory_index >= len(self.images):
            self.catergory_index = 0
            return
        
        tile_num = prevous_list_length
        for i, image in enumerate(self.images[self.current_category]):
            tile_num += 1
            image.tile_number = tile_num
        self.catergory_index += 1
        
        return self.set_image_tilenum(tile_num + prevous_list_length)

    def draw_image_object(self):
        pygame.draw.rect(DISPLAY, 'black', (WIDTH, 0, 300, HEIGHT))

        self.current_category = list(self.images.keys())[self.catergory_index]

        # Function Properties
        row_gap = 100
        col_gap = 75
        tiles_per_row = 3
        start_x = WIDTH + 50  # Starting x position for the palette

        for i, image in enumerate(self.images[self.current_category]):
            col = i % tiles_per_row
            row = i // tiles_per_row

            # Calculate position
            x = start_x + (col_gap * col)
            y = row_gap * row + 20

            image.rect.topleft= (x,y)

            image.draw()
        
    def load_from_csv(self, file_path=str):    
        map = []
        with open(file_path) as file:
            tile = csv.reader(file, delimiter=',')
            for row in tile:
                map.append(list(row))
        return map
    
    def save_map(self):
        with open(join('assets', 'tilemap.csv'), 'w', newline='') as file:
            writer = csv.writer(file)
            for row in self.tile_map:
                writer.writerow(row)

    def show_updated_tiles(self):
        if self.redraw:
            for x,y, num in self.updated_tiles:
                pygame.draw.rect(DISPLAY, 'blue', (x * TILE_SIZE,y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            self.redraw = False
            
        if self.load_tile:
            for x,y,num in self.updated_tiles:
                pygame.draw.rect(DISPLAY, 'black', (x * TILE_SIZE,y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                for image in self.images[self.current_category]:
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
                    pygame.draw.rect(display, 'grey', (rows * self.tile_size, cols * self.tile_size, self.tile_size, self.tile_size), 1)

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
            if 0 <= x < len(self.tile_map[0]) and 0 <= y < len(self.tile_map):
                if add_tile and self.selected_tile is not None:
                    if self.tile_map[y][x] != self.selected_tile:
                        self.updated_tiles.append((x,y,self.selected_tile))
                        self.tile_map[y][x] = self.selected_tile
                        self.redraw = True

        self.show_grid(images)
        self.show_updated_tiles()
        

    # Main Class Loop
    def edit_tiles(self):
        mouse_pos = pygame.Vector2(
            min(max(pygame.mouse.get_pos()[0] // self.tile_size, 0), len(self.tile_map[0]) - 1),
            min(max(pygame.mouse.get_pos()[1] // self.tile_size, 0), len(self.tile_map) - 1)
        )
        mdx, mdy = round(mouse_pos.x), round(mouse_pos.y)

        self.handle_tiles([mdx,mdy], self.images[self.current_category])
       
tile = TileEditor(TILE_SIZE, join('assets', 'tilemap.csv'))

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
            if event.key == pygame.K_LEFTBRACKET:
                tile.catergory_index -= 1
                if tile.catergory_index <= -1:
                    tile.catergory_index = 3
                tile.draw_image_object()
            if event.key == pygame.K_RIGHTBRACKET:
                tile.catergory_index += 1
                if tile.catergory_index >= 4:
                    tile.catergory_index = 0
                tile.draw_image_object()

    tile.edit_tiles()

    pygame.display.update()
pygame.quit()
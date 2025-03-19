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
        self.tile_size = tile_size
        self.tile_screen = pygame.Surface((300, HEIGHT), pygame.SRCALPHA)

        # Load Images from folder
        if not os.path.exists(tile_file_path):
            raise FileNotFoundError(f"Passed Argument Assumes a STRUCTURED folder. \nExample: \n📂 assets\n└── 📂 tiles")
        
        self.folder_directories = [join(tile_file_path, folder_dir) for folder_dir in sorted(os.listdir(tile_file_path)) if os.path.isdir(join(tile_file_path, folder_dir))]
        self.images = {} # Variable containing all images object
        # Load Images into a dictionary
        for file_path in self.folder_directories:
            folder_name = os.path.basename(file_path)
            self.images[folder_name] = list(filter(None, map( lambda file: self.create_image_object(join(file_path, file)), os.listdir(file_path))))
        
        # Tile Category Variables
        self.catergory_index = 0
        self.current_category = list(self.images.keys())[self.catergory_index]
        self.set_image_tilenum()

        self.image_lookup = {
            image.tile_number: image 
            for category in self.images.values()
            for image in category
        }

        # Edit Tile Properties
        self.selected_tile = None
        self.updated_tiles = set()
        self.redraw = False

        # Draw Grid
        for y in range(len(self.tile_map)):
            for x in range(len(self.tile_map[0])):
                pygame.draw.rect(display, 'grey', (x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size), 1)

        self.draw_image_object()

    def create_image_object(self, image_file_path, tile_size=None):
        try:
            return Tile(image_file_path, 0,0, tile_size)
        except Exception as e:
            print(f"Error loading image '{image_file_path}': {e}")
    
    def set_image_tilenum(self):
        tile_num = 0
        
        while self.catergory_index < len(self.images):
            for image in self.images[self.current_category]:
                tile_num += 1
                image.tile_number = tile_num
            
            # Move to the next category
            self.catergory_index += 1
            if self.catergory_index >= len(self.images):
                self.catergory_index = 0
                break
            
            self.current_category = list(self.images.keys())[self.catergory_index]
        
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

    def show_updated_tiles(self):
        if not self.updated_tiles:
            return
        
        for tile in self.updated_tiles:
            x, y, tile_num = tile
            # Clear Tile Area
            pygame.draw.rect(DISPLAY, 'black', (x * self.tile_size, y * self.tile_size,self.tile_size, self.tile_size))

            if tile_num > 0:
                image = self.image_lookup.get(tile_num)
                image.draw((x * TILE_SIZE, y * TILE_SIZE))
            
            pygame.draw.rect(DISPLAY, 'grey', (x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size), 1)
        
        self.updated_tiles = set()

    def handle_tiles(self, tile_pos):        
        add_tile, remove_tile = pygame.mouse.get_pressed()[0], pygame.mouse.get_pressed()[1]
        mouse_pos = pygame.mouse.get_pos()

        # First handle tile selection from palette (outside grid)
        for image in self.images[self.current_category]:
            if image.rect.collidepoint(mouse_pos) and add_tile:
                self.selected_tile = image.tile_number
                return  # Return early to avoid placing a tile in the same click
        
        # Then handle tile placement (inside grid)
        if tile_pos is not None:  # Make sure we have valid coordinates
            x, y = tile_pos
            
            # Check if within bounds of the tilemap
            if 0 <= x < len(self.tile_map[0]) and 0 <= y < len(self.tile_map):
                if add_tile and self.selected_tile is not None:
                    self.updated_tiles.add((x,y,self.selected_tile))
                    self.tile_map[y][x] = self.selected_tile
                    self.redraw = True

        self.show_updated_tiles()
        
    # Main Class Loop
    def run(self):
        mouse_pos = pygame.Vector2(
            min(max(pygame.mouse.get_pos()[0] // self.tile_size, 0), len(self.tile_map[0]) - 1),
            min(max(pygame.mouse.get_pos()[1] // self.tile_size, 0), len(self.tile_map) - 1)
        )
        mdx, mdy = round(mouse_pos.x), round(mouse_pos.y)

        self.handle_tiles([mdx,mdy])
    
       
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
 
    tile.run()

    pygame.display.update()
pygame.quit()
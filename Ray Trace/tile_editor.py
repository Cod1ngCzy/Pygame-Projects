from settings import *

pygame.init()
offset = 300
display = pygame.display.set_mode((WIDTH + offset,HEIGHT))
pygame.display.set_caption('Tile Editor')

running = True
clock = pygame.time.Clock()

class TileEditor():
    def __init__(self, tile_size: int, tile_map: str, tile_file_path=join('assets','tiles')):
        # Base Checks
        if not os.path.exists(tile_file_path):
            raise FileNotFoundError(f"Passed Argument Assumes a STRUCTURED folder. \nExample: \n📂 assets\n└── 📂 tiles")
        elif not os.path.exists(tile_file_path):
            raise FileNotFoundError(f"Passed Argument Assumes a STRUCTURED folder. \nExample: \n📂 assets\n└── tilemap.csv")
        
        self.tile_map = self.load_from_csv(tile_map) # Load CSV map to variable
        self.tile_size = tile_size
        
        self.folder_directories = [join(tile_file_path, folder_dir) for folder_dir in sorted(os.listdir(tile_file_path)) if os.path.isdir(join(tile_file_path, folder_dir))]
        self.images = {} # Variable containing all images object
        # Load Images into a dictionary
        for file_path in self.folder_directories:
            folder_name = os.path.basename(file_path)
            self.images[folder_name] = list(filter(None, map( lambda file: self.create_image_object(join(file_path, file)), os.listdir(file_path))))
        # Initialize Tilenum and Create a Image Lookup for easy rendering
        self.image_lookup = self.set_image_tilenum(self.images) 
        self.catergory_index = 0
        self.current_category = list(self.images.keys())[self.catergory_index]

        # Pallete Grid Variables
        pallete_pos_offset = 300
        pallete_width, pallete_height = (pallete_pos_offset, HEIGHT / 1.5)
        self.pallete_surface = pygame.Surface((pallete_width, pallete_height))
        self.scroll_offset = 0
        self.max_scroll = max(0, len(self.images[self.current_category]) // 3 * 75 - self.pallete_surface.get_height())

        self.selected_tile = None
        self.updated_tiles = set()
        self.redraw = False

        self.load_tiles_to_grid() # Load Current Tilemap
        self.draw_pallete_grid() # Load Tiles to Pallete Grid (Pallete Grid is a selection of images/tiles)

    def create_image_object(self, image_file_path, tile_size=None):
        """Uses Tile class at it's basis for creating an object."""
        try:
            return Tile(image_file_path, 0,0, tile_size)
        except Exception as e:
            print(f"Error loading image '{image_file_path}': {e}")
    
    def set_image_tilenum(self, images):
        tile_num = 0
        image_lookup = {}
        for category in images.values():
            for image in category:
                tile_num += 1
                image.tile_number = tile_num
                image_lookup[tile_num] = image

        return image_lookup # Returns Image Look up after tile num intialization
        
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

    def load_tiles_to_grid(self):
        for y, tiles in enumerate(self.tile_map):
            for x, tile in enumerate(tiles):
                tile_num = int(tile)

                image = self.image_lookup.get(tile_num)

                image.draw((x * self.tile_size, y * self.tile_size))
        
        # Draw Grid
        for y in range(len(self.tile_map)):
            for x in range(len(self.tile_map[0])):
                pygame.draw.rect(display, 'grey', (x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size), 1)

    def draw_pallete_grid(self):
        self.pallete_surface.fill((0, 0, 0))
        
        self.current_category = list(self.images.keys())[self.catergory_index]
        row_gap = 75
        col_gap = 75
        tiles_per_row = 3
        offset_pos = WIDTH
        
        # Calculate total number of tiles and rows needed
        total_tiles = len(self.images[self.current_category])
        total_rows = math.ceil(total_tiles / tiles_per_row)
        
        # Calculate the maximum scroll value based on content height
        self.max_scroll = max(0, (total_rows * row_gap) - self.pallete_surface.get_height() + 40)
        
        for i, image in enumerate(self.images[self.current_category]):
            col = i % tiles_per_row
            row = i // tiles_per_row
            
            x = offset_pos + (col_gap * col) + 40
            y = (row_gap * row) + 20 - self.scroll_offset
            
            # Only draw tiles that are within the viewport
            if 0 <= y < self.pallete_surface.get_height() + row_gap:
                image.rect.topleft = (x, y)
                image.draw((x - offset_pos, y), self.pallete_surface)
        
        # Add scroll indicators if content exceeds viewport
        if self.max_scroll > 0:
            if self.scroll_offset > 0:
                # Draw up arrow or indicator
                pygame.draw.polygon(self.pallete_surface, (200, 200, 200), 
                                [(self.pallete_surface.get_width() // 2, 10), 
                                    (self.pallete_surface.get_width() // 2 - 10, 25), 
                                    (self.pallete_surface.get_width() // 2 + 10, 25)])
            
            if self.scroll_offset < self.max_scroll:
                # Draw down arrow or indicator
                pygame.draw.polygon(self.pallete_surface, (200, 200, 200), 
                                [(self.pallete_surface.get_width() // 2, self.pallete_surface.get_height() - 10), 
                                    (self.pallete_surface.get_width() // 2 - 10, self.pallete_surface.get_height() - 25), 
                                    (self.pallete_surface.get_width() // 2 + 10, self.pallete_surface.get_height() - 25)])
        
        display.blit(self.pallete_surface, (WIDTH, 0))

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
    
    def handle_inputs(self):
        just_pressed = pygame.key.get_just_pressed()

        if just_pressed[pygame.K_s]:
            self.save_map()
            print('Tilemap Saved')
        elif just_pressed[pygame.K_l]:
            self.load_tile = True
        elif just_pressed[pygame.K_LEFTBRACKET]:
            self.catergory_index -= 1
            self.catergory_index = (tile.catergory_index + len(tile.images)) % len(tile.images)
            self.draw_pallete_grid()
        elif just_pressed[pygame.K_RIGHTBRACKET]:
            self.catergory_index += 1
            self.catergory_index = (tile.catergory_index + len(tile.images)) % len(tile.images)
            self.draw_pallete_grid()
        elif just_pressed[pygame.K_n]:  # Scroll up
            self.scroll_offset = max(0, self.scroll_offset - 20)
            self.draw_pallete_grid()
        elif just_pressed[pygame.K_m]:  # Scroll down
            self.scroll_offset = min(self.max_scroll, self.scroll_offset + 20)
            self.draw_pallete_grid()
        

    def handle_tiles(self, tile_pos):   
        self.handle_inputs()
        
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
        mouse_pos = min(max(pygame.mouse.get_pos()[0] // self.tile_size, 0), len(self.tile_map[0]) - 1), min(max(pygame.mouse.get_pos()[1] // self.tile_size, 0), len(self.tile_map) - 1)
        
        mdx, mdy = round(mouse_pos[0]), round(mouse_pos[1])

        self.handle_tiles([mdx,mdy])
    
       
tile = TileEditor(TILE_SIZE, join('assets', 'tilemap.csv'))

while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            

    tile.run()

    pygame.display.update()
pygame.quit()
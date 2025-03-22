from settings import *

pygame.init()
offset = 300
display = pygame.display.set_mode((WIDTH + offset,HEIGHT))
pygame.display.set_caption('Tile Editor')

running = True
clock = pygame.time.Clock()

class TileHandler():
    def __init__(self):
        # File and Folder Variables
        self.file_path = 'assets/tiles'
        self.folder_directories = ()
        self.images = {}  
        self.image_objects = {} 
        self.image_lookup = {}  

        # Initialize
        self.handle_file_path()
        self.handle_images()

    def handle_file_path(self):
        if not os.path.exists('assets'):
            os.makedirs(self.file_path)
            raise FileNotFoundError(f"Directories not found. Tile Editor requires a STRUCTURED folder. \nExample: \n📂 assets\n└── 📂 tiles\nCreating required folders...")
        
    def handle_images(self):
        self.folder_directories = [folder_name for folder_name in os.listdir(self.file_path) 
                             if os.path.isdir(os.path.join(self.file_path, folder_name))]
        
        # Return if no folders are found
        if not self.folder_directories:
            print("No tile folders found in", self.file_path)
            return 

        images, image_objects = {}, {}
        for folder_name in self.folder_directories:
            folder_path = os.path.join(self.file_path, folder_name)
            images[folder_name] = [image for image in os.listdir(folder_path)]
            image_objects[folder_name] = list(filter(None, map(lambda file: self.set_image_object(os.path.join(folder_path,file)), os.listdir(folder_path))))

        self.images, self.image_objects = images, image_objects
        self.set_image_tilenum(image_objects)

    def set_image_object(self, image_file_path, tile_size=None):
        """Uses Tile class as basis for creating an object."""
        try:
            return Tile(image_file_path, 0, 0, tile_size)
        except Exception as e:
            print(f"Error loading image '{image_file_path}': {e}")
            return None
    
    def set_image_tilenum(self, image_objects):
        """Assigns unique tile numbers to all tile objects"""
        tile_num = 0
        
        for category_tiles in image_objects.values():
            for tile in category_tiles:
                tile_num += 1
                tile.tile_number = tile_num
                self.image_lookup[tile_num] = tile
        
    def get_tile_by_number(self, number):
        """Retrieve a tile by its assigned number"""
        return self.image_lookup.get(number)
 
class TileMapManager():
    def __init__(self, file_path_to_map: str):
        self.file_path = file_path_to_map
        self.tile_map = self.load_tilemap()
    
    def load_tilemap(self):  
        map = []
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f'{self.file_path} not found')
        
        with open(self.file_path) as file:
            tile = csv.reader(file, delimiter=',')
            for row in tile:
                map.append(list(row))

        return map
    
    def save_tilemap(self):
        with open(self.file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            for row in self.tile_map:
                writer.writerow(row)
        return True
        
class TileEditor():
    def __init__(self, tile_size: int, tile_map: str, tile_file_path=join('assets','tiles')):
        # Create a single TileHandler instance and store it
        self.tile_handler = TileHandler()
        self.tile_manager = TileMapManager(tile_map)
        
        # Reference the data from that single instance
        self.images = self.tile_handler.image_objects
        self.image_lookup = self.tile_handler.image_lookup
        self.tile_map = self.tile_manager.tile_map
        self.tile_size = tile_size # Load Tile Size

        self.catergory_index = 0
        self.current_category = list(self.images.keys())[self.catergory_index]

        # Pallete Grid Variables
        self.pallete_surface = pygame.Surface((300, HEIGHT / 1.5))
        self.scroll_offset = 0
        self.max_scroll = max(0, len(self.images[self.current_category]) // 3 * 75 - self.pallete_surface.get_height())

        self.selected_tile = None
        self.updated_tiles = set()
        self.redraw = False

        self.load_tiles_to_grid() # Load Current Tilemap
        self.draw_pallete_grid() # Load Tiles to Pallete Grid (Pallete Grid is a selection of images/tiles)

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
        pygame.draw.rect(self.pallete_surface, (105,105,105), (0, 0, self.pallete_surface.get_width(),self.pallete_surface.get_height() ))
        
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
            self.tile_manager.tile_map = self.tile_map
            self.tile_manager.save_tilemap()
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
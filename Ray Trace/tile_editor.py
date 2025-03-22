from settings import *

class Tile:
    def __init__(self, image_file_path, x, y, size=None, tile_number=None, display=None):
        if size is None:
            size = TILE_SIZE
            
        # Load and scale the tile image
        self.image = pygame.image.load(image_file_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (size, size))
        self.display = display
        
        # Create a rect for the tile and center it at (x, y)
        self.rect = self.image.get_frect(topleft=(x, y))
        self.tile_number = tile_number
        self.is_collision = False
        self.image_name = os.path.basename(image_file_path)
    
    def draw(self, pos=None, display=None):
        if pos is None:
            pos = self.rect
        
        if display == None:
            display = DISPLAY

        display.blit(self.image, pos)

class TileImageManager():
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

class TileEditor:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        self.ORIGIN_WIDTH, self.ORIGIN_HEIGHT = 1324, 768
        self.ORIGIN_DISPLAY = pygame.display.set_mode((self.ORIGIN_WIDTH, self.ORIGIN_HEIGHT))
        pygame.display.set_caption('2D Tile Editor')

        # State Variables
        self.clock = pygame.time.Clock()
        self.running = True

        # Initialize resources
        self.init_resources()

    def init_resources(self):
        # Tile Editor Variables
        self.tile_size = TILE_SIZE
        self.tile_handler = TileImageManager()
        self.tile_manager = TileMapManager(join('assets', 'tilemap.csv'))
        
        # Reference the data from TileHandler and TileMapManager
        self.images = self.tile_handler.image_objects
        self.image_lookup = self.tile_handler.image_lookup
        self.tile_map = self.tile_manager.tile_map

        # Editor State
        self.category_index = 0
        self.current_category = list(self.images.keys())[self.category_index]
        self.selected_tile = None
        self.updated_tiles = set()
        self.redraw = False

        # Palette Screen Variables
        self.palette_surface = pygame.Surface((300, self.ORIGIN_HEIGHT // 1.5))
        self.scroll_offset = 0
        self.max_scroll = max(0, len(self.images[self.current_category]) // 3 * 75 - self.palette_surface.get_height())

        # Grid Screen Variables
        self.grid_surface_width ,self.grid_surface_height = 1024, 700
        self.grid_surface = pygame.Surface((self.grid_surface_width, self.grid_surface_height))
        self.grid_width, self.grid_height = self.grid_surface_width // self.tile_size, self.grid_surface_height // self.tile_size
        # Camera Variables (Viewport)
        self.camera_x, self.camera_y = 0, 0  # Camera position
        self.zoom = 1.0  # Default zoom level
        # World Variables (Imported World Level)
        self.world_width, self.world_height = 1024,768
        self.world_tilesize = 64
        self.world_surface = pygame.Surface((self.world_width, self.world_height)) 

        # Load tiles to grid and draw the palette
        #self.load_tiles_to_grid()
        self.draw_grid_surface()
        self.draw_palette_surface()

    def draw_palette_surface(self):
        """Draw the tile palette grid."""
        pygame.draw.rect(self.palette_surface, (105, 105, 105), (0, 0, self.palette_surface.get_width(), self.palette_surface.get_height()))
        
        row_gap = 75
        col_gap = 75
        tiles_per_row = 3
        offset_pos = 1024
        
        # Calculate total number of tiles and rows needed
        total_tiles = len(self.images[self.current_category])
        total_rows = math.ceil(total_tiles / tiles_per_row)
        
        # Calculate the maximum scroll value based on content height
        self.max_scroll = max(0, (total_rows * row_gap) - self.palette_surface.get_height() + 40)
        
        for i, image in enumerate(self.images[self.current_category]):
            col = i % tiles_per_row
            row = i // tiles_per_row
            
            x = offset_pos + (col_gap * col) + 40
            y = (row_gap * row) + 20 - self.scroll_offset
            
            # Only draw tiles that are within the viewport
            if 0 <= y < self.palette_surface.get_height() + row_gap:
                image.rect.topleft = (x, y)
                image.draw((x - offset_pos, y), self.palette_surface)
        
        # Add scroll indicators if content exceeds viewport
        if self.max_scroll > 0:
            if self.scroll_offset > 0:
                # Draw up arrow or indicator
                pygame.draw.polygon(self.palette_surface, (200, 200, 200), 
                                [(self.palette_surface.get_width() // 2, 10), 
                                 (self.palette_surface.get_width() // 2 - 10, 25), 
                                 (self.palette_surface.get_width() // 2 + 10, 25)])
            
            if self.scroll_offset < self.max_scroll:
                # Draw down arrow or indicator
                pygame.draw.polygon(self.palette_surface, (200, 200, 200), 
                                [(self.palette_surface.get_width() // 2, self.palette_surface.get_height() - 10), 
                                 (self.palette_surface.get_width() // 2 - 10, self.palette_surface.get_height() - 25), 
                                 (self.palette_surface.get_width() // 2 + 10, self.palette_surface.get_height() - 25)])
        
        self.ORIGIN_DISPLAY.blit(self.palette_surface, (1024, 0))

    def draw_grid_surface(self):
        # Render Grid Surface
        pygame.draw.rect(self.grid_surface, (255,255,255), (0,0, self.grid_surface_width, self.grid_surface_height))

        # World Surface Blit #
        self.world_surface.fill((30, 30, 30))  # Background Color
        
        for y, tiles in enumerate(self.tile_map):
            for x, tile in enumerate(tiles):
                tile_num = int(tile)

                image = self.tile_handler.get_tile_by_number(tile_num)
                image.draw((x * self.world_tilesize, y * self.world_tilesize), self.world_surface)

        for x in range(0, self.world_width, self.world_tilesize):
            for y in range(0, self.world_height, self.world_tilesize):
                pygame.draw.rect(self.world_surface, (80, 80, 80), (x, y, self.world_tilesize, self.world_tilesize), 1)

        self.grid_surface.blit(self.world_surface, (-self.camera_x,-self.camera_y))
        self.ORIGIN_DISPLAY.blit(self.grid_surface, (0,0))
    
    def handle_inputs(self):
        """Handle user inputs."""
        keys = pygame.key.get_pressed()
        just_pressed = pygame.key.get_just_pressed()

        if just_pressed[pygame.K_s]:
            self.tile_manager.tile_map = self.tile_map
            self.tile_manager.save_tilemap()
            print('Tilemap Saved')
        elif just_pressed[pygame.K_LEFTBRACKET]:
            self.category_index = (self.category_index - 1) % len(self.images)
            self.current_category = list(self.images.keys())[self.category_index]
            self.draw_grid_surface()
        elif just_pressed[pygame.K_RIGHTBRACKET]:
            self.category_index = (self.category_index + 1) % len(self.images)
            self.current_category = list(self.images.keys())[self.category_index]
            self.draw_grid_surface()
        elif just_pressed[pygame.K_n]:  # Scroll up
            self.scroll_offset = max(0, self.scroll_offset - 20)
            self.draw_grid_surface()
        elif just_pressed[pygame.K_m]:  # Scroll down
            self.scroll_offset = min(self.max_scroll, self.scroll_offset + 20)
            self.draw_grid_surface()

        # Camera Panning
        if keys[pygame.K_UP]:
            self.camera_y = max(-200, self.camera_y -10)
        if keys[pygame.K_DOWN]: 
            self.camera_y = min(200, self.camera_y + 10)
        if keys[pygame.K_LEFT]: 
            self.camera_x -= 10  # Move Left
        if keys[pygame.K_RIGHT]: 
            self.camera_x += 10  # Move Right

    def handle_tiles(self, tile_pos):
        """Handle tile placement and selection."""
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
                    self.updated_tiles.add((x, y, self.selected_tile))
                    self.tile_map[y][x] = self.selected_tile
                    self.redraw = True
        
    def run(self):
        """Main loop for the tile editor."""
        while self.running:
            delta_time = self.clock.tick(60) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Get mouse position in grid coordinates
            mouse_pos = (
                min(max((pygame.mouse.get_pos()[0] + self.camera_x) // self.world_tilesize, 0), len(self.tile_map[0]) - 1),
                min(max((pygame.mouse.get_pos()[1] + self.camera_y) // self.world_tilesize, 0), len(self.tile_map) - 1)
            )
            mdx, mdy = round(mouse_pos[0]), round(mouse_pos[1])

            # Handle tile placement and input
            self.handle_tiles([mdx, mdy])

            #self.load_tiles_to_grid()
            self.draw_palette_surface()
            self.draw_grid_surface()

            pygame.display.update()

        pygame.quit()

TileEditor().run()
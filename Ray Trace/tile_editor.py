import pygame, sys, math, json, csv, os
from os.path import join

class Tile:
    def __init__(self, image_file_path, x, y, size=None, tile_number=None, display=None):
        # Load the tile image
        self.image = pygame.image.load(image_file_path).convert_alpha()
        
        # Use the provided size or default to 64
        self.size = size if size is not None else 64
        
        # Scale the image once during initialization
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
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
            display = pygame.Surface((0,0))
            
        # No need to rescale every time - only blit the image
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
        self.root_path = 'assets' 
        self.file_name = file_path_to_map
        self.tile_maps = self.check_existent_tilemaps()
        self.tile_map = {}
        
        self.handle_tilemap()

    def handle_multiple_tilemap(self):
        tilemapset = {}
        pass # To Work On. Should handle multiple tiles (if many levels are created)

    def handle_tilemap(self):
        # Checks if file name exists
        if os.path.exists(self.file_name):
            self.tile_map = self.load_tilemap(self.file_name)
            return True

        print(f'{self.file_name} doesn\'t exists. \nCreating custom tilemap')
        self.create_tilemap() # Default Tilemap
        self.tile_map = self.load_tilemap('assets/new_map.csv')
     
    def load_tilemap(self, file_path):
        tilemap = {
            'metadata': {
                'world_width': None,
                'world_height':None,
                'world_tilesize': None,
                'world_name': None
            },
            'map': []
        }

        # If base check == true, open file
        with open(file_path) as file:
            csv_reader = csv.reader(file)
            parsing_metadata = False

            for row in csv_reader:
                if not row or row[0].startswith("#"):  # Skip empty lines & comments
                    if row and row[0] == "#metadata":
                        parsing_metadata = True  # Start reading metadata
                    elif row and row[0] == "#tilemap":
                        parsing_metadata = False  # Stop reading metadata
                    continue

                if parsing_metadata:
                    key, value = row
                    tilemap['metadata'][key] = int(value) if value.isdigit() else value # Store metadata
                else:
                    tilemap['map'].append([int(x) for x in row])  # Store tilemap

        return tilemap

    def save_tilemap(self, tile_map=None):
        tile_map_holder = []

        with open(self.file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            
            # Write metadata
            writer.writerow(["#metadata"])
            for key, value in self.tile_map['metadata'].items():
                writer.writerow([key, value])
            writer.writerow([])  # Empty row to separate metadata from tilemap
            
            # Write tilemap data
            writer.writerow(["#tilemap"])
            for row in self.tile_map['map']:
                writer.writerow(row)
        
        return True
    
    def create_tilemap(self, width:int=None, height:int=None, tilesize:int=None, worldname:str=None):
        default_width = width if width else 1024
        default_height = height if height else 768
        default_tilesize = tilesize if tilesize else 32
        world_name = worldname if worldname else 'new_map'

        default_tile_map = [[1 for _ in range(default_width // default_tilesize)] for _ in range(default_height // default_tilesize)]

        with open(f'{self.root_path}/{world_name}.csv', 'w', newline='') as file:
            meta_data_header, tilemap_header = '#metadata', '#tilemap'
            csv_writer = csv.writer(file)

            # CREATE METADATA HEADER
            csv_writer.writerow([meta_data_header])
            meta_data = {
                    'world_width': default_width,
                    'world_height':default_height,
                    'world_tilesize': default_tilesize,
                    'world_name': world_name
                }
            
            for key, value in meta_data.items():
                csv_writer.writerow([key, value])
            
            # Create empty space for seperation
            csv_writer.writerow([])

            # CREATE TILEMAP HEADER
            csv_writer.writerow([tilemap_header])
            for row in default_tile_map:
                csv_writer.writerow(row)
            
        print(f'Successfully Created a new tilemap: {world_name}.csv')

    def check_existent_tilemaps(self):
        tile_maps = []
        for path in os.listdir(self.root_path):
            if path.endswith('.csv'):
                tile_maps.append(join(self.root_path,path))
        
        return tile_maps

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
        self.init_tile_editor()
        self.init_grid_surface()
        self.init_pallete_surface()
    
    def init_tile_editor(self):
        # Tile Editor Variables
        self.tile_handler = TileImageManager()
        self.tile_manager = TileMapManager(join('assets', 'tilema.csv'))
        
        # Reference the data from TileHandler and TileMapManager
        self.images = self.tile_handler.image_objects
        self.image_lookup = self.tile_handler.image_lookup

        self.tile_map = self.tile_manager.tile_map

        # State Variables
        self.category_index = 0
        if not len(self.images.keys()) > 1:
            self.current_category = ''
        self.current_category = list(self.images.keys())[self.category_index]

        # State Variables
        self.selected_tile = None
        self.on_pallete = False
        self.on_grid = False
        self.tilemap_found = True
    
    def init_grid_surface(self):
        # --- Grid Surface Variables --- #
        # Grid 
        self.world_tilesize = self.tile_map['metadata']['world_tilesize']
        self.grid_surface_width ,self.grid_surface_height = 1024, 768
        self.grid_surface = pygame.Surface((self.grid_surface_width, self.grid_surface_height))
        self.grid_surface_rect = self.grid_surface.get_frect(topleft = (0,0))
        self.grid_width, self.grid_height = self.grid_surface_width // self.world_tilesize, self.grid_surface_height // self.world_tilesize
        self.grid_static_bg = pygame.image.load(join('assets', 'grid_bg.png')).convert_alpha()
        # World Variables (Imported World Level)
        self.world_width, self.world_height = self.tile_map['metadata']['world_width'],self.tile_map['metadata']['world_height']
        self.world_surface = pygame.Surface((self.world_width, self.world_height)) 
        self.world_surface_rect = self.world_surface.get_frect(center = (self.grid_width // 2 ,self.grid_height // 2))
        # Camera Variables (Viewport)
        self.zoom = 1 # Default zoom level
        self.dragging = False
        self.start_drag_x, self.start_drag_y = 0,0
        self.start_camera_pos_x, self.start_camera_pos_y = 0,0
        self.camera = pygame.Vector2(0,0)
        # --- Grid Surface Variables --- #
        self.draw_grid_surface()
        return True

    def init_pallete_surface(self):
        # --- Pallete Surface Variables --- #
        self.pallete_width, self.pallete_height = 300, self.ORIGIN_HEIGHT // 2
        self.palette_surface = pygame.Surface((self.pallete_width, self.pallete_height))
        self.palette_surface_rect = self.palette_surface.get_frect(topleft = (1024,0))
        self.row_gap, self.col_gap = 75, 75
        self.max_rows = 3
        self.scroll_offset = 0
        self.max_scroll = 0
        # --- Pallete Surface Variables --- #
        self.draw_palette_surface()
        return True

    def draw_palette_surface(self):
        pygame.draw.rect(self.palette_surface, (0,0,0), (0, 0, self.pallete_width, self.pallete_height))
        pygame.draw.rect(self.palette_surface, (80,79,79), (0, 0, self.pallete_width, self.pallete_height), 1)
        
        # Calculate total number of tiles and rows needed
        total_tiles = len(self.images[self.current_category])
        total_rows = math.ceil(total_tiles / self.max_rows)
        screen_offset_pos = self.ORIGIN_WIDTH - self.pallete_width # Offset from original display screen
        
        # Calculate the maximum scroll value based on content height
        self.max_scroll = max(0, (total_rows * self.row_gap) - self.pallete_height + 20)

        for i, image in enumerate(self.images[self.current_category]):
            col = i % self.max_rows
            row = i // self.max_rows
            
            x = screen_offset_pos + (self.col_gap * col) + 40
            y = (self.row_gap * row) + 20 - self.scroll_offset
            
            # Only draw tiles that are within the viewport
            if 0 <= y < self.pallete_height + self.row_gap:
                image.rect.topleft = (x, y)
                image.draw((x - screen_offset_pos, y), self.palette_surface)
        
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
        if self.tilemap_found:
            self.grid_surface.fill((0,0,0))
            self.grid_surface.blit(self.grid_static_bg,(-10,-5))
            pygame.draw.rect(self.grid_surface, (80,79,79), (0,0, self.grid_surface_width, self.grid_surface_height),1)
            self.world_surface.fill((30, 30, 30))  
            
            for y, tiles in enumerate(self.tile_map['map']):
                for x, tile in enumerate(tiles):
                    tile_num = int(tile)

                    image = self.tile_handler.get_tile_by_number(tile_num)
                    scaled_image = pygame.transform.scale(image.image, (self.world_tilesize, self.world_tilesize))
                    self.world_surface.blit(scaled_image, (x * self.world_tilesize, y * self.world_tilesize))

            for x in range(0, self.world_width, self.world_tilesize):
                for y in range(0, self.world_height, self.world_tilesize):
                    pygame.draw.rect(self.world_surface, (80, 80, 80), (x, y, self.world_tilesize, self.world_tilesize), 1)
            
            scaled_world = pygame.transform.scale(self.world_surface, (self.world_width * self.zoom,self.world_height * self.zoom))
            
            self.world_surface_rect = -self.camera.x, -self.camera.y

            self.grid_surface.blit(scaled_world, self.world_surface_rect)
            self.ORIGIN_DISPLAY.blit(self.grid_surface, (0,0))
        else:
            # Config Screen
            self.grid_surface.fill((0,0,0))
            self.grid_surface.blit(self.grid_static_bg,(-10,-5))
            pygame.draw.rect(self.grid_surface, (80,79,79), (0,0, self.grid_surface_width, self.grid_surface_height),1)
            
            pygame.draw.rect(self.grid_surface, 'white', (self.grid_surface_width / 2, self.grid_surface_height / 2, 300,300))
            self.ORIGIN_DISPLAY.blit(self.grid_surface, (0,0))
             
    def handle_inputs(self):
        keys = pygame.key.get_pressed()
        just_pressed = pygame.key.get_just_pressed()

        if just_pressed[pygame.K_s]:
            self.tile_manager.tile_map = self.tile_map
            self.tile_manager.save_tilemap()
            print('Tilemap Saved')
        elif just_pressed[pygame.K_LEFTBRACKET]:
            self.scroll_offset = 0
            self.category_index = (self.category_index - 1) % len(self.images)
            self.current_category = list(self.images.keys())[self.category_index]
            self.draw_grid_surface()
        elif just_pressed[pygame.K_RIGHTBRACKET]:
            self.scroll_offset = 0
            self.category_index = (self.category_index + 1) % len(self.images)
            self.current_category = list(self.images.keys())[self.category_index]
            self.draw_grid_surface()
        elif just_pressed[pygame.K_n]:  # Scroll up
            self.scroll_offset = max(0, self.scroll_offset - 20)
            self.draw_grid_surface()
        elif just_pressed[pygame.K_m]:  # Scroll down
            self.scroll_offset = min(self.max_scroll, self.scroll_offset + 20)
            self.draw_grid_surface()

        # Zooming (In/Out)
        if keys[pygame.K_q]:  # Zoom In
            self.zoom = min(2.0, self.zoom + 0.05)
        if keys[pygame.K_e]:  # Zoom Out
            self.zoom = max(0.5, self.zoom - 0.05)

        # Recalculate tile size for zoom effect
    
    def handle_camera_panning(self, mouse_pos):
        delta_change_x = self.start_drag_x - mouse_pos[0]
        delta_change_y = self.start_drag_y - mouse_pos[1]

        self.camera.x = self.start_camera_pos_x + delta_change_x
        self.camera.y = self.start_camera_pos_y + delta_change_y

    def handle_mouse(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        mouse_just_click = pygame.mouse.get_just_pressed()
        mouse_just_released = pygame.mouse.get_just_released()
        
        # Mouse Clicks
        if mouse_just_click[2]:
            self.start_drag_x, self.start_drag_y = mouse_pos[0], mouse_pos[1]
            self.start_camera_pos_x, self.start_camera_pos_y = self.camera.x, self.camera.y
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEALL)
            self.dragging = True
        if mouse_just_released[2]:
            self.dragging = False
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # Mouse Collisions
        if self.palette_surface_rect.collidepoint(mouse_pos):
            self.on_pallete = True
        else:
            self.on_pallete = False
        if self.grid_surface_rect.collidepoint(mouse_pos):
            self.on_grid = True
        else:
            self.on_grid = False

        # If on pallete
        if self.on_pallete:
            self.handle_pallete_interactions(mouse_pos, mouse_click)
        elif self.on_grid:
            self.handle_grid_interactions(mouse_pos, mouse_click)

        if self.dragging:
            self.handle_camera_panning(mouse_pos)
    
    def handle_pallete_interactions(self, mouse_pos, mouse_click):
        for image in self.images[self.current_category]:
            if image.rect.collidepoint(mouse_pos) and mouse_click[0]:
                self.selected_tile = image.tile_number
    
    def handle_grid_interactions(self, mouse_pos, mouse_click):
        # Convert mouse position into world space, accounting for camera position and zoom
        world_x = (mouse_pos[0] + self.camera.x) / self.zoom 
        world_y = (mouse_pos[1] + self.camera.y) / self.zoom

        # Convert world position to grid indices
        grid_x = int(world_x // self.world_tilesize)
        grid_y = int(world_y // self.world_tilesize)

        # Make sure grid coordinates are within bounds
        if 0 <= grid_x < len(self.tile_map['map'][0]) and 0 <= grid_y < len(self.tile_map['map']):
            if mouse_click[0] and self.selected_tile:
                self.tile_map['map'][grid_y][grid_x] = self.selected_tile
                
        
        return self.tile_map
    
    def run(self):
        while self.running:
            delta_time = self.clock.tick(60) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.handle_inputs()
            self.handle_mouse()
            self.draw_palette_surface()
            self.draw_grid_surface()

            pygame.display.update()

        pygame.quit()

TileEditor().run()
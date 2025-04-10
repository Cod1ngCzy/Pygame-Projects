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
        self._required_file_paths = {
            'base_path': os.path.join('assets', 'tiles'),
            'background_folder_path': os.path.join('assets','tiles','background'),
            'foreground_folder_path': os.path.join('assets','tiles','foreground')
        }
     
        self.images = {
            'background': {},
            'foreground': {}
        }  
        self.image_objects = {
            'background': {},
            'foreground': {}
        } 
        self.image_lookup = {
            'background': {},
            'foreground': {}
        }  # To be changed 

        # Initialize 
        self._validate_file_paths()
        self._handle_background_layer_images()
        self._handle_foreground_layer_images()

    def _validate_file_paths(self):
        # Validates Required Folder/File Paths
        if not os.path.exists(self._required_file_paths['base_path']):
            os.makedirs(self._required_file_paths['base_path'])
        elif not os.path.exists(self._required_file_paths['background_folder_path']):
            os.makedirs(self._required_file_paths['background_folder_path'])
        elif not os.path.exists(self._required_file_paths['foreground_folder_path']):
            os.makedirs(self._required_file_paths['foreground_folder_path'])
    
    def _handle_background_layer_images(self):
        background_folder_path = [folder_name for folder_name in os.listdir(self._required_file_paths['background_folder_path'])]

        for folder_name in background_folder_path:
            folder_path = os.path.join(self._required_file_paths['background_folder_path'], folder_name)
            self.images['background'][folder_name] = [image_name for image_name in os.listdir(folder_path)]
            self.image_objects['background'][folder_name] = list(filter(None, map(lambda file: self._set_image_object(os.path.join(folder_path,file)), os.listdir(folder_path))))

        # Clear File Name Path
        self.images['background'] = {}
        self._set_image_tilenum(self.image_objects['background'],'background')

    def _handle_foreground_layer_images(self):
        foreground_folder_path = [folder_name for folder_name in os.listdir(self._required_file_paths['foreground_folder_path'])]

        for folder_name in foreground_folder_path:
            folder_path = os.path.join(self._required_file_paths['foreground_folder_path'], folder_name)
            self.images['foreground'][folder_name] = [image_name for image_name in os.listdir(folder_path)]
            self.image_objects['foreground'][folder_name] = list(filter(None, map(lambda file: self._set_image_object(os.path.join(folder_path,file)), os.listdir(folder_path))))
        
        # Clear File Name Path
        self.images['foreground'] = {}
        self._set_image_tilenum(self.image_objects['foreground'], 'foreground')

    def _set_image_object(self, image_file_path, tile_size=None):
        """Uses Tile class as basis for creating an object."""
        try:
            return Tile(image_file_path, 0, 0, tile_size)
        except Exception as e:
            print(f"Error loading image '{image_file_path}': {e}")
            return None
    
    def _set_image_tilenum(self, image_objects,layer):
        """Assigns unique tile numbers to all tile objects"""
        tile_num = 0
        
        for category_tiles in image_objects.values():
            for tile in category_tiles:
                tile_num += 1
                tile.tile_number = tile_num
                self.image_lookup[layer][tile_num] = tile
    
    # ==== OUTSIDE FUNCTIONS ==== #
    def get_tile_by_number(self, number, layer):
        """Retrieve a tile by its assigned number"""
        return self.image_lookup[layer].get(number)

    def get_image_object(self):
        if self.image_objects is None:
            raise ReferenceError("Image Object is empty. Might be error on handling process.")
        return self.image_objects

    def get_image_lookup(self):
        if self.image_lookup is None:
            raise ReferenceError("Image Lookup is empty. Might be error on handling process.")
        return self.image_lookup
 
class TileMapManager():
    def __init__(self):
        self._root_path = 'assets/maps' 
        self._accessed_tilemap = ''
        self._cache_tilemaps = {} # {map_name: map_full_path}
        self._map_names = self._cache_tilemaps.keys()

        # Intialize Tile Map Manager
        self._init_tilemanager()
    
    def _handle_mapname_duplicate(self, map_name):
        base_name = map_name
        name_counter = 1

        while map_name in self._cache_tilemaps:
            if name_counter >= 3:
                break
            map_name = f'{base_name}_{name_counter}'
            
            name_counter += 1

        return map_name
    
    def _init_tilemanager(self):
        tilemaps_path = [map_name for map_name in os.listdir(self._root_path) if map_name.endswith('.csv')]

        if tilemaps_path:
            # First Item Only
            if len(tilemaps_path) > 1:
                map = tilemaps_path[0]

            map = tilemaps_path

            # Load Cache Data
            self._cache_tilemaps = {
                mapname: join(self._root_path, mapname)
                for mapname in map
            }
        else:
            self.create_tilemap()
            
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

    def save_tilemap(self,modified_tile_map):
        tile_map = modified_tile_map

        with open(self._cache_tilemaps.get(self._accessed_tilemap), 'w', newline='') as file:
            writer = csv.writer(file)
            
            # Write metadata
            writer.writerow(["#metadata"])
            for key, value in tile_map['metadata'].items():
                writer.writerow([key, value])
            writer.writerow([])  # Empty row to separate metadata from tilemap
            
            # Write tilemap data
            writer.writerow(["#tilemap"])
            for row in tile_map['map']:
                writer.writerow(row)
        
        return True
    
    def create_tilemap(self, width:int=None, height:int=None, tilesize:int=None, map_name:str=None):
        default_width = width if width else 1024
        default_height = height if height else 768
        default_tilesize = tilesize if tilesize else 32
        default_name = map_name if map_name else 'untitled_map'
        default_tile_map = [[1 for _ in range(default_width // default_tilesize)] for _ in range(default_height // default_tilesize)]

        world_name = self._handle_mapname_duplicate(default_name)
        full_path_map = join(self._root_path, f'{world_name}.csv')

        with open(full_path_map, 'w', newline='') as file:
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
        
        self._cache_tilemaps[world_name] = full_path_map # Updates and Stores, FILE NAME AND PATH ONLY (not loaded) lazy loading

    def access_tilemap(self, map_name):
        if map_name in self._cache_tilemaps:
           self._accessed_tilemap = map_name
           return self.load_tilemap(self._cache_tilemaps.get(map_name))
        else:
            raise FileNotFoundError
             
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
        self.font = pygame.font.Font(None, 25)

        # Initialize resources
        self._init_tile_editor()
    
    def _init_tile_editor(self):
        # Create an instance of classes
        self.TILEIMAGE_HANDLER = TileImageManager()
        self.TILEMAP_MANAGER = TileMapManager()
        
        # Reference the data from TileHandler and TileMapManager
        self.images = self.TILEIMAGE_HANDLER.get_image_object()
        self.image_lookup = self.TILEIMAGE_HANDLER.get_image_lookup()
        
        self.tile_map_index = 0
        self.available_tile_maps = self.TILEMAP_MANAGER._cache_tilemaps.keys()
        self.tile_map_keys = list(self.available_tile_maps)[self.tile_map_index]
        self.tile_map = self.TILEMAP_MANAGER.access_tilemap(self.tile_map_keys)

        # === SCREEN COMPONENTS === #
        
        # Independent Screen Component #
        self.menu_component = TileEditor_Menu(self.TILEMAP_MANAGER)
        self.menu_component_surface = self.menu_component.get_surface()
        self.menu_component_rect = self.menu_component_surface.get_frect(topleft = (0,0))
        
        # Grouped Screen Component #
        self.grid_component = TileEditor_Grid(self.tile_map,self.TILEIMAGE_HANDLER, self.TILEMAP_MANAGER)
        self.grid_component_surface = self.grid_component.get_surface() # TODO: Fix how tilemap is passed upon this function
        self.grid_component_rect = self.grid_component_surface.get_frect(topleft = (0,0))

        self.pallete_component = TileEditor_Pallete(self.images['background'], self.image_lookup)
        self.pallete_component_surface = self.pallete_component.get_surface()
        self.pallete_component_rect = self.pallete_component_surface.get_frect(topleft = (1024,0))

        self.config_component = TileEditor_Config(self.tile_map, self.font)
        self.config_component_surface = self.config_component.get_surface()
        self.config_component_rect = self.config_component_surface.get_frect(topleft = (1024, 768 / 2))
        # === SCREEN COMPONENTS === #

        # Flag Variables
        self.selected_tilenum = None
        self.on_pallete = False
        self.on_grid = False
        self.on_config = False
        self.load_map = False
        self.create_map = False

        # Isolated Flag
        self.on_menu = True

    def _handle_menu_surface(self):
        self.menu_component.render()
        self.ORIGIN_DISPLAY.blit(self.menu_component_surface, self.menu_component_rect)

    def _handle_config_surface(self):
        self.config_component.render()
        self.ORIGIN_DISPLAY.blit(self.config_component_surface, self.config_component_rect.topleft)

    def _handle_palette_surface(self):
        self.pallete_component.render()
        self.ORIGIN_DISPLAY.blit(self.pallete_component_surface, self.pallete_component_rect.topleft)

    def _handle_grid_surface(self):
        self.grid_component.render() 
        self.ORIGIN_DISPLAY.blit(self.grid_component_surface, self.grid_component_rect.topleft)
    
    def handle_inputs(self):
        # Mouse Interactions
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()
        mouse_just_click = pygame.mouse.get_just_pressed()
        mouse_just_released = pygame.mouse.get_just_released()

        # Keyboard Interactions
        keys = pygame.key.get_pressed()
        keys_just_pressed = pygame.key.get_just_pressed()

        if self.on_menu:
            self.menu_component.handle_inputs(mouse_pos, mouse_click, mouse_just_click, mouse_just_released, keys, keys_just_pressed)
        else:
            # === KEYBOARD === #
            if keys_just_pressed[pygame.K_s]:
                self.TILEMAP_MANAGER.save_tilemap(self.tile_map)
                print('Tilemap Saved')
            # === KEYBOARD === #

            # === MOUSE === #
            if self.pallete_component_rect.collidepoint(mouse_pos):
                self.on_pallete = True
                self.selected_tilenum = self.pallete_component.get_selected_tilenum()
            else:
                self.on_pallete = False

            if self.grid_component_rect.collidepoint(mouse_pos):
                self.on_grid = True
            else:
                self.on_grid = False
            
            if self.config_component_rect.collidepoint(mouse_pos):
                self.on_config = True
            else:
                self.on_config = False
            # === MOUSE === #

            self.config_component.handle_inputs(mouse_pos, mouse_click, mouse_just_click, mouse_just_released, self.on_grid, keys, keys_just_pressed)
            self.pallete_component.handle_inputs(mouse_pos, mouse_click, mouse_just_click, mouse_just_released, self.on_grid, keys, keys_just_pressed)
            self.grid_component.handle_inputs(mouse_pos, mouse_click, mouse_just_click, mouse_just_released, self.on_grid, keys, keys_just_pressed, self.selected_tilenum)

    def run(self):
        while self.running:
            delta_time = self.clock.tick(60) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Input Management Methods
            self.handle_inputs()
            
            # Component Management Methods
            if self.on_menu:
                self._handle_menu_surface()
            else:
                self._handle_palette_surface()
                self._handle_grid_surface()
                self._handle_config_surface()

            pygame.display.update()

        pygame.quit()

class TileEditor_Config():
    def __init__(self, TILEMAP, font):
        self.TILEMAP = TILEMAP
        self.font = font

        self.config_width, self.config_height = 300, 768 // 2
        self.config_surface = pygame.Surface((self.config_width, self.config_height))
        self.config_surface_rect = self.config_surface.get_frect(topleft = (1024, 768 / 2))

        # Images
        self.save_btn_image = pygame.image.load('assets/save_btn.png').convert_alpha()
        self.save_btn_rect = self.save_btn_image.get_frect(topleft = (20,self.config_height - 40))
        self.create_btn_image = pygame.image.load('assets/create_btn.png').convert_alpha()
        self.create_btn_rect = self.create_btn_image.get_frect(topleft = (110,self.config_height - 40))
        self.load_btn_image = pygame.image.load('assets/load_btn.png').convert_alpha()
        self.load_btn_rect = self.load_btn_image.get_frect(topleft = (220,self.config_height - 40))

        # Config Flags
        self.draw_once = True

    def _handle_config_interactions(self, mouse_pos, mouse_just_click):
        # Convert mouse pos to the local screen 
        local_mouse_pos = (mouse_pos[0] - self.config_surface_rect.left, 
                           mouse_pos[1] - self.config_surface_rect.top)
        
        if self.save_btn_rect.collidepoint(local_mouse_pos) and mouse_just_click[0]:
            print('on save')
        elif self.load_btn_rect.collidepoint(local_mouse_pos) and mouse_just_click[0]:
            print('on load')
        elif self.create_btn_rect.collidepoint(local_mouse_pos) and mouse_just_click[0]:
            print('on create')
    
    def _config_file_mode(self):
        txt_gap = 20

        for i,data in enumerate(self.TILEMAP['metadata'].values()):
            txt_surface = self.font.render(str(data), True, (255,255,255))
            self.config_surface.blit(txt_surface, (20, i * txt_gap + 20))

        self.config_surface.blit(self.save_btn_image, (self.save_btn_rect))
        self.config_surface.blit(self.create_btn_image, (self.create_btn_rect))
        self.config_surface.blit(self.load_btn_image, (self.load_btn_rect))    

    def render(self):
        pygame.draw.rect(self.config_surface, (80,79,79), (0,0, self.config_width, self.config_height), 1)
        row_gap = 60

        # Load File Mode
        if self.draw_once:
            self._config_file_mode()
            self.draw_once = False
    
    def handle_inputs(self, mouse_pos, mouse_click, mouse_just_click, mouse_just_released, mouse_on_grid, keys, keys_just_pressed):
        self._handle_config_interactions(mouse_pos, mouse_just_click)

    def get_surface(self):
        return self.config_surface
    
class TileEditor_Pallete():
    def __init__(self, images, image_lookup):
        # Handle Local Instance
        self.images = images
        self.image_lookup = image_lookup

        self.category_index = 0
        self.current_category = list(self.images.keys())[self.category_index]

        self.palette_width, self.palette_height = 300, (768 // 2)
        self.palette_surface = pygame.Surface((self.palette_width, self.palette_height))
        self.palette_surface_rect = self.palette_surface.get_frect(topleft = (1024,0))
        self.row_gap, self.col_gap = 75, 75
        self.max_rows = 3
        self.scroll_offset = 0
        self.max_scroll = 0

        self.selected_tilenum = None

    def _handle_pallete_interactions(self, mouse_pos, mouse_click):
        pallete_relative_pos = (mouse_pos[0] - 1024 + self.col_gap, mouse_pos[1])

        for image in self.images[self.current_category]:
            if image.rect.collidepoint(pallete_relative_pos) and mouse_click[0]:
                self.selected_tilenum = image.tile_number

    def render(self):
        pygame.draw.rect(self.palette_surface, (0,0,0), (0, 0, self.palette_width, self.palette_height))
        pygame.draw.rect(self.palette_surface, (80,79,79), (0, 0, self.palette_width, self.palette_height), 1)
        
        # Calculate total number of tiles and rows needed
        total_tiles = len(self.images[self.current_category])
        total_rows = math.ceil(total_tiles / self.max_rows)
        screen_offset_pos = self.palette_height - self.palette_width # Offset from original display screen
        
        # Calculate the maximum scroll value based on content height
        self.max_scroll = max(0, (total_rows * self.row_gap) - self.palette_height + 20)

        for i, image in enumerate(self.images[self.current_category]):
            col = i % self.max_rows
            row = i // self.max_rows
            
            x = screen_offset_pos + (self.col_gap * col) + 40
            y = (self.row_gap * row) + 20 - self.scroll_offset
            
            # Only draw tiles that are within the viewport
            if 0 <= y < self.palette_height + self.row_gap:
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

    def handle_inputs(self, mouse_pos, mouse_click, mouse_just_click, mouse_just_released, mouse_on_grid, keys, keys_just_pressed):
        self._handle_pallete_interactions(mouse_pos, mouse_click)
        if keys_just_pressed[pygame.K_LEFTBRACKET]:
            self.scroll_offset = 0
            self.category_index = (self.category_index - 1) % len(self.images)
            self.current_category = list(self.images.keys())[self.category_index]
        elif keys_just_pressed[pygame.K_RIGHTBRACKET]:
            self.scroll_offset = 0
            self.category_index = (self.category_index + 1) % len(self.images)
            self.current_category = list(self.images.keys())[self.category_index]
        elif keys_just_pressed[pygame.K_n]:  # Scroll up
            self.scroll_offset = max(0, self.scroll_offset - 20)
        elif keys_just_pressed[pygame.K_m]:  # Scroll down
            self.scroll_offset = min(self.max_scroll, self.scroll_offset + 20)

    def get_selected_tilenum(self):
        return self.selected_tilenum

    def get_surface(self):
        return self.palette_surface

class TileEditor_Grid():
    def __init__(self, tilemap, tile_handler, tile_manager):
        """
            CLASS FUNCTION:

        """
        # World Surface Variables
        self.world_width = None
        self.world_height = None
        self.world_tilesize = None

        # This is a processed variable that is passed upon this function
        self.TILEMAP = self._handle_tilemap(tilemap)
        self.TILE_HANDLER = tile_handler
        self.TILE_MANAGER = tile_manager

        self.world_surface = pygame.Surface((self.world_width, self.world_height))
        self.world_surface_rect = self.world_surface.get_frect(topleft=(0,0))
        # Grid Surface Variables
        self.grid_surface_width = 1024
        self.grid_surface_height = 768
        self.grid_surface = pygame.Surface((self.grid_surface_width, self.grid_surface_height))
        self.grid_surface_rect = self.grid_surface.get_frect(topleft=(0,0)) 
        self.grid_tile_width = self.grid_surface_width // self.world_tilesize if self.world_tilesize else None
        self.grid_tile_height = self.grid_surface_height // self.world_tilesize if self.world_tilesize else None

        # Zoom and Panning Variables
        self.zoom = 1 
        self.dragging = False
        self.start_drag_x, self.start_drag_y = 0,0
        self.start_camera_pos_x, self.start_camera_pos_y = 0,0
        self.camera = pygame.Vector2(0,0)

        # TODO: Define Used Color for this Class    
        self.IS_TILEMAP = False
        self.RENDER_REDRAW = True

    def _handle_tilemap(self, TILEMAP):
        """
            Function:
                Validate tilemap metadata and update class attributes if valid.

            Args:
                TILEMAP: Dict containing 'metadata' with world_width, world_height, 
                        and world_tilesize keys.

            Returns:
                dict: Valid TILEMAP if successful, None otherwise.
        """

        try:
            world_width = TILEMAP['metadata']['world_width']
            world_height = TILEMAP['metadata']['world_height']
            world_tilesize = TILEMAP['metadata']['world_tilesize']

            # If value are accessed, update the state variable
            self.world_width = world_width
            self.world_height = world_height
            self.world_tilesize = world_tilesize

            # Update State Variable that the function was succesful
            self.IS_TILEMAP = True

            print(f'Class Method Success\nProcessed:\nworld_width\nworld_height\nworld_tilesize.\nReturned tilemap') # DEBUG
            return TILEMAP
        except Exception as TILEMAP_ERROR:
            return None, print(f'\nClass method \"_handle_tilemap\" fails. Returns None.\nError Info: {TILEMAP_ERROR}')
    
    def _draw_world_grid(self):
        """
            FUNCTION:
                Draw World Grid

            RETURNS:
                None, no returned variable
        """
        
        for y in range(0, self.world_height, self.world_tilesize):
            for x in range(0, self.world_width, self.world_tilesize):
                pygame.draw.rect(self.world_surface, (80,79,79),(x, y, self.world_tilesize, self.world_tilesize),1)

    def _draw_world_tile(self):
        """
            FUNCTION:
                Draw Tile Images on the Grid

            RETURNS:
                None, no returned variable
        """
        for y, tiles in enumerate(self.TILEMAP['map']):
            for x, tile in enumerate(tiles):
                tile_num = int(tile)

                image = self.TILE_HANDLER.get_tile_by_number(tile_num, 'background')
                scaled_image = pygame.transform.scale(image.image, (self.world_tilesize, self.world_tilesize))
                self.world_surface.blit(scaled_image, (x * self.world_tilesize, y * self.world_tilesize))            

    def _handle_grid_interactions(self, mouse_pos, mouse_click, selected_tilenum):
        # Convert mouse position into world space, accounting for camera position and zoom
        world_x = (mouse_pos[0] + self.camera.x) / self.zoom 
        world_y = (mouse_pos[1] + self.camera.y) / self.zoom

        # Convert world position to grid indices
        grid_x = int(world_x // self.world_tilesize)
        grid_y = int(world_y // self.world_tilesize)

        # TODO: now how can we update the tilemap on the main class? YOU FUCKING FIND IT OUT.
        # Make sure grid coordinates are within bounds
        if 0 <= grid_x < len(self.TILEMAP['map'][0]) and 0 <= grid_y < len(self.TILEMAP['map']):
            if mouse_click[0] and selected_tilenum:
                self.TILEMAP['map'][grid_y][grid_x] = selected_tilenum
    
    def _handle_camera_panning(self, mouse_pos):
        delta_change_x = self.start_drag_x - mouse_pos[0]
        delta_change_y = self.start_drag_y - mouse_pos[1]

        self.camera.x = self.start_camera_pos_x + delta_change_x
        self.camera.y = self.start_camera_pos_y + delta_change_y
        
    def render(self):
        self.grid_surface.fill((0,0,0))

        self._draw_world_tile()
        self._draw_world_grid()
                
        # Adjust World Surface, this ensures zooming is handled and adjust world_surface
        scaled_world_surface = pygame.transform.scale(self.world_surface, (self.world_width * self.zoom,self.world_height * self.zoom))

        # Adjust world surface rect for panning. 
        self.world_surface_rect = -self.camera.x, -self.camera.y

        # Render the world surface on the grid surface.
        self.grid_surface.blit(scaled_world_surface, self.world_surface_rect)
    
    def handle_inputs(self, mouse_pos, mouse_click, mouse_just_click, mouse_just_released, mouse_on_grid, keys, keys_just_pressed, selected_tilenum):
        # Handle Mouse Clicks
        if mouse_just_click[2]:
            self.start_drag_x, self.start_drag_y = mouse_pos[0], mouse_pos[1]
            self.start_camera_pos_x, self.start_camera_pos_y = self.camera.x, self.camera.y
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEALL)
            self.dragging = True
        if mouse_just_released[2]:
            self.dragging = False
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        
        # Handle Grid Interactions
        if mouse_on_grid:
            self._handle_grid_interactions(mouse_pos, mouse_click, selected_tilenum)
            if self.dragging:
                self._handle_camera_panning(mouse_pos)
        
        if keys[pygame.K_q]:  # Zoom In
            self.zoom = min(2.0, self.zoom + 0.05)

        if keys[pygame.K_e]:  # Zoom Out
            self.zoom = max(0.5, self.zoom - 0.05)
    
    def get_surface(self):
        return self.grid_surface

class TileEditor_Menu():
    def __init__(self, TILEMAP_MANAGER):
        self.TILEMAP_MANAGER = TILEMAP_MANAGER

        # Menu Properties
        self.menu_width, self.menu_height = 1324, 768
        self.menu_surface = pygame.Surface((self.menu_width, self.menu_height))
        self.menu_surface_rect = self.menu_surface.get_frect(topleft = (0,0))
        self.menu_surface_color = (153,153,153)

        # Text Properties
        self.menu_screen_font = pygame.font.Font(None, 50)
        self.menu_font = pygame.font.Font(None, 15)

        # Button Instances
        self.BUTTON_new_map = Button(70,40,pygame.Vector2(self.menu_width / 2 - 50, self.menu_height / 2), 'New Map', (85,85,85))
        self.BUTTON_load_map = Button(70,40,pygame.Vector2(self.menu_width / 2 + 50, self.menu_height / 2), 'Load Map', (85,85,85))
        self.DIALOG_mapsettings = Dialog_MapSettings(self.menu_surface)

        self.dialog_on_screen = False
    
    def handle_inputs(self, mouse_pos, mouse_click, mouse_just_click, mouse_just_released, keys, keys_just_pressed):
        if self.dialog_on_screen:
            if not self.DIALOG_mapsettings.dialog_events(mouse_pos=mouse_pos,mouse_click=mouse_click, mouse_just_click=mouse_just_click, mouse_just_released=mouse_just_released, keys=keys, keys_just_pressed=keys_just_pressed):
                self.dialog_on_screen = False
        elif self.BUTTON_new_map.button_events(mouse_pos, mouse_just_click):
            self.handle_menu_interactions('new_map')
        elif self.BUTTON_load_map.button_events(mouse_pos, mouse_just_click):
            self.handle_menu_interactions('load_map')
        
    def handle_menu_interactions(self, interaction_type):
        if interaction_type == 'new_map':
            self.dialog_on_screen = True
            self.DIALOG_mapsettings.show_dialog()
        
        if interaction_type == 'load_map':
            print('Load Map')

    def render(self):
        pygame.draw.rect(self.menu_surface, self.menu_surface_color, self.menu_surface_rect)

        if self.dialog_on_screen:
            self.DIALOG_mapsettings.draw()
        else:
            info_text = self.menu_screen_font.render("No Project File",True, (255,255,255))
            info_text_rect = info_text.get_frect(center = (self.menu_width / 2,self.menu_height / 2 - 60))

            # Draw Button
            self.BUTTON_new_map.draw(self.menu_surface)
            self.BUTTON_load_map.draw(self.menu_surface)
            
            # Draw Info Text
            self.menu_surface.blit(info_text, info_text_rect)
        

    def get_surface(self):
        return self.menu_surface

class Button():
    def __init__(self, button_width:int = 200, button_height:int = 100, button_pos=pygame.Vector2(0,0), button_text:str = 'Button', button_color:tuple = (255,255,255)):
        self.button_width = button_width
        self.button_height = button_height
        self.button_surface = pygame.Surface((self.button_width, self.button_height))
        self.button_pos = button_pos
        self.button_color = button_color
        self.button_rect = self.button_surface.get_frect(center = self.button_pos)

        self.button_font = pygame.font.Font(None, 20)
        self.button_text = self.button_font.render(f'{button_text}', True, (255,255,255))
        self.button_text_rect = self.button_text.get_frect(center = self.button_rect.center)

    def draw(self, surface):
            # Draw the button rectangle
            pygame.draw.rect(surface, self.button_color, self.button_rect)
            
            # Blit the button text
            surface.blit(self.button_text, self.button_text_rect)
    
    def button_events(self, mouse_pos, mouse_just_click):
        if self.button_rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            if mouse_just_click[0]:
                return True
            
class Dialog_MapSettings():
    def __init__(self, draw_screen_surface, dialog_width:int=400, dialog_height:int=300):
        # Draw Surface Properties (The reference surface)
        self.draw_screen_surface = draw_screen_surface

        # Dialog Properties
        self.dialog_width = dialog_width
        self.dialog_height = dialog_height
        self.dialog_surface = pygame.Surface((self.dialog_width, self.dialog_height), pygame.SRCALPHA)
        self.dialog_pos = pygame.Vector2(
            (self.draw_screen_surface.get_width() - self.dialog_width) // 2,
            (self.draw_screen_surface.get_height() - self.dialog_height) // 2
        )
        self.dialog_surface_rect = self.dialog_surface.get_frect(topleft=self.dialog_pos)

        # Dialog Flag
        self.active = False
        self.result = None
        
        # Colors
        self.dialog_bg_color = (169,169,169)  # Added alpha for slight transparency
        self.title_color = (255, 255, 255)
        self.label_color = (255, 255, 255)
        self.input_textbox_bg_color = (85,85,85)
        self.input_active_color = (90, 90, 120)
        self.text_color = (255, 255, 255)
        self.button_color = (85,85,85)
        self.button_hover_color = (100, 100, 140)
        
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.label_font = pygame.font.SysFont('Arial', 18)
        self.input_font = pygame.font.SysFont('Arial', 16)
        
        # Input Text Box Properties
        self.input_textbox = [
            {"label": "Map Width:", 
                                "value": "50", 
                                "active": False, 
                                "rect": None},
            {"label": "Map Height:", 
                                "value": "30", 
                                "active": False, 
                                "rect": None},
            {"label": "Tile Size:", 
                                    "value": "32", 
                                    "active": False, 
                                    "rect": None},
            {"label": "World Name:", 
                                    "value": "MyWorld", 
                                    "active": False, 
                                    "rect": None}
        ]
        self.input_textbox_width = self.dialog_width - 200
        self.input_textbox_height = 30

        # Pre Render Input Text Box
        start_y = 60
        spacing = 50
        
        for i, input_textbox in enumerate(self.input_textbox):
            # Create rect directly with all parameters at once
            input_textbox["rect"] = pygame.Rect(
                150,  # x position
                start_y + i * spacing,  # y position
                self.input_textbox_width,
                self.input_textbox_height
            )
        
        # Pre Render Button
        self.BUTTON_ok = Button(100,35,pygame.Vector2(self.dialog_width - 200, self.dialog_height - 30), 'OK', self.button_color)
        self.BUTTON_cancel = Button(100,35,pygame.Vector2(self.dialog_width - 90, self.dialog_height - 30), 'CANCEL', self.button_color)
        
        # Track if we're currently editing text
        self.editing_text = False
        
        self._render_dialogbox_elements()
        
    def _render_dialogbox_elements(self):
        self.dialog_surface.fill((0, 0, 0, 0))  # Transparent
        
        # Draw dialog background
        pygame.draw.rect(self.dialog_surface, self.dialog_bg_color, (0, 0, self.dialog_width, self.dialog_height))
        
        # Draw title
        title = self.title_font.render("Map Settings", True, self.title_color)
        title_rect = title.get_frect(center = (self.dialog_width // 2, 30))
        self.dialog_surface.blit(title, title_rect)
        
        # Draw labels (static part)
        for input_text_box in self.input_textbox:
            label = self.label_font.render(input_text_box["label"], True, self.label_color)
            self.dialog_surface.blit(label, (20, input_text_box["rect"].y + 5))
        
        # Draw buttons (static part)
        self.BUTTON_ok.draw(self.dialog_surface)
        self.BUTTON_cancel.draw(self.dialog_surface)
    
    def show_dialog(self):
        """Show the dialog and reset its state"""
        self.active = True
        self.result = None
        for input_text_box in self.input_textbox:
            input_text_box["active"] = False
        self.editing_text = False
    
    def dialog_events(self, mouse_pos, mouse_click, mouse_just_click, mouse_just_released, keys, keys_just_pressed):
        if not self.active:
            return False
        
        # Adjust mouse position relative to dialog
        rel_mouse_pos = (mouse_pos[0] - self.dialog_pos.x, mouse_pos[1] - self.dialog_pos.y)
        
        # Check for clicks on input fields
        if mouse_just_click[0]:
            for input_text_box in self.input_textbox:
                if input_text_box["rect"].collidepoint(rel_mouse_pos):
                    # Deactivate all other inputs
                    for other_input_text_box in self.input_textbox:
                        other_input_text_box["active"] = False
                    input_text_box["active"] = True
                    self.editing_text = True
            
            if not any(input_textbox["rect"].collidepoint(rel_mouse_pos) for input_textbox in self.input_textbox):
                # Clicked outside - deactivate all inputs
                for input_text_box in self.input_textbox:
                    input_text_box["active"] = False
                self.editing_text = False
        
        # Check Button Clicks
        if self.BUTTON_ok.button_events(rel_mouse_pos,mouse_just_click):
            print('yes')
            self._on_ok()
        elif self.BUTTON_cancel.button_events(rel_mouse_pos, mouse_just_click):
            print('no')
            self._on_cancel()
        
        # Handle text input for active field
        active_input = next((input_text_box for input_text_box in self.input_textbox if input_text_box["active"]), None)
        if active_input:
            if keys_just_pressed[pygame.K_BACKSPACE]:
                active_input["value"] = active_input["value"][:-1]

            # Check for enter/escape
            if keys_just_pressed[pygame.K_RETURN]:
                self._on_ok()

            elif keys_just_pressed[pygame.K_ESCAPE]:
                self._on_cancel()
            
            # Handle regular text input
            for key in range(len(keys_just_pressed)):
                if keys_just_pressed[key] and key not in [pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                    # Get the unicode character if it's a text input key
                    if pygame.K_a <= key <= pygame.K_z:
                        char = chr(key)
                        if not keys[pygame.K_LSHIFT] and not keys[pygame.K_RSHIFT]:
                            char = char.lower()
                        active_input["value"] += char
                    elif key == pygame.K_SPACE:
                        active_input["value"] += " "
                    elif pygame.K_0 <= key <= pygame.K_9:
                        # Numbers
                        active_input["value"] += chr(key)
                    elif key in [pygame.K_MINUS, pygame.K_UNDERSCORE]:
                        active_input["value"] += "-" if not keys[pygame.K_LSHIFT] else "_"
        return True
    
    def _on_ok(self):
        try:
            self.result = {
                "width": int(self.input_textbox[0]["value"]),
                "height": int(self.input_textbox[1]["value"]),
                "tile_size": int(self.input_textbox[2]["value"]),
                "world_name": self.input_textbox[3]["value"]
            }
            self.active = False
            self.editing_text = False

            # TODO: return the result values upon tileeditor class so it should be the one handling the created map with the given values.

        except ValueError:
            # Handle invalid number input
            pass
    
    def _on_cancel(self):
        self.result = None
        self.active = False
        self.editing_text = False
    
    def draw(self):
        if not self.active:
            return
        
        # Create a copy of the pre-rendered dialog
        dialog_copy = self.dialog_surface.copy()
        
        # Draw dynamic elements (input boxes and text)
        for input_textbox in self.input_textbox:
            # Draw input box
            color = self.input_active_color if input_textbox["active"] else self.input_textbox_bg_color
            pygame.draw.rect(dialog_copy, color, input_textbox["rect"])
            pygame.draw.rect(dialog_copy, (120, 120, 150), input_textbox["rect"], 1)
            
            # Draw input text
            inputlabel_text = self.input_font.render(input_textbox["value"], True, self.text_color)
            inputlabel_text_rect = inputlabel_text.get_rect(x=input_textbox["rect"].x + 5, centery=input_textbox["rect"].centery)
            dialog_copy.blit(inputlabel_text, inputlabel_text_rect)
        
        # Blit the dialog to the screen
        self.draw_screen_surface.blit(dialog_copy, self.dialog_pos)
        
TileEditor().run()
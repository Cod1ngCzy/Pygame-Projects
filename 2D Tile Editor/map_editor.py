# Import Managers
from TileImageManager import *
from TileMapManager import *
from settings import *

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
        self.IMAGES = self.TILEIMAGE_HANDLER.get_image_object()
        self.IMAGE_LOOKUP = self.TILEIMAGE_HANDLER.get_image_lookup()
        
        # Load Tilemap from Tilemap Manager
        self.TILEMAP_INDEX = 0
        self.CACHE_TILEMAPS = self.TILEMAP_MANAGER._cache_tilemaps.keys()
        self.TILEMAP_KEYS = list(self.CACHE_TILEMAPS)[self.TILEMAP_INDEX]
        self.TILEMAP = None

        # === SCREEN COMPONENTS === #
        # Independent Screen Component #
        self.menu_component = TileEditor_Menu(self.TILEMAP_MANAGER, self.TILEMAP)
        self.menu_component_surface = self.menu_component.get_surface()
        self.menu_component_rect = self.menu_component_surface.get_frect(topleft = (0,0))
        self._reinitialize_components()
        # === SCREEN COMPONENTS === #

        # Flag Variables
        self.selected_tilenum = None
        self.on_pallete = False
        self.on_grid = False
        self.on_config = False
        self.load_map = False
        self.create_map = False

        # Isolated Flag
        self.on_menu = self.menu_component.DIALOG_STATE
    
    def _reinitialize_components(self):
        if self.TILEMAP is None:
            return
        
        # Grouped Screen Component #
        self.grid_component = TileEditor_Grid(self.TILEMAP,self.TILEIMAGE_HANDLER, self.TILEMAP_MANAGER)
        self.grid_component_surface = self.grid_component.get_surface() # TODO: Fix how tilemap is passed upon this function
        self.grid_component_rect = self.grid_component_surface.get_frect(topleft = (0,0))

        self.pallete_component = TileEditor_Pallete(self.IMAGES['background'], self.IMAGE_LOOKUP)
        self.pallete_component_surface = self.pallete_component.get_surface()
        self.pallete_component_rect = self.pallete_component_surface.get_frect(topleft = (1024,0))

        self.config_component = TileEditor_Config(self.TILEMAP, self.font)
        self.config_component_surface = self.config_component.get_surface()
        self.config_component_rect = self.config_component_surface.get_frect(topleft = (1024, 768 / 2))

    def _handle_menu_surface(self):
        # If Processed get tilemap
        if self.menu_component.DIALOG_MAP_CREATED:
            self.TILEMAP = self.menu_component.get_created_map()
            self._reinitialize_components()

        self.menu_component.render()
        # Handle Menu Updates
        # |--> This updates the menu state
        self.on_menu = self.menu_component.DIALOG_STATE

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
                self.TILEMAP_MANAGER.save_tilemap(self.TILEMAP)
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
        pygame.draw.rect(self.config_surface, (0,0,0), (0,0, self.config_width, self.config_height), 1)
        row_gap = 60

        # Load File Mode
        if self.draw_once:
            pygame.draw.rect(self.config_surface, (169,169,169), (0,0, self.config_width, self.config_height))
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
        pygame.draw.rect(self.palette_surface, (169,169,169), (0, 0, self.palette_width, self.palette_height))
        pygame.draw.rect(self.palette_surface, (0,0,0), (0, 0, self.palette_width, self.palette_height), 1)
        
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
        self.world_width = 0
        self.world_height = 0
        self.world_tilesize = 0

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
        self.grid_surface.fill((169,169,169))

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
    def __init__(self, TILEMAP_MANAGER, TILEMAP):
        self.TILEMAP_MANAGER = TILEMAP_MANAGER
        self.TILEMAP = TILEMAP

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
        self.DIALOG_mapconfig = Dialog_NewMap(self.TILEMAP_MANAGER, self.menu_surface)

        # Update States
        self.DIALOG_ONSCREEN = True
        self.DIALOG_STATE = True # True on first initialization
        self.DIALOG_INPUT_RESULT = None # Result Input from the Dialog
        self.DIALOG_MAP_CREATED = False
    
    def _handle_menu_interactions(self, interaction_type):
        if interaction_type == 'new_map':
            self._handle_new_map()
        
        if interaction_type == 'load_map':
            self._handle_load_map()

    def _handle_new_map(self):
        self.DIALOG_ONSCREEN = True
        self.DIALOG_mapconfig.show_dialog()

    def _handle_load_map(self):
        pass

    def _handle_map_creation(self):
         # Unpack Results
         map_width = self.DIALOG_INPUT_RESULT['width']
         map_height = self.DIALOG_INPUT_RESULT['height']
         map_tilesize = self.DIALOG_INPUT_RESULT['tile_size']
         map_name = self.DIALOG_INPUT_RESULT['world_name']

         self.TILEMAP_MANAGER.create_tilemap(map_width,map_height,map_tilesize,map_name)
         self.TILEMAP = self.TILEMAP_MANAGER.access_tilemap(map_name)

    def _handle_dialog_updates(self):
        self.DIALOG_MAP_CREATED = self.DIALOG_mapconfig.DIALOG_INPUT_PROCESSED
        self.DIALOG_INPUT_RESULT = self.DIALOG_mapconfig.DIALOG_INPUT_RESULT
    
    def handle_inputs(self, mouse_pos, mouse_click, mouse_just_click, mouse_just_released, keys, keys_just_pressed):
        if self.DIALOG_ONSCREEN:
            if not self.DIALOG_mapconfig.dialog_events(mouse_pos=mouse_pos,mouse_click=mouse_click, mouse_just_click=mouse_just_click, mouse_just_released=mouse_just_released, keys=keys, keys_just_pressed=keys_just_pressed):
                self.DIALOG_ONSCREEN = False
            if self.DIALOG_MAP_CREATED:
                self._handle_map_creation()
                # Reset State and DIALOG state
                self.DIALOG_ONSCREEN = False
                self.DIALOG_STATE = False
        elif self.BUTTON_new_map.button_events(mouse_pos, mouse_just_click):
            self._handle_menu_interactions('new_map')
        elif self.BUTTON_load_map.button_events(mouse_pos, mouse_just_click):
            self._handle_menu_interactions('load_map')

    def render(self):
        pygame.draw.rect(self.menu_surface, self.menu_surface_color, self.menu_surface_rect)

        # Get constant dialog updates
        self._handle_dialog_updates()

        if self.DIALOG_ONSCREEN:
            self.DIALOG_mapconfig.draw()
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
    
    def get_created_map(self):
        return self.TILEMAP

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
        
class Dialog_NewMap():
    def __init__(self,TILEMAP_MANAGER, ORIGIN_SCREEN_SURFACE, dialog_width:int=400, dialog_height:int=300):
        # Draw Surface Properties (The reference surface)
        self.ORIGIN_SCREEN_SURFACE = ORIGIN_SCREEN_SURFACE
        self.TILEMAP_MANAGER = TILEMAP_MANAGER
        # Get tilemap dimensions for proper referencing
        self.TILEMAP_INDEX = 1
        self.TILESIZE_INDEX = 0
        self.TILEMAP_DIMENSION = self.TILEMAP_MANAGER.tilemap_dimension
        self.TILEMAP_DIMENSION_KEYS = list(self.TILEMAP_DIMENSION.keys())[self.TILEMAP_INDEX]

        # Dialog Properties
        self.dialog_width = dialog_width
        self.dialog_height = dialog_height
        self.dialog_surface = pygame.Surface((self.dialog_width, self.dialog_height), pygame.SRCALPHA)
        self.dialog_pos = pygame.Vector2(
            (self.ORIGIN_SCREEN_SURFACE.get_width() - self.dialog_width) // 2,
            (self.ORIGIN_SCREEN_SURFACE.get_height() - self.dialog_height) // 2
        )
        self.dialog_surface_rect = self.dialog_surface.get_frect(topleft=self.dialog_pos)
        
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
        self.dialog_title_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.textbox_label_font = pygame.font.SysFont('Arial', 18)
        self.input_font = pygame.font.SysFont('Arial', 16)
        
        # Input Text Box Properties
        self.input_textbox = [
            {"label": "Map Dimension:", 
                                "value": f"{self.TILEMAP_DIMENSION[self.TILEMAP_DIMENSION_KEYS]['width']}", 
                                "active": False, 
                                "rect": None},
            {"label": "", 
                                "value": f"{self.TILEMAP_DIMENSION[self.TILEMAP_DIMENSION_KEYS]['height']}", 
                                "active": False, 
                                "rect": None},
            {"label": "Tile Size:", 
                                    "value": f"{self.TILEMAP_DIMENSION[self.TILEMAP_DIMENSION_KEYS]['tilesize'][self.TILESIZE_INDEX]}", 
                                    "active": False, 
                                    "rect": None},
            {"label": "World Name:", 
                                    "value": "MyWorld", 
                                    "active": False, 
                                    "rect": None}
        ]
        self.input_textbox_width = self.dialog_width - 190
        self.input_textbox_height = 30
            
        # Dialog States
        self.DIALOG_ACTIVE = False
        self.DIALOG_INPUT_RESULT = {}
        self.DIALOG_INPUT_PROCESSED = False
        
        # Pre render Button
        self.BUTTON_ok = Button(100,35,pygame.Vector2(self.dialog_width - 200, self.dialog_height - 30), 'OK', self.button_color)
        self.BUTTON_cancel = Button(100,35,pygame.Vector2(self.dialog_width - 90, self.dialog_height - 30), 'CANCEL', self.button_color)
        
        # Track if we're currently editing text
        self.editing_text = False

        self._cache_input_textbox()
        self._cache_dialogbox_elements()
    
    def _cache_input_textbox(self):
        # Initialize with the correct structure
        self.input_textbox = [
            {"label": "Map Dimension:", 
            "value": f"{self.TILEMAP_DIMENSION[self.TILEMAP_DIMENSION_KEYS]['width']}", 
            "active": False, 
            "rect": None},
            {"label": "", 
            "value": f"{self.TILEMAP_DIMENSION[self.TILEMAP_DIMENSION_KEYS]['height']}", 
            "active": False, 
            "rect": None},
            {"label": "Tile Size:", 
            "value": f"{self.TILEMAP_DIMENSION[self.TILEMAP_DIMENSION_KEYS]['tilesize'][self.TILESIZE_INDEX]}", 
            "active": False, 
            "rect": None},
            {"label": "World Name:", 
            "value": "MyWorld", 
            "active": False, 
            "rect": None}
        ]
        # Manual Placings
        rect_placement = [
            pygame.Rect(150, 60, self.input_textbox_width - 100, self.input_textbox_height),
            pygame.Rect(250, 60, self.input_textbox_width - 100, self.input_textbox_height),
            pygame.Rect(150, 120, self.input_textbox_width, self.input_textbox_height),
            pygame.Rect(150, 180, self.input_textbox_width, self.input_textbox_height),
        ]
        
        # Iterate to the list then assign it to their rect
        for i, input_textbox in enumerate(self.input_textbox):
            input_textbox["rect"] = rect_placement[i]

    def _cache_dialogbox_elements(self):
        # Draw dialog background
        pygame.draw.rect(self.dialog_surface, self.dialog_bg_color, (0, 0, self.dialog_width, self.dialog_height))
        
        # Draw title
        dialog_title = self.dialog_title_font.render("Map Settings", True, self.title_color)
        dialog_title_rect = dialog_title.get_frect(center = (self.dialog_width // 2, 30))
        self.dialog_surface.blit(dialog_title, dialog_title_rect) # Render Dialog Title
        
        # Draw input textbox label (static part)
        for input_text_box in self.input_textbox:
            label = self.textbox_label_font.render(input_text_box["label"], True, self.label_color)
            self.dialog_surface.blit(label, (20, input_text_box["rect"].y + 5))
        
        # Draw buttons (static part)
        self.BUTTON_ok.draw(self.dialog_surface)
        self.BUTTON_cancel.draw(self.dialog_surface)

    def _handle_textbox_state(self, mouse_just_click, rel_mouse_pos):
        # Check for clicks on input fields
        if mouse_just_click[0]:
            clicked_textbox = next((textbox for textbox in self.input_textbox
                                if textbox["rect"].collidepoint(rel_mouse_pos)), None)
                
            if clicked_textbox:
                # Deactive All Textboxes
                for textbox in self.input_textbox:
                    textbox["active"] = False
                # Active Clicked TextBox
                clicked_textbox["active"] = True
                self.editing_text = True
                if clicked_textbox['label'] == 'Tile Size:':
                    self.TILESIZE_INDEX = (self.TILESIZE_INDEX + 1) % len(self.TILEMAP_DIMENSION[self.TILEMAP_DIMENSION_KEYS]['tilesize'])
                    self._cache_input_textbox()
                if clicked_textbox['label'] == 'Map Dimension:' or clicked_textbox['label'] == '':
                    self.TILEMAP_INDEX = (self.TILEMAP_INDEX + 1) % len(self.TILEMAP_DIMENSION)
                    self.TILEMAP_DIMENSION_KEYS = list(self.TILEMAP_DIMENSION.keys())[self.TILEMAP_INDEX]
                    self.TILESIZE_INDEX = 0
                    self._cache_input_textbox()
            else:
                # Clicked outside - deactivate all
                for textbox in self.input_textbox:
                    textbox["active"] = False
                self.editing_text = False
         
    def _handle_text_input(self, keys, keys_just_pressed):
        # Handle text input for active field
        active_textbox = next((input_text_box for input_text_box in self.input_textbox if input_text_box["active"]), None)

        if active_textbox:
            # Clear Text Box Input by 1
            if keys_just_pressed[pygame.K_BACKSPACE]:
                active_textbox["value"] = active_textbox["value"][:-1]
            
            # Handle regular text input
            for key in range(len(keys_just_pressed)):
                if keys_just_pressed[key] and key not in [pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                    # Get the unicode character if it's a text input key
                    if pygame.K_a <= key <= pygame.K_z:
                        char = chr(key)
                        if not keys[pygame.K_LSHIFT] and not keys[pygame.K_RSHIFT]:
                            char = char.lower()
                        active_textbox["value"] += char
                    elif key == pygame.K_SPACE:
                        active_textbox["value"] += " "
                    elif pygame.K_0 <= key <= pygame.K_9:
                        # Numbers
                        active_textbox["value"] += chr(key)
                    elif key in [pygame.K_MINUS, pygame.K_UNDERSCORE]:
                        active_textbox["value"] += "-" if not keys[pygame.K_LSHIFT] else "_"
    
    def _on_ok(self):
        try:
            self.DIALOG_INPUT_RESULT = {
                "width": int(self.input_textbox[0]["value"]),
                "height": int(self.input_textbox[1]["value"]),
                "tile_size": int(self.input_textbox[2]["value"]),
                "world_name": self.input_textbox[3]["value"]
            }
            self.DIALOG_INPUT_PROCESSED = True
            self.DIALOG_ACTIVE = False
            self.editing_text = False

        except ValueError:
            # Handle invalid number input
            pass
    
    def _on_cancel(self):
        self.DIALOG_INPUT_RESULT = None
        self.DIALOG_ACTIVE = False
        self.editing_text = False
    
    def draw(self):
        if not self.DIALOG_ACTIVE:
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
        self.ORIGIN_SCREEN_SURFACE.blit(dialog_copy, self.dialog_pos)
    
    def show_dialog(self):
        self.DIALOG_ACTIVE = True
        self.DIALOG_INPUT_RESULT = {}
        for input_text_box in self.input_textbox:
            input_text_box["active"] = False
        self.editing_text = False
    
    def dialog_events(self, mouse_pos, mouse_click, mouse_just_click, mouse_just_released, keys, keys_just_pressed):
        if not self.DIALOG_ACTIVE:
            return False
        
        # Adjust mouse position relative to dialog
        rel_mouse_pos = (mouse_pos[0] - self.dialog_pos.x, mouse_pos[1] - self.dialog_pos.y)

        # Check Button Clicks
        if self.BUTTON_ok.button_events(rel_mouse_pos,mouse_just_click):
            self._on_ok()
        elif self.BUTTON_cancel.button_events(rel_mouse_pos, mouse_just_click):
            self._on_cancel()
        
        # Handle Active State of Textbox Fields
        self._handle_textbox_state(mouse_just_click, rel_mouse_pos)
        
        # Handle Text Inputs
        self._handle_text_input(keys, keys_just_pressed)

        return True


TileEditor().run()

from settings import *

class Button():
    def __init__(self, button_width:int = 200, button_height:int = 100, button_pos=pygame.Vector2(0,0), button_text:str = 'Button', button_color:tuple = (255,255,255)):
        self.button_width = button_width
        self.button_height = button_height
        self.button_surface = pygame.Surface((self.button_width, self.button_height))
        self.button_pos = button_pos
        self.button_color = button_color
        self.button_rect = self.button_surface.get_frect(topleft = (self.button_pos.x, self.button_pos.y))

        self.button_font = pygame.font.Font(None, 20)
        self.button_text = self.button_font.render(f'{button_text}', True, (255,255,255))
        self.button_text_rect = self.button_text.get_frect(center = self.button_rect.center)

    def draw(self, surface):
            # Draw the button rectangle
            pygame.draw.rect(surface, self.button_color, (self.button_pos.x,self.button_pos.y - 768, self.button_width,self.button_height),0,10)
            
            # Blit the button text
            surface.blit(self.button_text, (self.button_text_rect.centerx,self.button_text_rect.centery - 768))
    
    def button_events(self, mouse_pos, mouse_just_click):
        if self.button_rect.collidepoint(mouse_pos) and mouse_just_click[0]:
                return True
            
class LevelEditor(Game, TileMapManager):
    def __init__(self):
        super().__init__()
        self._SCREEN_WIDTH = 1024
        self._SCREEN_HEIGHT = 768
        self._SCREEN_OFFSET = 200 # For UI
        self._SCREEN_SURFACE = pygame.display.set_mode((self._SCREEN_WIDTH, self._SCREEN_HEIGHT + self._SCREEN_OFFSET))

        self.GRID_TILESIZE = 64
        self.GRID_WIDTH = self._SCREEN_WIDTH // self.GRID_TILESIZE
        self.GRID_HEIGHT = self._SCREEN_HEIGHT // self.GRID_TILESIZE
        self.TILEMAP = self._load_tilemap(os.path.join('assets','Levels','tilemap.json'))

        self.ui_surface = pygame.Surface((1024, self._SCREEN_OFFSET))
        self.ui_surface_rect = self.ui_surface.get_frect(topleft = (0,768))
        self.tile_images = self.handle_tile_image(os.path.join('assets', 'TileSet', '1 Tiles'))
        self.object_images = self.handle_tile_image(os.path.join('assets', 'TileSet', '2 Objects', '1 Shadow'))

        self.button_tiles_surface = Button(85,35,pygame.Vector2(900,920),'Tiles', (255,0,0))
        self.button_objects_surface = Button(85,35,pygame.Vector2(800,920),'Objects', (255,0,0))

        self.selected_tilenum = None
        self.object = False
        self.tile = True

    def _handle_game_grid(self):
        for col in range(len(self.TILEMAP['tile'])):
            for row in range(len(self.TILEMAP['tile'][0])):
                pygame.draw.rect(self._SCREEN_SURFACE, (255,255,255), (row * self.GRID_TILESIZE, col * self.GRID_TILESIZE, self.GRID_TILESIZE, self.GRID_TILESIZE), 1)

    def _handle_tile_image_draw(self):
        for row,tiles in enumerate(self.TILEMAP['tile']):
            for col,tile in enumerate(tiles):
                if tile > 0:
                    tile_surface = self.tile_images[tile].get('tile_surface')
                    tile_surface = pygame.transform.scale(tile_surface, (64,64))
                    self._SCREEN_SURFACE.blit(tile_surface, (col * 64, row * 64))

        for row,objects in enumerate(self.TILEMAP['object']):
            for col,object in enumerate(objects):
                if object > 0:
                    object_surface = self.object_images[object].get('tile_surface')
                    object_surface = pygame.transform.scale(object_surface, (64,64))
                    self._SCREEN_SURFACE.blit(object_surface, (col * 64, row * 64))
    
    def handle_tile_image(self, path):
        images = self._get_tile_images(path)
        tile_images = {}

        for i, (tile_name, tile_surface) in enumerate(images.items()):
            tile_images[i + 1] = {
                'tile_name': tile_name,
                'tile_surface': tile_surface,
                'tile_rect' : tile_surface.get_frect(topleft = (0,0))
            }

        return tile_images
    
    def _handle_tile_selection(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_just_pressed = pygame.mouse.get_just_pressed()

        if mouse_pos[1] > 768:
            if self.tile:
                for tile_num, tile in self.tile_images.items():
                    image_rect = tile.get('tile_rect')
                    if image_rect.collidepoint(mouse_pos) and mouse_just_pressed[0]:
                        self.selected_tilenum = tile_num
            if self.object:
                for object_num, object in self.object_images.items():
                    image_rect = object.get('tile_rect')
                    if image_rect.collidepoint(mouse_pos) and mouse_just_pressed[0]:
                        self.selected_tilenum = object_num
    
    def _handle_grid_selection(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_just_pressed = pygame.mouse.get_just_pressed()
        mouse_pressed = pygame.mouse.get_pressed()
        
        if mouse_pos[1] < 768 and mouse_pos[0] < 1024 and mouse_pos[0] >= 0 :
            grid_pos = (mouse_pos[0] // 64, mouse_pos[1] // 64)
            if mouse_pressed[0] and self.selected_tilenum and self.object:
                object_image = self.object_images[self.selected_tilenum].get('tile_surface')
                object_image = pygame.transform.scale(object_image, (64,64))
                self._SCREEN_SURFACE.blit(object_image, (grid_pos[0] * 64, grid_pos[1] * 64))
                self.TILEMAP['object'][grid_pos[1]][grid_pos[0]] = self.selected_tilenum
            if mouse_pressed[0] and self.selected_tilenum and self.tile:
                tile_image = self.tile_images[self.selected_tilenum].get('tile_surface')
                tile_image = pygame.transform.scale(tile_image, (64,64))
                self._SCREEN_SURFACE.blit(tile_image, (grid_pos[0] * 64, grid_pos[1] * 64))
                self.TILEMAP['tile'][grid_pos[1]][grid_pos[0]] = self.selected_tilenum

    def _handle_ui_selection(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_just_pressed = pygame.mouse.get_just_pressed()
        mouse_pressed = pygame.mouse.get_pressed()
        
        self.button_tiles_surface.draw(self.ui_surface)
        self.button_objects_surface.draw(self.ui_surface)

        if self.button_tiles_surface.button_events(mouse_pos,mouse_just_pressed):
            self.tile = True
            self.object = False
            self.selected_tilenum = 0
        elif self.button_objects_surface.button_events(mouse_pos,mouse_just_pressed):
            self.object = True
            self.tile = False
            self.selected_tilenum = 0
         
    def _draw_ui_surface(self):
        max_col = 30
        if self.tile:
            self.ui_surface.fill((0,0,0))
            for i, tile in self.tile_images.items():
                image = tile.get('tile_surface')
                col = (i - 1) % max_col
                row = (i - 1) // max_col
                x = col * (image.get_width() + 2)
                y = row * (image.get_height() + 5)
                tile['tile_rect'] = pygame.Rect(x,y + 768,image.get_width(),image.get_height())
                self.ui_surface.blit(image, (x, y))
        elif self.object:
            self.ui_surface.fill((0,0,0))
            for i, tile in self.object_images.items():
                image = tile.get('tile_surface')
                image = pygame.transform.scale(image, (32,32))
                col = (i - 1) % max_col
                row = (i - 1) // max_col
                x = col * (image.get_width() + 2)
                y = row * (image.get_height() + 5)
                tile['tile_rect'] = pygame.Rect(x,y + 768,image.get_width(),image.get_height())
                self.ui_surface.blit(image, (x, y))

    def run(self):
        while self._GAME_RUN:
            delta_time = self._GAME_CLOCK.tick() / 1000

            keys = pygame.key.get_just_pressed()

            if keys[pygame.K_s]:
                self._save_tilemap(os.path.join('assets','Levels','tilemap.json'), self.TILEMAP)

            self._SCREEN_SURFACE.fill((0,0,0))

            self._draw_ui_surface()
            self._handle_grid_selection()
            self._handle_tile_selection()
            self._handle_ui_selection()

            self._handle_game_events()
            self._handle_game_timer(delta_time)
            self._handle_game_grid()
            self._handle_tile_image_draw()

            self._SCREEN_SURFACE.blit(self.ui_surface, self.ui_surface_rect)

            pygame.display.update()

        pygame.quit

if __name__ == "__main__":
    Instance = LevelEditor()
    Instance.run()

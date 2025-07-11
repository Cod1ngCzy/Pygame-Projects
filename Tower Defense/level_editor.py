
from settings import *
from game import Game

class TileMapManager():
    def __init__(self):
        pass

    def _get_tile_images(self, base_path):
        images = {}

        for image in os.listdir(base_path):
            image_name = os.path.basename(image)
            images[image_name.rsplit('.')[0]] = pygame.image.load(os.path.join(base_path, image_name))

        return images
    
    def _create_tilemap(self, file_path):
        map_data = {
                'tilemap': {
                    'width' : 1024,
                    'height': 768,
                    'tilesize': 64
                },
                'tile': None,
                'object': None,
            }
        with open(file_path, 'w') as file:
            json.dump(map_data, file, indent=4)
    
    def _save_tilemap(self, file_path, tilemap):
        if os.path.exists(file_path):
            with open(file_path, 'w') as file:
                json.dump(tilemap, file, indent=4)

    def _load_tilemap(self, file_path):
        try:
            with open(file_path, 'r') as file:
                tilemap_data = json.load(file)
            return tilemap_data
        except:
            print(f'{file_path} does not exists')

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
        self.tile_images = self.handle_tile_image()
        self._draw_ui_surface()

        self.selected_tilenum = None

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
    
    def handle_tile_image(self):
        images = self._get_tile_images(os.path.join('assets', 'TileSet', '1 Tiles'))
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
            for tile_num, tile in self.tile_images.items():
                image_rect = tile.get('tile_rect')
                if image_rect.collidepoint(mouse_pos) and mouse_just_pressed[0]:
                    self.selected_tilenum = tile_num
    
    def _handle_grid_selection(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_just_pressed = pygame.mouse.get_just_pressed()
        mouse_pressed = pygame.mouse.get_pressed()

        if mouse_pos[1] < 768 and mouse_pos[0] < 1024 and mouse_pos[0] >= 0 :
            grid_pos = (mouse_pos[0] // 64, mouse_pos[1] // 64)
            if mouse_pressed[0] and self.selected_tilenum:
                tile_image = self.tile_images[self.selected_tilenum].get('tile_surface')
                tile_image = pygame.transform.scale(tile_image, (64,64))
                self._SCREEN_SURFACE.blit(tile_image, (grid_pos[0] * 64, grid_pos[1] * 64))
                self.TILEMAP['tile'][grid_pos[1]][grid_pos[0]] = self.selected_tilenum
    
    def _handle_ui_selection(self):
        pygame.draw.rect(self.ui_surface, (255,255,255), (900,120, 80,30),0,10)
        pygame.draw.rect(self.ui_surface, (255,255,255), (900,120, 80,30),0,10)
         
    def _draw_ui_surface(self):
        max_col = 30
        for i, tile in self.tile_images.items():
            image = tile.get('tile_surface')
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

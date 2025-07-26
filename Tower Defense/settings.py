import os, pygame, math, random, json
from enum import Enum

class Game():
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Tower Defense')
        self._SCREEN_WIDTH = 1024
        self._SCREEN_HEIGHT = 768
        self._SCREEN_SURFACE = pygame.display.set_mode((self._SCREEN_WIDTH, self._SCREEN_HEIGHT))
        self._SCREEN_FILLCOLOR = (50,50,50)

        # Game Clock
        self._GAME_CLOCK = pygame.time.Clock()
        self._GAME_TIMER = 0

        # Running Flag
        self._GAME_RUN = True
    
    def _handle_game_timer(self, delta_time):
        self._GAME_TIMER += delta_time * 1000
    
    def _handle_game_events(self, keys=None):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._GAME_RUN = False

class GameState(Enum):
    MAIN_MENU = "menu"
    GAME_PLAY = "playing"
    GAME_OVER = "paused"
    GAME_PAUSED = "game_over"

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



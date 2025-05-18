from settings import *
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
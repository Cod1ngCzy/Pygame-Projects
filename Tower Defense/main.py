from settings import *
from archer import ArcherTower
from enemy import Enemy

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

        # Running Flag
        self._GAME_RUN = True

        # Create Tower Instance
        self.TOWER_archer = ArcherTower(pygame.Vector2(0,1))
        self.TOWER_SPRITE_GROUP = pygame.sprite.Group()
        self.TOWER_SPRITE_GROUP.add(self.TOWER_archer)
        
        self.ENEMY_slime = Enemy()
        self.ENEMY_SPRITE_GROUP = pygame.sprite.Group()
        self.ENEMY_SPRITE_GROUP.add(self.ENEMY_slime)

        # Grid Properties
        self.GRID_TILESIZE = 64
        self.GRID_WIDTH = self._SCREEN_WIDTH // self.GRID_TILESIZE
        self.GRID_HEIGHT = self._SCREEN_HEIGHT // self.GRID_TILESIZE
        self.TILEMAP = [[0 for _ in range(self.GRID_WIDTH)] for _ in range(self.GRID_HEIGHT)]
        self.TILEMAP_INIT = False

    def _handle_game_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._GAME_RUN = False
    
    def _handle_game_timer(self):
        pass

    def _handle_game_grid(self):
        for col in range(len(self.TILEMAP)):
            for row in range(len(self.TILEMAP[0])):
                pygame.draw.rect(self._SCREEN_SURFACE, (255,255,255), (row * self.GRID_TILESIZE, col * self.GRID_TILESIZE, self.GRID_TILESIZE, self.GRID_TILESIZE), 1)

    def run(self):
        while self._GAME_RUN:
            delta_time = self._GAME_CLOCK.tick() / 1000

            mouse_pos = pygame.mouse.get_pos()
            
            self._handle_game_events()

            # Clear the screen first
            self._SCREEN_SURFACE.fill(self._SCREEN_FILLCOLOR)
            self._handle_game_grid()

            self.TOWER_SPRITE_GROUP.update(delta_time, self._SCREEN_SURFACE, self.ENEMY_slime)
            self.TOWER_SPRITE_GROUP.draw(self._SCREEN_SURFACE)

            self.ENEMY_SPRITE_GROUP.update(delta_time, self._SCREEN_SURFACE)
            self.ENEMY_SPRITE_GROUP.draw(self._SCREEN_SURFACE)  
            # Update display once after all drawing is complete
            pygame.display.update()
        
        pygame.quit()

if __name__ == "__main__":
    GAME = Game()
    GAME.run()
from settings import *
from archer import ArcherTower
from enemy import Enemy
from card import Card, CardManager

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

        self.TOWER_SPRITE_GROUP = pygame.sprite.Group() 
        self.ENTITY_SPRITE_GROUP = pygame.sprite.Group()

        # Grid Properties
        self.GRID_TILESIZE = 64
        self.GRID_WIDTH = self._SCREEN_WIDTH // self.GRID_TILESIZE
        self.GRID_HEIGHT = self._SCREEN_HEIGHT // self.GRID_TILESIZE
        self.TILEMAP = [[0 for _ in range(self.GRID_WIDTH)] for _ in range(self.GRID_HEIGHT)]
        self.TILEMAP_INIT = False

        # Game Logic Properties
        self.WAVE = 0
        self.WAVE_START = False
        self.ENTITY_MAX_SPAWN = 2
        self.ENTITY_SPAWN_EVENT = pygame.event.custom_type()
        pygame.time.set_timer(self.ENTITY_SPAWN_EVENT, 1000)

        # Card Properties
        self.CARD_MANAGER = CardManager()
        self.CARD_TOWER = None

    def _handle_game_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._GAME_RUN = False
            if event.type == self.ENTITY_SPAWN_EVENT: 
                self._handle_entity_spawning()
        
    def _handle_game_timer(self, delta_time):
        self._GAME_TIMER += delta_time * 1000

    def _handle_game_grid(self):
        for col in range(len(self.TILEMAP)):
            for row in range(len(self.TILEMAP[0])):
                pygame.draw.rect(self._SCREEN_SURFACE, (255,255,255), (row * self.GRID_TILESIZE, col * self.GRID_TILESIZE, self.GRID_TILESIZE, self.GRID_TILESIZE), 1)
    
    def _handle_entity_spawning(self):
        if len(self.ENTITY_SPRITE_GROUP) <= self.ENTITY_MAX_SPAWN:
            ENTITY_slime = Enemy()
            self.ENTITY_SPRITE_GROUP.add(ENTITY_slime)

    def _handle_card_manager_updates(self, mouse_pos, mouse_just_clicked):
        if mouse_just_clicked[0]:
            if self.CARD_MANAGER.selected_card and self.CARD_TOWER is None:
                self.CARD_TOWER = ArcherTower(pygame.Vector2(0,0), True)
                self.TOWER_SPRITE_GROUP.add(self.CARD_TOWER)
            elif self.CARD_TOWER:
                self._handle_tower_placement(mouse_pos, mouse_just_clicked)

            return
        
        if self.CARD_MANAGER.card_consumed or self.CARD_MANAGER.card_returned:
            if self.CARD_TOWER:
                self.CARD_TOWER.kill()
                self.CARD_TOWER = None
        

        if self.CARD_TOWER:
            grid_pos = pygame.Vector2(
                mouse_pos[0] // 64,
                mouse_pos[1] // 64
            )

            self.CARD_TOWER.update_position(pygame.Vector2(grid_pos.x, grid_pos.y))

        self.CARD_MANAGER.reset_card_flags()
        return

    def _handle_tower_placement(self, mouse_pos, mouse_just_clicked):
        if self.CARD_MANAGER.selected_card and mouse_just_clicked[0]:
            grid_pos = pygame.Vector2(
                mouse_pos[0] // 64,
                mouse_pos[1] // 64
            )

            new_tower = ArcherTower(grid_pos, False)
            self.TOWER_SPRITE_GROUP.add(new_tower)
            self.CARD_MANAGER.consume_selected_card()
        
        return

    def run(self):
        while self._GAME_RUN:
            delta_time = self._GAME_CLOCK.tick() / 1000

            mouse_pos = pygame.mouse.get_pos()
            mouse_just_clicked = pygame.mouse.get_just_pressed()

            self._handle_game_timer(delta_time)
            self._handle_game_events()

            # Clear the screen first
            self._SCREEN_SURFACE.fill(self._SCREEN_FILLCOLOR)
            self._handle_game_grid()

            self.CARD_MANAGER.handle_deck(self._SCREEN_SURFACE, delta_time)
            self._handle_card_manager_updates(mouse_pos, mouse_just_clicked)

            self.TOWER_SPRITE_GROUP.update(delta_time, self._SCREEN_SURFACE, self.ENTITY_SPRITE_GROUP)
            self.TOWER_SPRITE_GROUP.draw(self._SCREEN_SURFACE)

            self.ENTITY_SPRITE_GROUP.update(delta_time, self._SCREEN_SURFACE)
            self.ENTITY_SPRITE_GROUP.draw(self._SCREEN_SURFACE)  
            # Update display once after all drawing is complete
            pygame.display.update()
        
        pygame.quit()

if __name__ == "__main__":
    GAME = Game()
    GAME.run()
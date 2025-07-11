from settings import *
from game import Game
from archer import ArcherTower
from enemy import Slime, EntitySpawner
from card import Card, CardManager
from gui import GUIManager

class TowerDefense(Game):
    def __init__(self):
        super().__init__()
        self.TOWER_SPRITE_GROUP = pygame.sprite.Group() 
        self.TOWER_ENTITIES = {}
        self.ENTITY_SPRITE_GROUP = pygame.sprite.Group()

        # Grid Properties
        self.GRID_TILESIZE = 64
        self.GRID_WIDTH = self._SCREEN_WIDTH // self.GRID_TILESIZE
        self.GRID_HEIGHT = self._SCREEN_HEIGHT // self.GRID_TILESIZE
        self.TILEMAP = [[0 for _ in range(self.GRID_WIDTH)] for _ in range(self.GRID_HEIGHT)]

        # Game Logic Properties
        self.ENTITY_SPAWNER = EntitySpawner(self.ENTITY_SPRITE_GROUP)

        # Card Properties
        self.CARD_MANAGER = CardManager()
        self.CARD_TOWER = None

        # GUI Properties
        self.GUI_MANAGER = GUIManager()

    def _handle_game_events(self, keys):
        super()._handle_game_events()
        
        if keys[pygame.K_s]:
            self.ENTITY_SPAWNER.start_wave()
        
        self.ENTITY_SPAWNER.handle_spawn_event()

    def _handle_game_grid(self):
        for col in range(len(self.TILEMAP)):
            for row in range(len(self.TILEMAP[0])):
                pygame.draw.rect(self._SCREEN_SURFACE, (255,255,255), (row * self.GRID_TILESIZE, col * self.GRID_TILESIZE, self.GRID_TILESIZE, self.GRID_TILESIZE), 1)

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
            self.TOWER_ENTITIES[f'CARD_TOWER{len(self.TOWER_ENTITIES)}'] = new_tower
            self.TOWER_SPRITE_GROUP.add(new_tower)
            self.CARD_MANAGER.consume_selected_card()
        
        return

    def run(self):
        while self._GAME_RUN:
            delta_time = self._GAME_CLOCK.tick() / 1000

            mouse_pos = pygame.mouse.get_pos()
            mouse_just_clicked = pygame.mouse.get_just_pressed()
            keys = pygame.key.get_pressed()

            self._handle_game_timer(delta_time)
            self._handle_game_events(keys)

            # Clear the screen first
            self._SCREEN_SURFACE.fill(self._SCREEN_FILLCOLOR)
            #self._handle_game_grid()

            self.CARD_MANAGER.handle_deck(self._SCREEN_SURFACE, delta_time)
            self._handle_card_manager_updates(mouse_pos, mouse_just_clicked)

            self.ENTITY_SPAWNER.update(delta_time, self._SCREEN_SURFACE)
            self.ENTITY_SPRITE_GROUP.update(delta_time, self._SCREEN_SURFACE)
            self.ENTITY_SPRITE_GROUP.draw(self._SCREEN_SURFACE)  

            self.TOWER_SPRITE_GROUP.update(delta_time, self._SCREEN_SURFACE, self.ENTITY_SPRITE_GROUP,mouse_pos,mouse_just_clicked)
            self.TOWER_SPRITE_GROUP.draw(self._SCREEN_SURFACE)

            self.GUI_MANAGER.handle_gui(self._SCREEN_SURFACE)
    
            # Update display once after all drawing is complete
            pygame.display.update()
        
        pygame.quit()

if __name__ == "__main__":
    GAME = TowerDefense()
    GAME.run()
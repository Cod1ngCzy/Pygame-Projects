from settings import *
import random

class Card(pygame.sprite.Sprite):
    def __init__(self,position=(0,0)):
        super().__init__()
        self.position = pygame.Vector2(position[0], position[1])
        self.deck_position = pygame.Vector2(position[0],position[1])

        self.image = self._load_card_image(f'ArcherTower.png')
        self.rect = self.image.get_frect(center=self.position)

        self.is_hover = False
        self.is_selected = False

    def _load_card_image(self, path_to_image):
        base_path = os.path.join('assets', 'card')
        full_path = os.path.join(base_path, path_to_image)
        card_image = pygame.image.load(full_path).convert_alpha()
        card_image = pygame.transform.scale(card_image, (128 + 50, 128 + 83))
        return card_image
    
    def _move_card(self, delta_time):
        self.position += (self.deck_position - self.position) * 0.1 * (delta_time * 50)
        self.rect.center = self.position
    
    def hover(self, mouse, delta_time):
        if self.rect.collidepoint(mouse):
            new_pos = pygame.Vector2(self.position.x,self.position.y - 100)
            self.position -= (self.position - new_pos) * 0.1 * (delta_time * 50)
            self.rect.center = self.position
            self.is_hover = True
        self.is_hover = False

    def update(self, delta_time, mouse):
        if not self.is_hover:
            self._move_card(delta_time)
        self.hover(mouse, delta_time)
        

class CardManager():
    def __init__(self):
        self.deck_width = 900
        self.deck_height = 150
        self.deck_surface = pygame.Surface((self.deck_width, self.deck_height), pygame.SRCALPHA)
        self.deck_surface_rect = self.deck_surface.get_frect(center=(1024 // 2, 700))
        
        self.deck_group = pygame.sprite.Group()
        self.max_cards = 5
        self.cards_spawned = 0
        self.card_spacing = 180  

        self.show_deck = True
        self.hide_deck = False

        self._spawn_cards()
    
    def _spawn_cards(self):
        for i in range(self.max_cards):
            start_pos = pygame.Vector2(
                self.deck_surface_rect.centerx,
                self.deck_surface_rect.centery - 60
            )
            
            card = Card(start_pos)
            self.deck_group.add(card)
            self.cards_spawned += 1
    
    def _show_cards(self):
        if not self.deck_group:
            return
            
        # Calculate total width needed for all cards
        total_width = (len(self.deck_group) * self.card_spacing)
        start_x = self.deck_surface_rect.centerx - (total_width / 2) + (self.card_spacing / 2)
        
        # Set target positions for each card
        for i, card in enumerate(self.deck_group):
            target_y = self.deck_surface_rect.centery - 60
            card.deck_position = pygame.Vector2(
                start_x + (i * self.card_spacing),
                target_y
            )
    
    def _hide_cards(self):
        if not self.deck_group:
            return
        
        for i, card in enumerate(self.deck_group):
            card.deck_position = pygame.Vector2(
                self.deck_surface_rect.centerx,
                self.deck_surface_rect.centery - 60
            )

    def draw(self, surface, delta_time):
        if self.show_deck:
            self._show_cards()
        elif self.hide_deck:
            self._hide_cards()

        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        if keys[pygame.K_r]:
            self.show_deck = False
            self.hide_deck = True
        
        # Draw cards
        self.deck_group.update(delta_time, mouse_pos)
        self.deck_group.draw(surface)
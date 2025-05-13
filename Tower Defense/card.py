from settings import *
import random

class Card(pygame.sprite.Sprite):
    def __init__(self,position=(0,0)):
        super().__init__()
        self.position = pygame.Vector2(position[0], position[1])
        self.deck_position = pygame.Vector2(position[0],position[1])

        self.original_image = self._load_card_image(f'ArcherTower.png')
        self.image = self.original_image.copy()
        self.rect = self.image.get_frect(center=self.position)

        self.is_hover = False
        self.is_selected = False
        self.move_speed = 5.0

    def _load_card_image(self, path_to_image):
        base_path = os.path.join('assets', 'card')
        full_path = os.path.join(base_path, path_to_image)
        card_image = pygame.image.load(full_path).convert_alpha()
        card_image = pygame.transform.scale(card_image, (128 + 50, 128 + 83))
        return card_image
    
    def _update_card_position(self, delta_time):
        clamp_factor = min(1.0, self.move_speed * delta_time)
        
        self.position.x += (self.deck_position.x - self.position.x) * clamp_factor
        self.position.y += (self.deck_position.y - self.position.y) * clamp_factor

        self.rect.center = self.position
    
    def _handle_hover(self, delta_time, mouse_pos):
        if self.rect.collidepoint(mouse_pos) and not self.is_hover:
            hover_position = pygame.Vector2(self.deck_position.x,self.deck_position.y - 200)
            clamp_factor = min(1.0, self.move_speed * delta_time)
            self.position -= (self.position - hover_position) * clamp_factor
            self.rect.center = self.position
            self.is_hover = True
        else:
            self.is_hover = False
 
    def _handle_selected(self, mouse_pos):
        if self.is_selected:
            self.position = pygame.Vector2(mouse_pos[0], mouse_pos[1])
            self.rect.center = self.position
    
    def set_selected(self, selected):
        if selected and not self.is_selected:
            self.is_selected = True
            self.image.set_alpha(50)
        elif not selected and self.is_selected:
            self.is_selected = False
            self.image.set_alpha(255)

    def update(self, delta_time, mouse_pos, mouse_just_clicked):
        self._handle_selected(mouse_pos)
        if not self.is_hover and not self.is_selected:
            self._update_card_position(delta_time)
        if not self.is_selected:
            self._handle_hover(delta_time, mouse_pos)
        
class CardManager():
    def __init__(self):
        self.deck_width = 900
        self.deck_height = 150
        self.deck_surface = pygame.Surface((self.deck_width, self.deck_height), pygame.SRCALPHA)
        self.deck_surface_rect = self.deck_surface.get_frect(center=(1024 // 2, 700))
        
        self.max_cards = 3
        self.cards_spawned = 0
        self.card_spacing = 140  
        self.card_consumed = False
        self.card_returned = False

        self.show_deck = True
        self.hide_deck = False

        self.deck_group = pygame.sprite.Group()
        self.selected_card = None

        self._spawn_cards()
    
    def _spawn_cards(self):
        start_pos = (self.deck_surface_rect.centerx, 
                    self.deck_surface_rect.centery - 60)
        
        for i in range(self.max_cards):
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
            target_y = self.deck_surface_rect.centery + 70
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
                self.deck_surface_rect.centery + 70
            )
        
    def _handle_selected_card(self, mouse_pos, mouse_just_clicked):
        if self.selected_card == None:
            for card in self.deck_group:
                if card.rect.collidepoint(mouse_pos) and mouse_just_clicked[0]:
                    self.selected_card = card
                    self.selected_card.set_selected(True)
                    return
                
        if mouse_just_clicked[2] and self.selected_card:
            self.return_selected_card()

        return

    def _handle_deck(self, surface, delta_time, mouse_pos, mouse_just_clicked):
        if self.show_deck:
            self._show_cards()
        elif self.hide_deck:
            self._hide_cards()
        
        self._handle_selected_card(mouse_pos, mouse_just_clicked)
        
        self.deck_group.update(delta_time, mouse_pos, mouse_just_clicked)
        self.deck_group.draw(surface)

    def get_selected_card(self):
        if self.selected_card:
            return self.selected_card
        return None
    
    def return_selected_card(self):
        if self.selected_card:
            self.selected_card.set_selected(False)
            self.selected_card = None
            self.card_returned = True
            return
        return None
    
    def consume_selected_card(self):
        if self.selected_card:
            self.selected_card.kill()
            self.selected_card.set_selected(False)
            self.selected_card = None
            self.card_consumed = True
            return
        return None

    def reset_card_flags(self):
        self.card_returned = False
        self.card_consumed = False
            
    def handle_deck(self, surface, delta_time):
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_just_clicked = pygame.mouse.get_just_pressed()

        if keys[pygame.K_r]:
            self.show_deck = False
            self.hide_deck = True
        
        self._handle_deck(surface, delta_time, mouse_pos, mouse_just_clicked)
    
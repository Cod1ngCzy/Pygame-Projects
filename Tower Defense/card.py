from settings import *

class Card(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(self)
        self.image = None
        self.rect = None
    
    def get_card(self, card_type):
        pass

class CardManager():
    def __init__(self):
        self.on_hand = []

        self.deck_surface = None
    
    def _handle_deck(self):
        pass

    def update(self):
        pass


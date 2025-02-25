from settings import *
from player import Player
from sprites import CollisionSprite
from random import randint

# Class
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Vampire Survivor')
        self.clock = pygame.time.Clock()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.running = True

        # Sprite Groups
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        # Instanciate Player
        self.player = Player((400,300), self.all_sprites, self.collision_sprites)

        # Sprites
        for i in range(6):
            x,y = randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)
            w,h = randint(0, 100), randint(50, 100)
            CollisionSprite((x,y),(w,h), (self.all_sprites, self.collision_sprites))

    def run(self):
        while self.running:
            # Clock Tick
            dt = self.clock.tick() / 1000

            # Event Handler
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            # Update
            self.all_sprites.update(dt)

            # Draw
            self.display_surface.fill('black')
            self.all_sprites.draw(self.display_surface)
            pygame.display.update()
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()

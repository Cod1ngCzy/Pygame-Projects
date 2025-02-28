# Game Loop
from settings import *
from sprites import *

class Game():
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Set up Display
        self.display_screen = pygame.display.set_mode((WIDTH,HEIGHT))
        pygame.display.set_caption("Pacman")

        # Set up Clock
        self.clock = pygame.time.Clock()

        # Running Flag
        self.running = True

        # Sprites
        self.all_sprites = pygame.sprite.Group()
        self.player = Player(self.all_sprites)
        pygame.key.set_repeat(500,100)


    def handle_events(self):
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
    
     
    def draw_grid(self):
         # x Loop to Draw Horizontal
         for x in range(0, WIDTH, TILE_SIZE):
              pygame.draw.line(self.display_screen, LIGHTGREY,(x,0), (x,HEIGHT))
         # y Loop to Draw Vertical
         for y in range(0, HEIGHT, TILE_SIZE):
              pygame.draw.line(self.display_screen, LIGHTGREY,(0,y), (WIDTH,y))
            

    def run(self):
        while self.running:
            # Delta Time
            dt = self.clock.tick(FPS) / 1000

            # Event Handler
            self.handle_events()
            
            # Fill Screen
            self.display_screen.fill('black')

            # Draw and Handle Sprites
            self.all_sprites.update()
            self.all_sprites.draw(self.display_screen)

            # Draw Grid
            self.draw_grid()

            # Render Display
            pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
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
        self.wall_objects = []

        # Check Grid Map
        self.pacman = Pacman(self.all_sprites, 1,1,self.wall_objects)

        pygame.key.set_repeat(500,100)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                mdx = round(mouse_x // TILE_SIZE)
                mdy = round(mouse_y // TILE_SIZE)

                #if pygame.mouse.get_just_pressed()[0]:
                #   GRID_MAP[mdy][mdx] = '1'
                #elif pygame.mouse.get_pressed()[2]:
                #   GRID_MAP[mdy][mdx] = '0'
                
             # Save on Key Press (e.g., Press 'S' to Save)
            #if event.type == pygame.KEYDOWN:
            #    if event.key == pygame.K_TAB:
            #       save_map()
        
    def draw_grid(self):
         # x Loop to Draw Horizontal
         #for x in range(0, WIDTH, TILE_SIZE):
         #     pygame.draw.line(self.display_screen, LIGHTGREY,(x,0), (x,HEIGHT))
         # y Loop to Draw Vertical
         #for y in range(0, HEIGHT, TILE_SIZE):
         #     pygame.draw.line(self.display_screen, LIGHTGREY,(0,y), (WIDTH,y))
         self.wall_objects = [ pygame.Rect(col_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            for row_index, row in enumerate(GRID_MAP)
            for col_index, cell in enumerate(row) if cell == '1']
         
         # Draw Walls
         for wall in self.wall_objects:
             pygame.draw.rect(self.display_screen, 'blue', wall,10)
            

    def run(self):
        while self.running:
            # Delta Time
            dt = self.clock.tick(FPS) / 1000

            # Event Handler
            self.handle_events()
            
            # Fill Screen
            self.display_screen.fill('black')

            # Draw and Handle Sprites
            self.all_sprites.update(dt, self.wall_objects)
            self.all_sprites.draw(self.display_screen)

            # Draw Grid
            self.draw_grid()

            # Render Display
            pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
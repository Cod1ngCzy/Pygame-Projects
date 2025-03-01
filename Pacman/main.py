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

        # Instantiate Pacman and Ghosts
        self.pacman = Pacman(self.all_sprites)
        self.ghosts = Ghosts(self.all_sprites)
        
        # Define walls and walkable paths from GRID_MAP
        self.wall_objects = [pygame.Rect(col_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            for row_index, row in enumerate(GRID_MAP)
            for col_index, cell in enumerate(row) if cell == '1']
        
        self.walk_path = [(int(col_index),int(row_index))
             for row_index, row in enumerate(GRID_MAP)
             for col_index, cell in enumerate(row) if cell == '0']
        
        # Create Grid Surface
        self.create_grid_surface()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                mdx = round(mouse_x // TILE_SIZE)
                mdy = round(mouse_y // TILE_SIZE)

                print(mdy,mdx)
                #if pygame.mouse.get_just_pressed()[0]:
                #   GRID_MAP[mdy][mdx] = '1'
                #elif pygame.mouse.get_pressed()[2]:
                #   GRID_MAP[mdy][mdx] = '0'
                
             # Save on Key Press (e.g., Press 'S' to Save)
            #if event.type == pygame.KEYDOWN:
            #    if event.key == pygame.K_TAB:
            #       save_map()
        
    def create_grid_surface(self):
        """Creates a pre-rendered grid surface to optimize performance."""
        self.grid_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.grid_surface.fill((0, 0, 0, 0))  # Transparent background

        # Draw Grid
        #for x in range(0, WIDTH, TILE_SIZE):
        #    pygame.draw.line(self.grid_surface, LIGHTGREY, (x, 0), (x, HEIGHT))
        #for y in range(0, HEIGHT, TILE_SIZE):
        #    pygame.draw.line(self.grid_surface, LIGHTGREY, (0, y), (WIDTH, y))

        # Draw Walls on Grid Surface
        for wall in self.wall_objects:
            pygame.draw.rect(self.grid_surface, 'blue', wall, 2)

            
    def run(self):
        while self.running:
            # Delta Time
            dt = self.clock.tick(FPS) / 1000

            # Event Handler
            self.handle_events()
            
            # Fill Screen
            self.display_screen.fill('black')

            # Blit Grid (pre-rendered for performance)
            self.display_screen.blit(self.grid_surface, (0, 0))

            # Draw and Handle Sprites
            self.all_sprites.update(dt, self.wall_objects, self.walk_path)
            self.all_sprites.draw(self.display_screen)
       
            # Render Display
            pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
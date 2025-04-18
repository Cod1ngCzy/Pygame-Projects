import pygame.gfxdraw
from settings import *
from libraries import *

# Game Class
class Game():
    def __init__(self):
        # Game Variables
        pygame.init()
        pygame.display.set_caption('Black Forest')
        self.display = DISPLAY
        self.clock = pygame.time.Clock()
        self.running = True  
        self.start_time = None  
        self.elapsed_time = None 

        # Camera
        self.camera_offset = pygame.Vector2()

        # Class Instance
        self.player = Observer(100, 100, 15, 15)  
        
        self.border_lines = self.create_screen_border()
        self.tiles = TILES
        self.light_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.dark_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    def handle_events(self):
        if self.start_time is None:
            self.start_time = pygame.time.get_ticks()
        self.elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False  
        
        keys = pygame.key.get_just_pressed()
        
        if keys[pygame.K_f]:
            self.player.show_ray_lines = not self.player.show_ray_lines

    def create_screen_border(self):
        border_lines = [
            # Top border
            Line(20, 20, WIDTH - 20, 20),  
            # Left border
            Line(20, 20, 20, HEIGHT - 20),  
            # Bottom border
            Line(20, HEIGHT - 20, WIDTH - 20, HEIGHT - 20),  
            # Right border
            Line(WIDTH - 20, HEIGHT - 20, WIDTH - 20, 20),  
        ]
        return border_lines
    
    def render(self, delta_time):
        # Render Tile Images
        self.tiles.load_map()

        # Create Surface
        self.light_surface.fill((0,0,0,0))
        self.dark_overlay.fill((0,0,0,225))

        self.player.update(delta_time, self.border_lines, self.light_surface)

        self.dark_overlay.blit(self.light_surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

        self.display.blit(self.dark_overlay, (0, 0))
    
    def run(self):
        while self.running:
            # Get the time difference (delta time) between frames (in seconds)
            delta_time = self.clock.tick(FPS) / 1000

            # Handle user input and game events
            self.handle_events()

            self.render(delta_time)

            # Render the updated frame
            pygame.display.update()

        # Quit pygame when the loop ends
        pygame.quit()

# Run the game when the script is executed directly
if __name__ == "__main__":
    game = Game()
    game.run()

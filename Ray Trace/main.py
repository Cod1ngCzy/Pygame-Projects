from settings import *
from libraries import *

class Game():
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Black Forest')
        self.display = DISPLAY
        self.clock = pygame.time.Clock()

        # Game Flags
        self.running = True
        
        # Game Time
        self.start_time = None
        self.elapsed_time = None

        # Classes 
        self.segment = Segment(0,0,100,100)
        self.player = Observer(100,100,15,15)

        # Game Variables
        self.border_lines = self.create_screen_border()

    def handle_events(self):
        # Record Game Time
        if self.start_time == None:
            self.start_time = pygame.time.get_ticks()
        self.elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000

        # Handle Game Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        
        keys = pygame.key.get_just_pressed()
        if keys[pygame.K_r]:
            self.player.show_ray_lines = not self.player.show_ray_lines
        elif keys[pygame.K_RIGHTBRACKET] and self.player.ray_length != 1000:
            self.player.ray_length += 100
        elif keys[pygame.K_LEFTBRACKET] and self.player.ray_length != 0:
            self.player.ray_length -= 100

    
    def create_screen_border(self):
        border_lines = [Line(20,20,WIDTH - 20,20),
                        Line(20,20,20,HEIGHT - 20),
                        Line(20,HEIGHT - 20,WIDTH - 20,HEIGHT - 20),
                        Line(WIDTH - 20, HEIGHT - 20,WIDTH - 20,20),
                        Line(200, 100, 200, 400),
                        Line(200, 400, 0, 400)
                        ]

        return border_lines
    
    def create_maze_path(self):
        pass
    
    def run(self):
        while self.running:
            delta_time = self.clock.tick(FPS) / 1000

            # Call Game Events
            self.handle_events()

            # Fill Screen
            self.display.fill('black')
            self.create_screen_border()
            
            # Instance Calls
            self.player.update(delta_time, self.border_lines)
            
            # Update Scren
            pygame.display.update()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()      
        
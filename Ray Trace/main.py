import pygame.gfxdraw
from settings import *
from libraries import *

# Game Class
class Game():
    def __init__(self):
        # Initialize pygame modules
        pygame.init()
        
        # Set the window title
        pygame.display.set_caption('Black Forest')
        
        # Create the display window from settings.py
        self.display = DISPLAY
        
        # Create a clock to control the frame rate
        self.clock = pygame.time.Clock()

        # Game Flags
        self.running = True  # Set to False to stop the game loop
        
        # Game Time
        self.start_time = None  # Will store the starting time of the game
        self.elapsed_time = None  # Will calculate the total elapsed game time

        # Create Game Objects
        # Segment and player are defined in libraries.py
        self.segment = Segment(0, 0, 100, 100)  # Create a segment at (0,0) with width and height of 100
        self.player = Observer(100, 100, 15, 15)  # Create a player at (100,100) with width and height of 15

        # Create screen border lines
        self.border_lines = self.create_screen_border()

    def handle_events(self):
        if self.start_time is None:
            self.start_time = pygame.time.get_ticks()
        self.elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000

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
        border_lines = [
            # Top border
            Line(20, 20, WIDTH - 20, 20),  
            # Left border
            Line(20, 20, 20, HEIGHT - 20),  
            # Bottom border
            Line(20, HEIGHT - 20, WIDTH - 20, HEIGHT - 20),  
            # Right border
            Line(WIDTH - 20, HEIGHT - 20, WIDTH - 20, 20),  
            # Additional obstacle (vertical line)
            Line(200, 100, 200, 400),
            # Additional obstacle (horizontal line)
            Line(200, 400, 0, 400)  
        ]
        return border_lines
    
    def run(self):
        """
        Main game loop:
        - Handles events
        - Updates game state
        - Renders objects to the screen
        - Maintains frame rate
        """
        while self.running:
            # Get the time difference (delta time) between frames (in seconds)
            delta_time = self.clock.tick(FPS) / 1000

            # Handle user input and game events
            self.handle_events()

            # Fill the screen with a dark gray color
            self.display.fill((10, 10, 10))

            # Draw the screen borders
            self.create_screen_border()
            
            # Update player and other game objects
            self.player.update(delta_time, self.border_lines)

            # Render the updated frame
            pygame.display.update()

        # Quit pygame when the loop ends
        pygame.quit()

# Run the game when the script is executed directly
if __name__ == "__main__":
    game = Game()
    game.run()

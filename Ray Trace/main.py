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
        self.game_time = None

        # Classes 
        self.segment = Segment(0,0,100,100)
        self.line = Line(100, 100, 100, 400)
        self.player = Observer(20,20,15,15)
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
    
    def run(self):
        while self.running:
            delta_time = self.clock.tick(FPS) / 1000

            # Call Game Events
            self.handle_events()

            # Fill Screen
            self.display.fill('grey')

            # Instance Calls
            self.player.update(delta_time, self.line)
            
            # Update Scren
            pygame.display.update()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()      
        
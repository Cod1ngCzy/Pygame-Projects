import pygame, sys, math, random

class Paddle:
    def __init__(self):
        self.width = 10
        self.height = 100
        self.position = pygame.Vector2((10,10))
        self.surface = pygame.Rect(self.position.x, self.position.y, self.width, self.height)
    
    def run(self, surface):
        self.handle_collision()
        pygame.draw.rect(surface,(255,255,255), (self.position.x, self.position.y, self.width, self.height))
        self.surface = pygame.Rect(self.position.x, self.position.y, self.width, self.height)
    
    def handle_collision(self):
        if self.position.y >= 690:
            self.position.y = 690
        elif self.position.y <= 10:
            self.position.y = 10
        
    def get_rect(self):
        return self.surface

class PongBall:
    def __init__(self, x, y, width, height, radius=10):
        self.position = pygame.Vector2(x, y)  
        self.surface = pygame.Rect(x, y, width, height) 
        self.radius = radius  
        self.velocity = pygame.Vector2(500, random.randint(-300,300))  
        self.color = 'red'  

        self.collided = False
    
    def move(self, dt):
        self.position += self.velocity * dt  # Apply movement
        
        # Sync the pygame Rect with the ball's position
        self.surface.center = (int(self.position.x), int(self.position.y))

    def collisions(self, paddle):
        if self.position.x + self.radius >= 800:  # Right wall collision
            self.position.x = 800 - self.radius # Prevent going outside
            self.velocity.x = -self.velocity.x   
            self.velocity.y += random.uniform(-300, 300)
        elif self.position.x - self.radius <= 0:  # Left wall collision
            self.collided = True
        elif self.position.y + self.radius >= 800:
            self.position.y = 800 - self.radius
            self.velocity.y = -self.position.y
        elif self.position.y - self.radius <= 0:
            self.position.y = 0 + self.radius
            self.velocity.y = -self.velocity.y
        
        if (self.position.x - self.radius <= paddle.position.x + paddle.width and
            self.position.y + self.radius >= paddle.position.y and 
            self.position.y - self.radius <= paddle.position.y + paddle.height):
            self.position.x = paddle.position.x + paddle.width + self.radius
            self.velocity.x = - self.velocity.x

    def run(self, surface, dt, paddle):
        self.move(dt)
        self.collisions(paddle)
    
        pygame.draw.circle(surface, self.color, (int(self.position.x), int(self.position.y)), self.radius)

class Game:
    def __init__(self):
        pygame.init()
        self.GAME_WIDTH = 800
        self.GAME_HEIGHT = 800
        self.GAME_DISPLAY = pygame.display.set_mode((self.GAME_WIDTH, self.GAME_HEIGHT))
        self.GAME_CLOCK = pygame.time.Clock()

        self.L_PADDLE = Paddle()
        self.L_PADDLE_DRAG_BOX = pygame.Rect(0,0, 400,800)
        self.L_PADDLE_DRAG = False
        self.PongBall = PongBall(self.GAME_WIDTH // 2, self.GAME_HEIGHT // 2, 10,10,10)

        self.GAME_RUNNING = True
    
    def handle_game_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.GAME_RUNNING = False
            if self.L_PADDLE_DRAG:
                mouse_pos = pygame.Vector2(10, pygame.mouse.get_pos()[1])
                self.L_PADDLE.position = mouse_pos
            if self.PongBall.collided:
                self.PongBall.position.x = self.L_PADDLE.position.x + 50
                self.PongBall.velocity = pygame.Vector2(500, 0)
                self.PongBall.collided = False
    
    def handle_input_events(self):
            if pygame.mouse.get_pressed()[0] and self.L_PADDLE_DRAG_BOX.collidepoint(pygame.mouse.get_pos()) :
                self.L_PADDLE_DRAG = True
            elif pygame.mouse.get_just_released()[0]:
                self.L_PADDLE_DRAG = False

    def run(self):
        while self.GAME_RUNNING:
            dt = self.GAME_CLOCK.tick() / 1000

            self.GAME_DISPLAY.fill((0,0,0))
            pygame.draw.rect(self.GAME_DISPLAY, (255,255,255),(400,0, 5,800)) # Game Line

            self.handle_game_events()
            self.handle_input_events()

            self.L_PADDLE.run(self.GAME_DISPLAY)
            self.PongBall.run(self.GAME_DISPLAY, dt, self.L_PADDLE)

            pygame.display.update()
        pygame.quit()

GAME = Game()
if __name__ == "__main__":
    GAME.run()
    

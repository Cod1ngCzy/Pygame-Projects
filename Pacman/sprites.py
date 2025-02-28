from settings import *

class Pacman(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image =  pygame.Surface((TILE_SIZE,TILE_SIZE))
        self.image.fill('yellow')
        self.rect = self.image.get_frect()
        self.pos = pygame.Vector2(0,0)
        self.direction = pygame.Vector2(0,0)
        self.speed = 5
        self.move_timer = 0
    
    def input_movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.direction = pygame.Vector2(1,0)
        elif keys[pygame.K_a]:
            self.direction = pygame.Vector2(-1,0)
        elif keys[pygame.K_w]:
            self.direction = pygame.Vector2(0,-1)
        elif keys[pygame.K_s]:
            self.direction = pygame.Vector2(0,1)
            
    def grid_boundary_collision(self):
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.pos.x = WIDTH / TILE_SIZE
        if self.rect.left < 0:
            self.rect.left = 0
            self.pos.x = 0
        if self.rect.top < 0:
            self.rect.top = 0
            self.pos.y = 0 
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.pos.y = HEIGHT / TILE_SIZE

    def update(self, dt):
        self.input_movement()
        self.move_timer += dt

        if self.move_timer >= 1 / self.speed:
            self.move_timer = 0

            self.pos += self.direction
            self.rect.x = self.pos.x * TILE_SIZE 
            self.rect.y = self.pos.y * TILE_SIZE

            self.grid_boundary_collision()

        
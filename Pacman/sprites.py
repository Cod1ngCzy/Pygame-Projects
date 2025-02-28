from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image =  pygame.Surface((TILE_SIZE,TILE_SIZE))
        self.image.fill('yellow')
        self.rect = self.image.get_frect()
        self.pos = pygame.Vector2(0,0)
    
    def move(self):
        # Get Input for Directional Movement
        keys = pygame.key.get_just_pressed()
        self.pos.x = (keys[pygame.K_d] - keys[pygame.K_a])
        self.pos.y = (keys[pygame.K_s] - keys[pygame.K_w])
        print(self.rect.center)
    
    def grid_boundary_collision(self):
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def update(self, *args, **kwargs):
        # Movement Application
        self.move()
        self.grid_boundary_collision()
        self.rect.x += self.pos.x * TILE_SIZE
        self.rect.y += self.pos.y * TILE_SIZE
     
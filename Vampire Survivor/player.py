from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos,groups,collision_sprites):
        super().__init__(groups)
        self.image = pygame.image.load(join('assets/images/player/down', '0.png')).convert_alpha()
        self.rect = self.image.get_frect(center = pos)
        self.direction = pygame.Vector2(0,0)
        self.speed = 500
        self.collision_sprite = collision_sprites
    
    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a]) 
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w]) 
        self.direction = self.direction.normalize() if self.direction else self.direction

    def move(self,dt):
        self.rect.x += self.direction.x * self.speed * dt
        self.collision('Horizontal')
        self.rect.y += self.direction.y * self.speed * dt
        self.collision('Vertical')
    
    def collision(self, direction):
        for sprite in self.collision_sprite:
            if sprite.rect.colliderect(self.rect):
                if direction == 'Horizontal':
                    if self.direction.x > 0: self.rect.right = sprite.rect.left
                    if self.direction.x < 0: self.rect.left = sprite.rect.right

    def update(self, dt):
        self.input()
        self.move(dt)

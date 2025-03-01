from settings import *

class Character(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.image =  pygame.Surface((TILE_SIZE,TILE_SIZE))
        self.image.fill('yellow')
        self.rect = self.image.get_frect()
        self.pos = pygame.Vector2(1,1)
        self.direction = pygame.Vector2(0,0)
        self.speed = 5
        self.move_timer = 0
    
    def wall_collisions(self, walls):
        for wall in walls:
            if self.rect.colliderect(wall):
                if self.direction.x > 0:
                    self.rect.right = wall.left
                    self.pos.x = self.rect.x / TILE_SIZE
                elif self.direction.x < 0:
                    self.rect.left = wall.right
                    self.pos.x = self.rect.x / TILE_SIZE
                if self.direction.y > 0:  # Moving down
                    self.rect.bottom = wall.top
                    self.pos.y = self.rect.y / TILE_SIZE
                elif self.direction.y < 0:  # Moving up
                    self.rect.top = wall.bottom
                    self.pos.y = self.rect.y / TILE_SIZE
    
    def update(self, dt, walls, paths):
        self.move_timer += dt
        
        if self.move_timer >= 1 / self.speed:
            self.move_timer = 0
            self.pos += self.direction  # Move based on direction
            self.rect.topleft = self.pos * TILE_SIZE  # Update position

        self.wall_collisions(walls)

class Pacman(Character):
    def __init__(self, groups):
        super().__init__(groups)
        self.pos = pygame.Vector2(1,1)

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
            
    def update(self, dt, walls, paths):
        self.input_movement()
        super().update(dt, walls, paths)  # Call parent update method
  

class Ghosts(Character):
    def __init__(self, groups):
        super().__init__(groups)
        self.pos = pygame.Vector2(6,8)
        self.image.fill('orange')
    
    def update(self, dt, walls, paths):
        super().update(dt, walls, paths)  # Call parent update method
  
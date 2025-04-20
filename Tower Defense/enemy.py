from settings import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.ENEMY_walk_frame = self._get_image_tileset(os.path.join('assets', 'Enemy', 'slime','down_walk')) 
        self.ENEMY_death_frame = self._get_image_tileset(os.path.join('assets', 'Enemy', 'slime','death')) 

        self.animation_speed = 5
        self.animation_index_Walk = 0
        self.animation_index_Death = 0
        
        self.position = pygame.Vector2(100,200)
        self.image = self.ENEMY_walk_frame[self.animation_index_Walk]
        self.rect = self.image.get_frect(center = (self.position))

        self.mask = pygame.mask.from_surface(self.image)
        self.mask_surface = self.mask.to_surface()
        self.mask_surface.set_colorkey((0,0,0))

        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 0.15
        self.hit_flash_color = (255,0,0)

        self.speed = 100
        self.health = 100

    def _get_image_tileset(self, path_to_image):
        sprite_image_paths = os.listdir(path_to_image)
        sprite_images = [pygame.image.load(os.path.join(path_to_image,sprite)) for sprite in sprite_image_paths]
        return sprite_images

    def _handle_animation_walk(self, delta_time):
        self.animation_index_Walk += self.animation_speed * delta_time

        self.animation_index_Walk %= len(self.ENEMY_walk_frame)

        self.image = self.ENEMY_walk_frame[int(self.animation_index_Walk)]
        self.mask = pygame.mask.from_surface(self.image)
        self.mask_surface = self.mask.to_surface()
        self.mask_surface.set_colorkey((0,0,0))

        if int(self.animation_index_Walk) >= 2 and int(self.animation_index_Walk) <= 4:
            self.position.x += self.speed * delta_time

            self.rect.center = self.position
    
    def _handle_animation_death(self, delta_time):
        self.animation_index_Death += 5 * delta_time
        self.animation_index_Death %= len(self.ENEMY_death_frame)

        self.image = self.ENEMY_death_frame[int(self.animation_index_Death)]
        
        if int(self.animation_index_Death) >= len(self.ENEMY_death_frame) - 1:
            self.kill()
    
    def _handle_damage_animation(self, delta_time):
        self.hit_timer += delta_time
        if self.hit_timer >= self.hit_duration:
            self.is_hit = False
        
        hit_image = self.image.copy()
        mask_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        mask_surface.fill((0, 0, 0, 0))  # Transparent
        
        # Get mask and convert to surface with color
        mask_pixels = pygame.mask.from_surface(hit_image)
        mask_outline = mask_pixels.to_surface(setcolor=(255, 0, 0, 128), unsetcolor=(0, 0, 0, 0))
        
        # Apply the colored mask to our image
        hit_image.blit(mask_outline, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        self.image = hit_image

    def take_damage(self, damage):
        self.health -= damage
        self.is_hit = True
        self.hit_timer = 0

    def update(self, delta_time, screen_surface):
        if self.health <= 0:
            self._handle_animation_death(delta_time)
        else:
            self._handle_animation_walk(delta_time)

        if self.is_hit:
            self._handle_damage_animation(delta_time)

        # Get Slime Rect
        pygame.draw.rect(screen_surface, (255,255,255), self.rect, 1)
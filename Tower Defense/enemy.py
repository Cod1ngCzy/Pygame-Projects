from settings import *

class Entity(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.position = pygame.Vector2(0,0)
        self.image = None
        self.rect = None

        self.mask = pygame.mask.from_surface(self.image) if self.image else None
        self.mask_surface = self.mask.to_surface(self.image) if self.mask else None
        self.mask_surface.set_colorkey((0,0,0)) if self.mask_surface else None

        self.animation_speed = 5
        self.animation_index = 0
        self.animation_frames = {}
        self.animation_state = None
    
    def _load_animation_frames(self, base_path):
        sprite_images = []
        sprite_image_directory = os.listdir(os.path.join(base_path))

        for image in sprite_image_directory:
            image_surface = pygame.image.load(os.path.join(base_path, image))
            sprite_images.append(image_surface)
        
        return sprite_images

    def _handle_sprite_animation(self, delta_time):
        self.animation_index += self.animation_speed * delta_time
        self.animation_index %= len(self.animation_frames[self.animation_state])
        self.image = self._get_animation_frame()
    
    def _get_animation_frame(self, new_state=None):
        if new_state is None:
            return self.animation_frames[self.animation_state][int(self.animation_index)]

class EntitySpawner(Entity):
    def __init__(self, entity_group):

        self.animation_speed = 5
        self.animation_index = 0
        self.animation_state = 'invi'
        self.animation_frames = {
            'static': self._load_animation_frames(os.path.join('assets', 'ParticleEffect', 'Portal', 'Static')),
            'open': self._load_animation_frames(os.path.join('assets', 'ParticleEffect', 'Portal', 'Open')),
            'close': self._load_animation_frames(os.path.join('assets', 'ParticleEffect', 'Portal', 'Close')),
            'invi' : [pygame.Surface((64,64), pygame.SRCALPHA)]
        }

        self.image = self.animation_frames['static'][int(self.animation_index)]
        self.rect = self.image.get_frect(topleft = (0 * 64,5 * 64))

        self.spawn_position = self.rect.center

        self.last_time_since_spawn = 0
        self.last_time_since_duration = 0
        self.spawn_cooldown = 2000
        self.spawn_duration = 10000
        self.spawn_start_time = None
        self.entity = 0
        self.entity_Group = entity_group
        self.max_entity = 5

        self.spawn_end = True

    def _handle_sprite_animation(self, delta_time):
        self._handle_animation_states()

        super()._handle_sprite_animation(delta_time)
    
    def _get_animation_frame(self, new_state=None):
        super()._get_animation_frame()
        
        if new_state in self.animation_frames and new_state != self.animation_state:
            self.animation_state = new_state
            self.animation_index = 0

        return self.animation_frames[self.animation_state][int(self.animation_index)]
        
    def _handle_animation_states(self):
        if self.animation_state == 'open':
            if int(self.animation_index) >= len(self.animation_frames['open']) - 1:
                self.image = self._get_animation_frame('static')
        elif self.animation_state == 'close':
            if int(self.animation_index) >= len(self.animation_frames['close']) - 1:
                self.image = self._get_animation_frame('invi')
        
    def handle_spawn_event(self):
        current_time = pygame.time.get_ticks()

        if self.spawn_end:
            return

        spawn_time = current_time - self.last_time_since_spawn
        spawn_end_time = (current_time - self.last_time_since_duration) 

        if spawn_time >= self.spawn_cooldown and not self.spawn_end:
            if self.entity < self.max_entity:
                self._generate_entity()
                self.last_time_since_spawn = current_time  # Reset spawn timer after entity is spawned
        
        if spawn_end_time >= self.spawn_duration:
            self.last_time_since_duration = current_time
            self.spawn_end = True
            self.image = self._get_animation_frame('close')
    
    def _generate_entity(self):
        Entity = Slime(self.spawn_position)
        self.entity_Group.add(Entity)
        self.entity += 1
    
    def start_wave(self):
        current_time = pygame.time.get_ticks()
        self.spawn_end = False
        self.last_time_since_spawn = current_time
        self.last_time_since_duration = current_time
        self.entity = 0
        self.image = self._get_animation_frame('open')

    def update(self, delta_time, screen_surface):
        self._handle_sprite_animation(delta_time)

        screen_surface.blit(self.image, self.rect)

class Slime(Entity):
    def __init__(self, position):
        super().__init__()

        self.animation_frames = {
            'walk' : self._load_animation_frames(os.path.join('assets', 'Enemy', 'slime', 'walk')),
            'death' : self._load_animation_frames(os.path.join('assets', 'Enemy', 'slime', 'death'))
        }
        self.animation_state = 'walk'

        self.position = pygame.Vector2(position)
        self.image = self.animation_frames[self.animation_state][self.animation_index]
        self.rect = self.image.get_frect(center = (self.position))

        self.hit_timer = 0
        self.hit_duration = 0.15
        self.hit_flash_color = (255,0,0)

        self.speed = 100
        self.health = 100

        self.is_hit = False
        self.is_alive = True
    
    def _handle_sprite_animation(self, delta_time):
        super()._handle_sprite_animation(delta_time)

        if self.animation_state == 'walk':
            if int(self.animation_index) >= 2 and int(self.animation_index) <= 4:
                self.position.x += self.speed * delta_time
                self.rect.center = self.position
        elif self.animation_state == 'death':
            if int(self.animation_index) >= len(self.animation_frames[self.animation_state]) - 1:
                self.kill()
        
        self._update_mask_surface()
    
    def _get_animation_frame(self, new_state=None):
        super()._get_animation_frame()

        if new_state in self.animation_frames and new_state != self.animation_state:
            self.animation_state = new_state
            self.animation_index = 0

        return self.animation_frames[self.animation_state][int(self.animation_index)]

    def _handle_entity_states(self):
        if self.health <= 0:
            self.is_alive = False
            self.animation_state = 'death'
    
    def _update_mask_surface(self):
        self.mask = pygame.mask.from_surface(self.image)
        self.mask_surface = self.mask.to_surface()
        self.mask_surface.set_colorkey((0,0,0))
    
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

    def get_entity_status(self, state=None):
        if state is None:
            return None
        elif state == 'is_alive':
            return self.is_alive
        
    def update(self, delta_time, screen_surface):
        self._handle_entity_states()
        self._handle_sprite_animation(delta_time)

        if self.is_hit:
            self._handle_damage_animation(delta_time)

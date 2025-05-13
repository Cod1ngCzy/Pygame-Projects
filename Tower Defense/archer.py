from settings import *

class Tower(pygame.sprite.Sprite):
    def __init__(self, position=pygame.Vector2(0, 0), preview_mode=False):
        super().__init__()

        self.animation_index = 0
        self.animation_speed = 10
        self.animation_state = None
        self.upgrade_level = 1
        self.max_upgrade_level = 6
        self.animation_frames = {}

        self.position = pygame.Vector2(position.x * 64 + 32, position.y * 64)
        self.image = None
        self.rect = None

        self.attack_radius = 150

        self.time_since_placed = 0
        self.upgrade_time = 0
        self.upgrade_time_threshold = 120000
        self.kill_count = 0

        self.show_rect = False
        self.show_radius = False
        self.preview_mode = preview_mode

    def _load_spritesheet_animations(self, base_path, prefix):
        animations = {}
        directory_length = len(os.listdir(os.path.join(base_path)))
        
        for level in range(1, directory_length + 1):
            path = f"{base_path}/{prefix}{level}"
            files = os.listdir(path)
            frames = []
            for file in sorted(files):
                img = pygame.image.load(os.path.join(path, file)).convert_alpha()
                img = pygame.transform.scale(img, (64, img.get_height()))
                frames.append(img)
            animations[level] = frames
        return animations

    def _create_radius_surface(self):
        self.attack_radius_surface = pygame.Surface((self.attack_radius*2, self.attack_radius*2), pygame.SRCALPHA)
        center_point = (self.attack_radius, self.attack_radius)
        pygame.draw.circle(self.attack_radius_surface, (255, 0, 0, 75), center_point, self.attack_radius)
        pygame.draw.circle(self.attack_radius_surface, (0, 0, 0, 255), center_point, self.attack_radius, 2)
        
        self.attack_radius_rect = self.attack_radius_surface.get_rect()

    def show_tower_radius(self, screen_surface):
        self.attack_radius_rect.center = self.rect.center
        screen_surface.blit(self.attack_radius_surface, (self.attack_radius_rect.x, self.attack_radius_rect.y + 30))

    def show_tower_rect(self, screen_surface):
        if self.show_rect:
            pygame.draw.rect(screen_surface, (255, 255, 255), self.rect, 1)

class ArcherTower(Tower):
    def __init__(self, position=pygame.Vector2(0, 0), preview_mode=False):
        super().__init__(position, preview_mode)

        self.animation_speed = 10
        self.animation_state = 'upgrade'
        self.animation_frames = {
            'idle': self._load_spritesheet_animations('assets/ArcherTower/IdleAnimation', 'idle'),
            'upgrade': self._load_spritesheet_animations('assets/ArcherTower/UpgradeAnimation', 'upgrade')
        }
        self._create_radius_surface()

        self.image = pygame.image.load(os.path.join('assets','ArcherTower', 'basetower.png'))
        self.rect = self.image.get_frect(center=self.position)
        self.anchor_rect = pygame.Rect(self.rect.x, self.rect.y + self.image.get_height() - 64, 64, 64)

        self.arrow_object_group = pygame.sprite.Group()
        self.arrow_cooldown = 1000  # milliseconds
        self.arrow_damage = 15
        self.arrow_speed = 250
        self.arrow_object_lastshot = 0
        self.arrow_multishot = False

        self.entity_list = []
        self.targeted_entity_object = None

    def _handle_animation(self, delta_time):
        self.animation_index += self.animation_speed * delta_time

        if self.animation_state == 'upgrade':
            frames = self.animation_frames['upgrade'][self.upgrade_level]
            if int(self.animation_index) >= len(frames):
                self._change_animation_state('idle')

        self.image = self._get_animation_frame()
    
    def _handle_tower_upgrade(self):
        if self.upgrade_level < self.max_upgrade_level:
            self.upgrade_level += 1
            self._change_animation_state('upgrade')
        
        match self.upgrade_level:
            case 2:
                self.arrow_damage = 15
                self.arrow_speed = 250
            case 3:
                self.arrow_damage = 15
                self.arrow_speed = 300
                self.attack_radius = 200
            case 4:
                self.arrow_damage = 20
                self.arrow_speed = 300
            case 5:
                self.arrow_damage = 20
                self.arrow_speed = 350
            case 6:
                self.arrow_damage = 25
                self.arrow_speed = 350
                self.attack_radius = 250
                self.arrow_multishot = True
        
        self._create_radius_surface()

    def _handle_internal_timer(self, delta_time):
        self.time_since_placed += delta_time * 1000
        self.upgrade_time += delta_time * 1000
        self.arrow_cooldown_timer = self.time_since_placed - self.arrow_object_lastshot

    def _handle_attack(self, delta_time, screen_surface, entity_object_group):
        self._handle_entity_targeting(entity_object_group) 

        if self.arrow_multishot:
            self._handle_multishot_attack()
        elif not self.arrow_multishot:
            self._handle_singleshot_attack()

        if self.arrow_object_group:
            self.arrow_object_group.update(delta_time)
            self.arrow_object_group.draw(screen_surface)
            for arrow in self.arrow_object_group:
                self._handle_arrow_status(arrow)
 
    def _handle_singleshot_attack(self):
        if self.arrow_cooldown_timer >= self.arrow_cooldown:
            self.create_arrow_object(self.targeted_entity_object)
    
    def _handle_multishot_attack(self):
        if not isinstance(self.targeted_entity_object, list):
            self._handle_singleshot_attack()
        else:
            for entities in self.targeted_entity_object:
                if self.arrow_cooldown_timer >= self.arrow_cooldown:
                    self.create_arrow_object(entities)
    
    def _handle_arrow_status(self, arrow):
        if arrow.get_arrow_status('active') is False or arrow.get_arrow_status('entity_killed'):
            if arrow.get_arrow_status('entity_killed'):
                self.kill_count += 1
                self.upgrade_time += 2000
            arrow.kill()

    def _handle_entity_targeting(self, entity_object_group):
        self.entity_list = [entities for entities in entity_object_group if self.position.distance_to(entities.rect.center) <= self.attack_radius + 30]
        
        if self.entity_list and self.arrow_multishot:
            self.targeted_entity_object = self.entity_list[:2]
        elif self.entity_list and not self.arrow_multishot:
            self.targeted_entity_object = self.entity_list[0]
        else:
            self.targeted_entity_object = 0
    
    def _handle_tower_events(self, delta_time, screen_surface, mouse_pos, mouse_just_clicked):
        self._handle_internal_timer(delta_time)
        # Handle Time Base Upgrades
        if self.upgrade_time >= self.upgrade_time_threshold:
            self.upgrade_time = 0
            self._handle_tower_upgrade()
        
        # Handle Hover
        if self.anchor_rect.collidepoint(mouse_pos):
            self.show_tower_radius(screen_surface)

    def _handle_preview_mode(self, screen_surface):
        self.show_tower_radius(screen_surface)
        self.image = pygame.image.load(os.path.join('assets','ArcherTower', 'basetower.png'))

    def _change_animation_state(self, new_state):
        if new_state in self.animation_frames and new_state != self.animation_state:
            self.animation_state = new_state
            self.animation_index = 0

    def _get_animation_frame(self):
        if not self.animation_frames or self.animation_state not in self.animation_frames:
            return pygame.Surface((64, 64), pygame.SRCALPHA)
        frames = self.animation_frames[self.animation_state][self.upgrade_level]
        frame = frames[int(self.animation_index) % len(frames)]
        return frame
    
    def create_arrow_object(self, entity_object):
        arrow_object = Arrow(self.rect, entity_object, self.arrow_damage, self.arrow_speed)
        self.arrow_object_group.add(arrow_object)
        self.arrow_object_lastshot = self.time_since_placed 

    def update_position(self, position=pygame.Vector2(0,0)):
        position.x = position.x * 64 + 32
        position.y = position.y * 64
        self.position.update(position)
        self.rect.center = self.position
    
    def update(self, delta_time, screen_surface, entity_object_group,mouse_pos,mouse_just_clicked):
        # Class Timer
        if self.preview_mode:
            self._handle_preview_mode(screen_surface)
            return
    
        self._handle_tower_events(delta_time,screen_surface, mouse_pos,mouse_just_clicked)
        self._handle_animation(delta_time)
        self._handle_attack(delta_time, screen_surface, entity_object_group)

class Arrow(pygame.sprite.Sprite):
    def __init__(self, tower_rect, target_entity_object=None, damage=15, speed=250):
        super().__init__()
        self.image_original = pygame.image.load(os.path.join('assets', 'ArcherTower','Normal.png'))
        self.image = self.image_original.copy()
        self.reference_position = pygame.Vector2(tower_rect.center)
        self.position = pygame.Vector2(self.reference_position)
        self.rect = self.image.get_frect(center = self.position)
        self.speed = speed
        self.damage = damage
        self.target_entity = target_entity_object 

        self.IS_ACTIVE = True
        self.IS_ENTITY_KILLED = False

    def _handle_arrow_logic(self, delta_time):
        if self.target_entity and self.target_entity.alive():
            self.IS_ACTIVE = True
            self.IS_ENTITY_KILLED = False

            arrow_position = pygame.Vector2(self.rect.midtop)
            arrow_direction = ((self.target_entity.rect.center - arrow_position)).normalize()
            arrow_rotation_angle = math.degrees(math.atan2(-arrow_direction.y, arrow_direction.x)) - 90
            self.image = pygame.transform.rotate(self.image_original, arrow_rotation_angle)
            self.mask = pygame.mask.from_surface(self.image)

            self._handle_arrow_movement(arrow_direction ,delta_time)
            self._handle_arrow_max_distance()
            self._handle_arrow_collision()
        else:
            self.IS_ACTIVE = False
    
    def _handle_arrow_movement(self, arrow_direction, delta_time):
        self.position += arrow_direction * self.speed * delta_time
        self.rect.center = self.position
    
    def _handle_arrow_collision(self):
        if pygame.Vector2(self.rect.midtop).distance_to(self.target_entity.rect.center) > max(self.rect.width, self.rect.height) * 2:
            return

        # Precise Collision Checking
        offset = (self.target_entity.rect.x - self.rect.x, self.target_entity.rect.y - self.rect.y)
        overlap_point = self.mask.overlap(self.target_entity.mask, offset)
        if overlap_point:
            self.target_entity.take_damage(self.damage)
            if not self.target_entity.get_entity_status('is_alive'):
                self.IS_ENTITY_KILLED = True
            self.IS_ACTIVE = False

    def _handle_arrow_max_distance(self):
        distance = self.reference_position.distance_to(self.position)
        if distance >= 250:
            self.IS_ACTIVE = False
        
    def get_arrow_status(self, state):
        if state == 'active':
            return self.IS_ACTIVE
        elif state == 'entity_killed':
            return self.IS_ENTITY_KILLED
            
    def update(self, delta_time):
        self._handle_arrow_logic(delta_time)


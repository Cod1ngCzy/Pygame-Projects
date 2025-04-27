from settings import *

class Tower(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        self.animation_index = 0
        self.animation_speed = 10
        self.animation_state = None
        self.upgrade_level = 1
        self.animation_frames = {}

        self.position = pygame.Vector2(0,0)
        self.image = None
        self.rect = None

        self.attack_radius = 150
        self.attack_radius_surface = pygame.Surface((self.attack_radius*2, self.attack_radius*2), pygame.SRCALPHA)
        self.attack_radius_rect = self.attack_radius_surface.get_frect(center = (0,0))
        self.attack_radius_color = (255,255,255,100)
        pygame.draw.circle(self.attack_radius_surface, (255, 0, 0, 75), (self.attack_radius, self.attack_radius), self.attack_radius)
        pygame.draw.circle(self.attack_radius_surface, (0, 0, 0, 255), (self.attack_radius, self.attack_radius), self.attack_radius, 2)

        # Tower Upgrade Properties
        self.time_since_placed = 0
        self.base_upgrade_time = 60000
        self.upgrade_time_threshold = self.base_upgrade_time
        self.kill_count = 0
        self.time_reduction_perkill = 2000
        self.max_upgrade_level = 6
        self.upgrade_level = 0

        # Flag
        self.show_rect = False
        self.show_radius = False
        self.preview_mode = False
        self.is_upgrade = False

    def _get_spritesheet(self, path_to_image):
        image_paths = os.listdir(path_to_image)
        image_sprite = []
        
        for image in image_paths:
            image = pygame.image.load(os.path.join(path_to_image, image)).convert_alpha()
            image = pygame.transform.scale(image, (64, image.get_height()))
            image_sprite.append(image)

        return image_sprite

    def _load_spritesheet_animations(self, base_path, prefix, count):
        animations = {}
        
        for level in range(1, count + 1):
            path = f"{base_path}/{prefix}{level}"
            files = os.listdir(path)
            frames = []
            
            for file in sorted(files):  # Sort to ensure correct order
                img = pygame.image.load(os.path.join(path, file)).convert_alpha()
                img = pygame.transform.scale(img, (64, img.get_height()))
                frames.append(img)
                
            animations[level] = frames
            
        return animations

    def show_tower_radius(self, screen_surface):
        self.attack_radius_rect.center = (self.rect.centerx, self.rect.centery + 30)
        screen_surface.blit(self.attack_radius_surface, self.attack_radius_rect)
    
    def show_tower_rect(self, screen_surface):
        pygame.draw.rect(screen_surface, (255,255,255), self.rect, 1)
    
class ArcherTower(Tower):
    def __init__(self, position=pygame.Vector2(0,0), preview_mode=False):
        super().__init__()

        # Animation Properties
        self.animation_speed = 10
        self.animation_state = 'idle'
        self.upgrade_level = 1
        self.animation_frames = {
            'idle': self._load_spritesheet_animations('assets/ArcherTower/IdleAnimation', 'idle', 6),
            'upgrade': self._load_spritesheet_animations('assets/ArcherTower/UpgradeAnimation', 'upgrade', 7)
        }

        # Base Image for Sprite Group Use
        self.position = pygame.Vector2(position.x * 64 + 32,position.y * 64)
        self.image = self._get_animation_frame()
        self.rect = self.image.get_frect(center = self.position)

        self.attack_radius = 150
        self.attack_radius_rect = self.attack_radius_surface.get_frect(center = (self.rect.center))
        self.preview_mode = preview_mode

        # ==== TOWER ARROW PROPERTIES === #
        self.arrow_object_group = pygame.sprite.Group()
        self.arrow_object = None
        self.arrow_cooldown = 500
        self.arrow_object_lastshot = 0
        # ==== TOWER ARROW PROPERTIES === #

        # ==== ENEMY PROPERTIES ==== #
        self.entity_list = []
        self.targeted_entity_object = None
         # ==== ENEMY PROPERTIES ==== #
    
    def _handle_animation(self, delta_time):
        self.animation_index += self.animation_speed * delta_time

        # Handle Upgrade Animation
        if self.animation_state == 'upgrade':
            frames = self.animation_frames['upgrade'][self.upgrade_level]
            if int(self.animation_index) >= len(frames):
                self._change_animation_state('idle')

        self.image = self._get_animation_frame()
    
    def _handle_tower_upgrade(self):
        if self.upgrade_level < self.max_upgrade_level and self.is_upgrade:
            # TODO: make this abomination more readable
            self.upgrade_level += 1
            self._change_animation_state('upgrade')
            self.is_upgrade = False

    def _handle_internal_timer(self, delta_time):
        self.time_since_placed += delta_time * 1000

        if self.time_since_placed >= self.upgrade_time_threshold and self.upgrade_level < self.max_upgrade_level:
            self.base_upgrade_time *= 1.5
            self.upgrade_time_threshold = self.base_upgrade_time
            self.is_upgrade = True

    def _handle_attack(self, delta_time, screen_surface, entity_object_group):
        entity_position = pygame.Vector2(self.targeted_entity_object.rect.center if self.targeted_entity_object else (0,0))
        entity_distance = self.position.distance_to(entity_position)
        arrow_cooldown_timer = self.time_since_placed - self.arrow_object_lastshot

        self._handle_entity_targeting(entity_object_group) 

        if entity_distance <= self.attack_radius and arrow_cooldown_timer >= self.arrow_cooldown and self.arrow_object is None:
            self.arrow_object = Arrow(self.rect, self.targeted_entity_object)
            self.arrow_object_group.add(self.arrow_object)
            self.arrow_object_lastshot = self.time_since_placed 
                
        if self.arrow_object:
            self.arrow_object_group.update(delta_time)
            self.arrow_object_group.draw(screen_surface)
            if self.arrow_object.IS_ENTITY_KILLED:
                self.kill_count += 1
            if self.arrow_object.IS_COLLIDED or self.arrow_object.IS_NO_OBJECT:
                self.arrow_object = None
    
    def _handle_entity_targeting(self, entity_object_group):
        self.entity_list = [entity for entity in entity_object_group if self.position.distance_to(entity.rect.center) <= self.attack_radius]

        if self.entity_list:
            self.targeted_entity_object = self.entity_list[0]
        else:
            self.targeted_entity_object = None
        
    def _change_animation_state(self, new_state):
        if new_state in self.animation_frames and new_state != self.animation_state:
            self.animation_state = new_state
            self.animation_index = 0

    def _get_animation_frame(self):
        frames = self.animation_frames[self.animation_state][self.upgrade_level]
        index = int(self.animation_index) % len(frames)

        return frames[index]

    def update(self, delta_time, screen_surface, entity_object_group):
        # Class Timer
        if self.preview_mode:
            self.show_tower_radius(screen_surface)
            return
        
        self._handle_internal_timer(delta_time)
        self._handle_tower_upgrade() 
        
        self.show_tower_radius(screen_surface)
        self._handle_animation(delta_time)
        self._handle_attack(delta_time, screen_surface, entity_object_group)
    
    def update_position(self, position=pygame.Vector2(0,0)):
        position.x = position.x * 64 + 32
        position.y = position.y * 64
        self.position.update(position)
        self.rect.center = self.position

class Arrow(pygame.sprite.Sprite):
    def __init__(self, tower_rect, target_entity_object=None):
        super().__init__()
        self.image_original = pygame.image.load(os.path.join('assets', 'ArcherTower','arrow.png'))
        self.image = self.image_original.copy()
        self.mask = pygame.mask.from_surface(self.image)
        self.position = pygame.Vector2(tower_rect.center)
        self.rect = self.image.get_frect(center = self.position)
        self.speed = 700
        self.damage = 15

        self.target_entity = target_entity_object 

        self.IS_COLLIDED = False
        self.IS_NO_OBJECT = False
        self.IS_ENTITY_KILLED = False

    def _handle_arrow_logic(self, delta_time):
        if self.target_entity and self.target_entity.alive():
            self.IS_NO_OBJECT = False

            # Calculate Direction for Aiming
            arrow_position = pygame.Vector2(self.rect.midtop)
            arrow_direction = (self.target_entity.rect.center - arrow_position).normalize()

            # Rotate Arrow
            arrow_rotation_angle = math.degrees(math.atan2(-arrow_direction.y, arrow_direction.x)) - 90
            self.image = pygame.transform.rotate(self.image_original, arrow_rotation_angle)
            self.mask = pygame.mask.from_surface(self.image)

            # Handle Arrow Logic (Movement & Collision)
            self._handle_arrow_collision(self.target_entity)
            self._handle_arrow_movement(arrow_direction ,delta_time)
        else:
            self.kill()
            self.IS_NO_OBJECT = True
    
    def _handle_arrow_movement(self, arrow_direction, delta_time):
        self.position += arrow_direction * self.speed * delta_time
        self.rect.center = self.position
    
    def _handle_arrow_collision(self, entity_object):
        if entity_object:
            offset_x = entity_object.rect.x - self.rect.x
            offset_y = entity_object.rect.y - self.rect.y
            overlap_point = self.mask.overlap(entity_object.mask, (offset_x, offset_y))

            if overlap_point:
                entity_object.take_damage(self.damage)
                if entity_object.killed:
                    self.IS_ENTITY_KILLED = True
                self.kill()
                self.IS_COLLIDED = True
            
    def update(self, delta_time):
        print(self.target_entity)
        self._handle_arrow_logic(delta_time)

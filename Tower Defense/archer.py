from settings import *

class ArcherTower(pygame.sprite.Sprite):
    def __init__(self, position=pygame.Vector2(0,0)):
        super().__init__()

        # Animation Properties
        self.animation_index = 0
        self.animation_speed = 10
        self.animation_state = 'idle'
        self.upgrade_level = 1
        self.animations = {
            'idle': self._load_spritesheet_animations('assets/ArcherTower/IdleAnimation', 'idle', 6),
            'upgrade': self._load_spritesheet_animations('assets/ArcherTower/UpgradeAnimation', 'upgrade', 7)
        }

        # Base Image for Sprite Group Use
        self.image = self._get_animation_frame()
        self.position = pygame.Vector2(position.x * 64,position.y * 64)
        self.rect = self.image.get_frect(center = self.position)
        # Tower Attack Properties
        self.attack_radius = 150
        self.attack_radius_surface = pygame.Surface((self.attack_radius*2, self.attack_radius*2), pygame.SRCALPHA)
        self.attack_radius_rect = self.attack_radius_surface.get_frect(center = (self.rect.center))
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
        self.upgrade = False

        # Flag
        self.show_rect = False
        self.show_radius = False

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
    
    def _handle_animation(self, delta_time):
        self.animation_index += self.animation_speed * delta_time

        # Handle Upgrade Animation
        if self.animation_state == 'upgrade':
            frames = self.animations['upgrade'][self.upgrade_level]
            if int(self.animation_index) >= len(frames):
                self._change_animation_state('idle')

        self.image = self._get_animation_frame()
    
    def _handle_tower_upgrade(self):
        if self.upgrade_level < self.max_upgrade_level:
            # TODO: make this abomination more readable
            if self.upgrade:
                self.upgrade_level += 1
                self._change_animation_state('upgrade')
                self.upgrade = False
    
    def _handle_internal_timer(self, delta_time):
        self.time_since_placed += delta_time * 1000

        if self.time_since_placed >= self.upgrade_time_threshold and self.upgrade_level < self.max_upgrade_level:
            self.upgrade = True
            self.base_upgrade_time *= 1.5
            self.upgrade_time_threshold = self.base_upgrade_time
        
        #print(self.time_since_placed, self.base_upgrade_time)

    def _handle_attack(self, delta_time, screen_surface, entity_object_group):
        self._handle_entity_targeting(entity_object_group)

        tower_position = pygame.Vector2(self.rect.center)
        entity_position = pygame.Vector2(self.targeted_entity_object.rect.center if self.targeted_entity_object else (0,0))
        entity_distance = tower_position.distance_to(entity_position)

        arrow_cooldown_timer = self.time_since_placed - self.arrow_object_lastshot 

        if entity_distance <= self.attack_radius and arrow_cooldown_timer >= self.arrow_cooldown:
            if self.arrow_object is None:
                self.arrow_object = Arrow(self.rect)
                self.arrow_object_group.add(self.arrow_object)
                self.arrow_object_lastshot = self.time_since_placed 
                
        if self.arrow_object:
            self.arrow_object_group.update(delta_time, self.targeted_entity_object, entity_position)
            self.arrow_object_group.draw(screen_surface)
            if self.arrow_object.IS_COLLIDED:
                self.arrow_object.kill()
                self.arrow_object = None
    
    def _handle_entity_targeting(self, entity_object_group):
        self.entity_list = [e for e in entity_object_group if e.health > 0]

        if self.entity_list:
            self.targeted_entity_object = self.entity_list[0]
        else:
            self.targeted_entity_object = None


    
    def _change_animation_state(self, new_state):
        if new_state in self.animations and new_state != self.animation_state:
            self.animation_state = new_state
            self.animation_index = 0

    def _get_animation_frame(self):
        frames = self.animations[self.animation_state][self.upgrade_level]
        index = int(self.animation_index) % len(frames)

        return frames[index]

    def show_tower_radius(self, screen_surface):
        self.attack_radius_rect.center = (self.rect.centerx, self.rect.centery + 30)
        screen_surface.blit(self.attack_radius_surface, self.attack_radius_rect)
    
    def show_tower_rect(self, screen_surface):
        pygame.draw.rect(screen_surface, (255,255,255), self.rect, 1)

    def update(self, delta_time, screen_surface, entity_object_group):
        # Class Timer
        self._handle_internal_timer(delta_time)
        self._handle_tower_upgrade() 

        #mouse_pos = pygame.Vector2(pygame.mouse.get_pos()[0] // 64, pygame.mouse.get_pos()[1] // 64)

        """if pygame.mouse.get_pressed()[0]: 
            mouse_pos.x = mouse_pos.x * 64 + 32
            mouse_pos.y = mouse_pos.y * 64 + 64
            self.position.update(mouse_pos)
            self.rect.midbottom = self.position"""
        
        self.show_tower_radius(screen_surface)
        self.show_tower_rect(screen_surface)
        self._handle_animation(delta_time)
        self._handle_attack(delta_time, screen_surface, entity_object_group)

class Arrow(pygame.sprite.Sprite):
    def __init__(self, tower_rect):
        super().__init__()
        self.image_original = pygame.image.load(os.path.join('assets', 'ArcherTower','arrow.png'))
        self.image = self.image_original.copy()
        self.mask = pygame.mask.from_surface(self.image)
        self.position = pygame.Vector2(tower_rect.center)
        self.rect = self.image.get_frect(center = self.position)
        self.speed = 400
        self.damage = 15

        self.IS_COLLIDED = False

    def handle_arrow_logic(self, delta_time, entity_object, entity_position):
        if entity_object:
            # Calculate Direction for Aiming
            arrow_position = pygame.Vector2(self.rect.midtop)
            entity_position = entity_position
            arrow_direction = (entity_position - arrow_position).normalize()

            # Rotate Arrow
            arrow_rotation_angle = math.degrees(math.atan2(-arrow_direction.y, arrow_direction.x)) - 90
            self.image = pygame.transform.rotate(self.image_original, arrow_rotation_angle)
            self.mask = pygame.mask.from_surface(self.image)

            # Handle Arrow Logic (Movement & Collision)
            self._handle_arrow_collision(entity_object)
            self._handle_arrow_movement(arrow_direction ,delta_time)
    
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
                self.kill()
                self.IS_COLLIDED = True
            
    def update(self, delta_time, entity_object, entity_position):
        self.handle_arrow_logic(delta_time, entity_object, entity_position)
    
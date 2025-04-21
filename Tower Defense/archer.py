from settings import *

class ArcherTower(pygame.sprite.Sprite):
    def __init__(self, position=pygame.Vector2(0,0)):
        super().__init__()
        # Idle Animation Sprites/Frames
        self.TOWER_idle_frame = {
            'idle1': self._get_image(os.path.join('assets', 'ArcherTower', 'IdleAnimation', 'idle1')),
            'idle2': self._get_image(os.path.join('assets', 'ArcherTower', 'IdleAnimation', 'idle2')),
            'idle3': self._get_image(os.path.join('assets', 'ArcherTower', 'IdleAnimation', 'idle3')),
            'idle4': self._get_image(os.path.join('assets', 'ArcherTower', 'IdleAnimation', 'idle4')),
            'idle5': self._get_image(os.path.join('assets', 'ArcherTower', 'IdleAnimation', 'idle5')),
            'idle6': self._get_image(os.path.join('assets', 'ArcherTower', 'IdleAnimation', 'idle6')),
        }
        self.TOWER_idle_keys = self.TOWER_idle_frame.keys()
        self.TOWER_upgrade_state = 2
        self.TOWER_idle_category = list(self.TOWER_idle_keys)[self.TOWER_upgrade_state]

        # Animation Properties
        self.animation_index = 0
        self.animation_speed = 10

        # Base Image for Sprite Group Use
        self.image = self.TOWER_idle_frame[self.TOWER_idle_category][int(self.animation_index)]

        self.TOWER_position = pygame.Vector2(position.x * 64,position.y * 64)
        self.rect = self.image.get_frect(center = self.TOWER_position)
        # Tower Attack Properties
        self.TOWER_attack_radius = 250
        self.TOWER_attack_radius_surface = pygame.Surface((self.TOWER_attack_radius*2, self.TOWER_attack_radius*2), pygame.SRCALPHA)
        self.TOWER_attack_radius_rect = self.TOWER_attack_radius_surface.get_frect(center = (self.rect.center))
        self.TOWER_attack_radius_color = (255,255,255,100)
        pygame.draw.circle(self.TOWER_attack_radius_surface, (255, 0, 0, 75), (self.TOWER_attack_radius, self.TOWER_attack_radius), self.TOWER_attack_radius)
        pygame.draw.circle(self.TOWER_attack_radius_surface, (0, 0, 0, 255), (self.TOWER_attack_radius, self.TOWER_attack_radius), self.TOWER_attack_radius, 2)

        # Flag
        self.show_rect = False
        self.show_radius = False

        # ==== TOWER ARROW PROPERTIES === #
        self.ARROW_SPRITES = pygame.sprite.Group()
        self.ARROW_OBJECT = None
        self.ARROW_COOLDOWN = 200
        # ==== TOWER ARROW PROPERTIES === #

        # ==== ENEMY ==== #
        self.ENTITY_OBJECT = None
        
    def _get_image(self, path_to_image):
        sprite_image_paths = os.listdir(path_to_image)
        sprite_images = [pygame.image.load(os.path.join(path_to_image,sprite)).convert_alpha() for sprite in sprite_image_paths]
        sprite_images = [pygame.transform.scale(sprite, (64,sprite.get_height())) for sprite in sprite_images]
        return sprite_images
    
    def _handle_animation_IDLE(self, delta_time):
        self.animation_index += self.animation_speed * delta_time
        self.animation_index %= len(self.TOWER_idle_frame[self.TOWER_idle_category])

        self.image = self.TOWER_idle_frame[self.TOWER_idle_category][int(self.animation_index)]

    def _handle_tower_upgrade(self):
        return
        keys = pygame.key.get_pressed()

        if keys[pygame.K_q]:
            print('upgrade')
            self.animation_index = 0
            self.TOWER_upgrade_state = 4
            self.TOWER_idle_category = list(self.TOWER_idle_keys)[self.TOWER_upgrade_state]
    
    def _handle_arrow(self, delta_time, screen_surface, entity_object):
        if entity_object:
            tower_position = pygame.Vector2(self.rect.center)
            entity_position = pygame.Vector2(entity_object.rect.center)
            entity_distance = tower_position.distance_to(entity_position)

            if entity_distance <= self.TOWER_attack_radius:
                if self.ARROW_OBJECT is None:
                    self.ARROW_OBJECT = Arrow(self.rect)
                    self.ARROW_SPRITES.add(self.ARROW_OBJECT)
            if self.ARROW_OBJECT:
                if self.ARROW_OBJECT.IS_COLLIDED:
                    self.ARROW_OBJECT.kill()
                    self.ARROW_OBJECT = None

            self.ARROW_SPRITES.update(delta_time, entity_object, entity_position)
            self.ARROW_SPRITES.draw(screen_surface)
    
    def show_tower_radius(self, screen_surface):
        self.TOWER_attack_radius_rect.center = self.rect.center
        screen_surface.blit(self.TOWER_attack_radius_surface, self.TOWER_attack_radius_rect)
    
    def show_tower_rect(self, screen_surface):
        pygame.draw.rect(screen_surface, (255,255,255), self.rect, 1)

    def update(self, delta_time, screen_surface, entity_object):
        self.ENTITY_OBJECT = entity_object

        print(self.TOWER_position)

        if self.ENTITY_OBJECT.health <= 0:
            self.ENTITY_OBJECT = None

        self.show_tower_radius(screen_surface)
        self.show_tower_rect(screen_surface)
        self._handle_animation_IDLE(delta_time)

        mouse_pos = pygame.Vector2(pygame.mouse.get_pos()[0] // 64, pygame.mouse.get_pos()[1] // 64)

        if pygame.mouse.get_pressed()[0]:
            mouse_pos.x = mouse_pos.x * 64 + 64 // 2
            mouse_pos.y = mouse_pos.y * 64 + 64 // 2 + 32
            self.TOWER_position.update(mouse_pos)
            self.rect.midbottom = self.TOWER_position
            print(self.TOWER_position.x, self.TOWER_position.y)
        
        # Render Arrow Frame
        self._handle_arrow(delta_time, screen_surface, self.ENTITY_OBJECT)

class Arrow(pygame.sprite.Sprite):
    def __init__(self, tower_rect):
        super().__init__()
        self.image_original = pygame.image.load(os.path.join('assets', 'ArcherTower','arrow.png'))
        self.image = self.image_original.copy()
        self.mask = pygame.mask.from_surface(self.image)
        self.position = pygame.Vector2(tower_rect.center)
        self.rect = self.image.get_frect(center = self.position)
        self.speed = 400
        self.damage = 5

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
    
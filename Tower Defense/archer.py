from settings import *
from arrow import Arrow

class ArcherTower(pygame.sprite.Sprite):
    def __init__(self):
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
        self.TOWER_position = pygame.Vector2(1024 // 2,768 // 2)
        self.rect = self.image.get_frect(center = self.TOWER_position)
        # Tower Attack Properties
        self.TOWER_attack_center = self.TOWER_position
        self.TOWER_attack_radius = 200
        # Radius Visibility 
        self.TOWER_attack_radius_color = (255,255,255,100)

        # ==== TOWER ARROW PROPERTIES === #
        self.ARROW_SPRITES = pygame.sprite.Group()
        # ==== TOWER ARROW PROPERTIES === #
        
    def _get_image(self, path_to_image):
        sprite_image_paths = os.listdir(path_to_image)
        sprite_images = [pygame.image.load(os.path.join(path_to_image,sprite)).convert_alpha() for sprite in sprite_image_paths]
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
    
    def _handle_arrow(self, delta_time, enemy_objects):
        if not self.ARROW_SPRITES:
            arrow_object = Arrow(self.rect)
            arrow_object.tower_attack_radius = self.TOWER_attack_radius
            self.ARROW_SPRITES.add(arrow_object)
            
    
    def _handle_arrow_FIRE(self, delta_time, enemy_object = None):
        if enemy_object is None:
            print('none')
            return
        
        if enemy_object.alive():
            enemy_rect = enemy_object.rect
        else: 
            return
        
        # Calculate direction vector from arrow to enemy
        arrow_pos = pygame.Vector2(self.ARROW_rect.center)
        direction = pygame.Vector2(enemy_rect.centerx, enemy_rect.centery) - arrow_pos
       
        dx = (enemy_rect.x + 20) - arrow_pos.x
        dy = (enemy_rect.y + 20)- arrow_pos.y
        distance = dx * dx + dy * dy
        
        # Normalize the direction vector (make it length 1)
        if direction.length() > 0:  # Avoid division by zero
            direction = direction.normalize()

        if distance <= self.TOWER_attack_radius * self.TOWER_attack_radius:
            # Calculate angle in radians, then convert to degrees
            angle = math.degrees(math.atan2(-direction.y, direction.x)) - 90
            
            # Rotate from the original image each time
            self.ARROW_frame = pygame.transform.rotate(self.ARROW_original, angle)
            
            # Move the arrow in the direction it's pointing
            # The speed is 200 pixels per second
            move_speed = 200 * delta_time
            
            # Update position using the normalized direction vector
            arrow_pos += direction * move_speed
            
            # Update the rect with the new position, maintaining rotation
            self.ARROW_rect = self.ARROW_frame.get_frect(center=arrow_pos)

            if self.ARROW_rect.colliderect(enemy_rect):
                self._handle_arrow_reset()
                enemy_object.kill()
        
            
    def _handle_arrow_reset(self):
        self.ARROW_original = pygame.image.load(os.path.join('assets', 'ArcherTower', 'arrow.png'))
        self.ARROW_frame = self.ARROW_original.copy()  # Working copy
        self.ARROW_offset = pygame.Vector2(35,60)
        self.ARROW_rect = self.ARROW_frame.get_frect(midbottom = (self.rect.x + self.ARROW_offset.x, self.rect.y + self.ARROW_offset.y))
                 
    def update(self, delta_time, screen_surface, enemy_rect):
        pygame.draw.circle(screen_surface,self.TOWER_attack_radius_color, self.TOWER_attack_center, self.TOWER_attack_radius)
        self._handle_animation_IDLE(delta_time)
        
        # Render Arrow Frame
        self.ARROW_SPRITES.update(delta_time, screen_surface, enemy_rect)
        self.ARROW_SPRITES.draw(screen_surface)
        self._handle_arrow(delta_time, screen_surface)
       
from settings import *

class Arrow(pygame.sprite.Sprite):
    def __init__(self, tower_rect):
        super().__init__()
        self.image_original = pygame.image.load(os.path.join('assets', 'ArcherTower','arrow.png')).convert_alpha()
        self.image = self.image_original.copy()
        self.position = pygame.Vector2(tower_rect.x,tower_rect.y)
        self.rect = self.image.get_frect(center = self.position)
        self.tower_attack_radius = None
    
    def _handle_fire(self, delta_time, enemy_objects):
        if enemy_objects is None:
            return

        enemy_rect = enemy_objects.rect
        
        arrow_position = pygame.Vector2(self.rect.center)
        arrow_direction = pygame.Vector2(enemy_rect.centerx, enemy_rect.centery) - arrow_position

        # Calculate Distance
        dx = (enemy_rect.x) - arrow_position.x
        dy = (enemy_rect.y)- arrow_position.y
        arrow_distance_to_enemy = dx * dx + dy * dy

        if arrow_direction.length() > 0:
            arrow_direction = arrow_direction.normalize()
        
        if arrow_distance_to_enemy <= self.tower_attack_radius * self.tower_attack_radius:
            arrow_angle = math.degrees(math.atan2(-arrow_direction.y, arrow_direction.x)) - 90

            self.image = pygame.transform.rotate(self.image_original, arrow_angle)

            arrow_speed = 200 * delta_time

            arrow_position += arrow_direction * arrow_speed

            self.rect = self.image.get_frect(center = arrow_position)
    
    def update(self, delta_time, screen_surface, enemy_rect):
        self._handle_fire(delta_time, enemy_rect)
    
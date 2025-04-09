import pygame.gfxdraw
import pygame.gfxdraw
from settings import *

class Line():
    def __init__(self, p_ax, p_ay, p_bx, p_by):
        self.start_point = pygame.Vector2(p_ax, p_ay)
        self.end_point = pygame.Vector2(p_bx, p_by)
      
    def intersect(self, other_line):
        # Unpack the (x, y) coordinates of the start and end points for both line segments
        (x1, y1), (x2, y2) = self.start_point, self.end_point               # Line 1: start and end points
        (x3, y3), (x4, y4) = other_line.start_point, other_line.end_point   # Line 2: start and end points

        # Compute the determinant of the system (denominator in intersection formula)
        denominator = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)

        # If the denominator is zero, the lines are parallel and do not intersect
        if denominator == 0:
            return None

        # Calculate the intersection ratio (ua, ub) along each segment
        intersection_ratio_L1 = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denominator # Represents how far the intersection is along Line 1 (0 = start, 1 = end)
        intersection_ratio_L2 = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denominator # Represents how far the intersection is along Line 2 (0 = start, 1 = end)

        # Check if the intersection point lies within both line segments
        if 0 <= intersection_ratio_L1 <= 1 and 0 <= intersection_ratio_L2 <= 1:
            # Calculate the intersection point
            x = x1 + intersection_ratio_L1 * (x2 - x1) # X-coordinate of intersection
            y = y1 + intersection_ratio_L1 * (y2 - y1) # Y-coordinate of intersection
            return pygame.Vector2(x, y) # Return intersection point as vector
    
    def collide(self, circle_center, circle_radius):
        circle_vector = circle_center - self.start_point
        line_vector = self.end_point - self.start_point 
        line_magnitude_squared = line_vector.length_squared()

        if line_magnitude_squared == 0: # Handle case where start and end points are the same
            return self.start_point.distance_to(circle_center) <= circle_radius

        # Clamp to restrict projection value to 0 and 1
        projection = circle_vector.dot(line_vector) / line_magnitude_squared # Projection Formula
        projection = max(0, min(1, projection))

        # Compute for Closest Point
        closest_point = pygame.Vector2(
            self.start_point.x + projection * (self.end_point.x - self.start_point.x ), # X value
            self.start_point.y + projection * (self.end_point.y - self.start_point.y)
        )

        # Get Distance 
        distance = math.sqrt((circle_center.x - closest_point.x) ** 2 + (circle_center.y - closest_point.y) ** 2)

        if distance <= circle_radius:
            return pygame.Vector2(closest_point.x, closest_point.y)

        return None
    
    def draw(self, display):
        pygame.draw.line(display,(255,255,255), self.start_point, self.end_point)

class Segment():
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect((x, y, width, height))
        self.pos = pygame.Vector2(x, y)
        self.corners = self.update_corners()
        self.corner_radius = 5
        self.dragging_corner = None
        self.edges = []
        self.update_edges()
    
    def show_rect_properties(self, circle=False, lines=False, color='white'):
        pygame.draw.rect(DISPLAY, 'green', self.rect)
        
        if lines:
            for edge in self.edges:
                pygame.draw.line(DISPLAY, color, edge[0], edge[1], 2)
        
        if circle:
            for corner in self.corners:
                pygame.draw.circle(DISPLAY, 'yellow', corner, self.corner_radius)

    def update_corners(self):
        self.corners = [
            pygame.Vector2(self.rect.left, self.rect.top),
            pygame.Vector2(self.rect.right, self.rect.top),
            pygame.Vector2(self.rect.left, self.rect.bottom),
            pygame.Vector2(self.rect.right, self.rect.bottom)
        ]
        return self.corners
    
    def update_edges(self):
        self.edges = [
            (self.corners[0], self.corners[1]),  # Top
            (self.corners[1], self.corners[3]),  # Right
            (self.corners[3], self.corners[2]),  # Bottom
            (self.corners[2], self.corners[0])   # Left
        ]

    def handle_position(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        mouse_pressed = pygame.mouse.get_pressed()[0]  # Left mouse button
        
        # Check if we're near any corner first
        corner_dragging = False
        for i, corner in enumerate(self.corners):
            # Check if mouse is within the corner's circle
            distance = corner.distance_to(mouse_pos)
            if distance <= self.corner_radius:
                # Highlight the corner
                pygame.draw.circle(DISPLAY, (255, 255, 0), corner, self.corner_radius)
                
                # If clicked, drag the corner
                if mouse_pressed:
                    corner_dragging = True
                    # Update corner position
                    self.corners[i] = mouse_pos
                    
                    # Update rectangle based on corner positions
                    if i == 0:  # Top-left
                        self.rect.topleft = mouse_pos
                    elif i == 1:  # Top-right
                        self.rect.topright = mouse_pos
                    elif i == 2:  # Bottom-left
                        self.rect.bottomleft = mouse_pos
                    elif i == 3:  # Bottom-right
                        self.rect.bottomright = mouse_pos
                    
                    # Make sure width and height stay positive
                    if self.rect.width < 10:
                        self.rect.width = 10
                    if self.rect.height < 10:
                        self.rect.height = 10
                        
                    # Update all corners and edges after changing the rectangle
                    self.update_corners()
                    self.update_edges()
                    break  # Only drag one corner at a time
        
        # If we're not dragging a corner, check if we're dragging the whole rectangle
        if not corner_dragging and self.rect.collidepoint(mouse_pos) and mouse_pressed:
            self.rect.center = mouse_pos
            self.update_corners()
            self.update_edges()
    
    def update(self):
        self.handle_position()
        self.show_rect_properties(True, True)

class Ray():
    def __init__(self, origin=pygame.Vector2(), ray_length=0,ray_angle=0, ray_num=0, mouse_follow=False):
        self.origin = origin
        self.ray_angle = ray_angle
        self.ray_num = ray_num
        self.ray_length = ray_length
        self.mouse_follow = mouse_follow

        # Initialize Ray 
        self.segments = self.create()
    
    def create(self):
        rays = []

        for i in range(self.ray_num):
            angle_offset = -self.ray_angle / 2 + i * self.ray_num 
            radian = math.radians(angle_offset)

            end_point = pygame.Vector2(
                self.origin.x + self.ray_length * math.cos(radian),
                self.origin.y + self.ray_length * math.sin(radian)
            )

            rays.append(Line(self.origin.x, self.origin.y, end_point.x, end_point.y))
        
        return rays
    
    def handle_rays(self, obstacles):
        intersections = []
        intersections.append(self.origin)
        obstacle_list = (obstacles if isinstance(obstacles, list) else [obstacles] if obstacles is not None else [])

        for i ,ray in enumerate(self.segments):
            closest_intersection = None
            closest_obstacle = None
            closest_distance = float('inf')

            for obstacle in obstacle_list:
                intersection_point = ray.intersect(obstacle)

                if intersection_point:
                    distance = (intersection_point - ray.start_point).length()
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_intersection = intersection_point
                        closest_obstacle = obstacle

            if closest_intersection:
                intersections.append(closest_intersection)
            else:
                intersections.append(ray.end_point)

        return intersections
    
    def update(self, new_pos, obstacles, display):
        self.origin = new_pos
        mouse_pos, mouse_angle = 0, 0
        if self.mouse_follow:
            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            mouse_angle = math.atan2(mouse_pos.y - new_pos.y, mouse_pos.x - new_pos.x)

        for i, ray in enumerate(self.segments):
            angle_offset = -self.ray_angle / 2 + i * (self.ray_angle / (len(self.segments) - 1))
            radian = mouse_angle + math.radians(angle_offset)

            ray.start_point = new_pos
            ray.end_point = pygame.Vector2(
                new_pos.x + self.ray_length * math.cos(radian),
                new_pos.y + self.ray_length * math.sin(radian)
            )
        
        # Draw Light Rays
        pygame.draw.polygon(display, 'yellow', self.handle_rays(obstacles))
        
class Observer():
    def __init__(self,x,y,width,height):
        self.rect = pygame.Rect(x,y,width,height)
        self.pos = pygame.Vector2(self.rect.x,self.rect.y)
        self.radius = 15
        self.direction = pygame.Vector2(0,0)
        self.color = (0, 0, 0, 0) 

        # Movement Properties
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)
        self.acceleration_rate = 0.5
        self.speed = 80
        self.max_speed = 5.0
        self.friction = 0.85
        self.mass = 1.0

        # Sprite Properties
        self.player_sprite = SPRITES
        self.player_sprite = [pygame.transform.scale(self.player_sprite[i], (40,40)) for i in range(3)]
        self.walking_animation = self.player_sprite[1:3]
        self.animation_cd = 200
        self.last_update = 0
        self.frame_index = 0

        # Ray Properties
        self.ray_properties = {
            'length' : 200,
            'angle'  : 60,
            'number' : 20,
            'color'  : (255,255,150,0)
        }
        self.show_ray_lines = False

        # Create Rays
        self.line_of_sight = Ray(self.pos, self.ray_properties['length'], self.ray_properties['angle'], self.ray_properties['number'], True)       
        self.surrounding_light = Ray(self.pos, 30, 360, 30, True)  
                        
    def handle_collisions(self, lines=None):
        for line in lines:
            collision_point = line.collide(self.pos, self.radius)
            if collision_point is not None:
                collision_vector = pygame.Vector2(self.pos - collision_point)
                collision_vector = collision_vector.normalize()
                self.pos = collision_point + collision_vector * self.radius

    def handle_sprite(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        angle = math.degrees(math.atan2(mouse_pos.y - self.pos.y, mouse_pos.x - self.pos.x))
        angle_offset = -angle - 90
        rotated_sprite = pygame.transform.rotate(self.walking_animation[self.frame_index], angle_offset)
        sprite_rect = rotated_sprite.get_frect(center = (self.pos))

        current_time = pygame.time.get_ticks()
        if self.direction.x > 0 or self.direction.y > 0 or self.direction.x < 0 or self.direction.y < 0:
            DISPLAY.blit(rotated_sprite, sprite_rect)
            if current_time - self.last_update >= self.animation_cd:
                self.frame_index += 1
                self.frame_index = self.frame_index % len(self.walking_animation)
                self.last_update = current_time
        else:
            self.frame_index = 0
            DISPLAY.blit(pygame.transform.rotate(self.player_sprite[0], angle_offset), sprite_rect)
            
    def move(self,dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction

        # Base Movement
        self.acceleration = self.direction * (self.acceleration_rate / self.mass)
        self.velocity += self.acceleration

        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)

        self.velocity *= self.friction

        self.pos += self.velocity * self.speed * dt 
        self.rect.center = self.pos
    
    def update(self,dt,lines=None, light_surface=pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)):
        self.move(dt)
        self.line_of_sight.update(self.pos, lines, light_surface)
        self.surrounding_light.update(self.pos, lines, light_surface)
        self.handle_sprite()
        self.handle_collisions(lines)
        



from settings import *

class Line():
    def __init__(self, p_ax, p_ay, p_bx, p_by):
        # Initialize the start and end points of the line using pygame.Vector2 for easy math operations
        self.start_point = pygame.Vector2(p_ax, p_ay)
        self.end_point = pygame.Vector2(p_bx, p_by)
      

    def intersect(self, other_line):
        # Unpack the coordinates of the start and end points of both lines
        x1, y1 = self.start_point
        x2, y2 = self.end_point
        x3, y3 = other_line.start_point
        x4, y4 = other_line.end_point

        # Calculate the denominator for the intersection formula
        denominator = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)

        # If the denominator is zero, the lines are parallel and do not intersect
        if denominator == 0:
            return None

        # Calculate the parameters ua and ub to determine if the lines intersect
        ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denominator
        ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denominator

        # If both parameters are between 0 and 1, the lines intersect
        if 0 <= ua <= 1 and 0 <= ub <= 1:
            # Calculate the intersection point
            x = x1 + ua * (x2 - x1)
            y = y1 + ua * (y2 - y1)
            return pygame.Vector2(x, y)
    
    def check_collision(self, circle_center, circle_radius):
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
            return True, distance, pygame.Vector2(closest_point.x, closest_point.y)

        return None
        
    def draw(self):
        pygame.draw.line(DISPLAY,(255,255,255), self.start_point, self.end_point)

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

class Observer():
    def __init__(self,x,y,width,height):
        self.rect = pygame.Rect(x,y,width,height)
        self.radius = 15
        self.pos = pygame.Vector2(x,y)
        self.direction = pygame.Vector2(0,0)
        self.color = (255,255,255) # White
    
    def create_rays(self, angle=0, ray_length=100, field_of_view=None, step=10):
        length = ray_length
        rays = []

        if field_of_view is not None: 
            num_rays = math.ceil(field_of_view / step + 1)
            mouse_pos = pygame.Vector2(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1])
            mouse_angle = math.atan2(mouse_pos.y - self.rect.y, mouse_pos.x - self.rect.x)

            for i in range(num_rays):
                angle_offset = -field_of_view / 2 + i * step
                radian = mouse_angle + math.radians(angle_offset)

                start_point = pygame.Vector2(self.rect.x, self.rect.y)
                end_point = pygame.Vector2(self.rect.x + length * (math.cos(radian)),
                                           self.rect.y + length * (math.sin(radian)))
                
                rays.append(Line(start_point.x,start_point.y,end_point.x,end_point.y))
        else:
            for i in range(0, (angle + 1), step):
                radian = math.radians(i)

                start_point = pygame.Vector2(self.rect.x, self.rect.y)
                end_point = pygame.Vector2(self.rect.x + length * (math.cos(radian)),
                                           self.rect.y + length * (math.sin(radian)))
                
                rays.append(Line(start_point.x,start_point.y,end_point.x,end_point.y))

        return rays

    def handle_rays(self, obstacles=None):
        rays = self.create_rays(0, 500, 60, 1)
        intersection_groups = []
        polygon_points = []
        polygon_points.append(rays[0].start_point) 

        # Handle Ray Intersect
        for i, ray in enumerate(rays):
            closest_point = None
            closest_obstacle = None
            closest_distance = float('inf')

            obstacle_list = obstacles if isinstance(obstacles, list) else [obstacles] if obstacles is not None else []

            for obstacle in obstacle_list:
                point = ray.intersect(obstacle)

                if point:
                    distance = (point - ray.start_point).length()
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_point = point
                        closest_obstacle = obstacle

            if closest_point:
                polygon_points.append(closest_point)
                intersection_groups.append((i, closest_point, closest_obstacle))
            else:
                polygon_points.append(ray.end_point)

        if len(polygon_points) > 2:  # Need at least 3 points for a polygon
            self.draw_rays(polygon_points)
            self.draw_visible_edges(intersection_groups) # Pass the Collection of Intersecting Point

    def draw_rays(self, polygon_points, show_line=False, ray_color=(255, 255, 150, 50)):
        if show_line:
            for point in polygon_points:
                pygame.draw.line(DISPLAY, ray_color, self.rect.center, point, 1)
        else:
            pygame.gfxdraw.filled_polygon(DISPLAY, polygon_points, ray_color)

    def draw_visible_edges(self, intersection_groups):
        # Group intersections by obstacle to draw edge lines
        obstacle_intersections = {}
        for ray_index, intersection_point, obstacle in intersection_groups:
            if obstacle not in obstacle_intersections:
                obstacle_intersections[obstacle] = []
            obstacle_intersections[obstacle].append((ray_index, intersection_point))
        
        # Draw lines along obstacle edges (boundaries of visibility)
        for obstacle, points in obstacle_intersections.items():
            if len(points) >= 2:
                points.sort(key = lambda x: x[0])
            
                for i in range(len(points) - 1):
                    current_index, current_point = points[i]
                    next_index, next_point = points[i + 1]

                    if next_index - current_index == 1: # It means all rays are consecutive order
                        pygame.draw.line(DISPLAY, 'white', current_point, next_point, 5)

    def move(self,dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction

        # Base Movement
        self.pos += self.direction * dt * 300
        self.rect.center = self.pos
    
    def update(self,dt,other_line=None):
        self.move(dt)
        self.handle_rays(other_line)
        for line in other_line:
            value = line.check_collision(self.pos, self.radius)
            if value:
                print(value[2])

        pygame.draw.circle(DISPLAY, self.color, self.pos, self.radius)

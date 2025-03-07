from settings import *

class Line():
    def __init__(self, p_ax, p_ay, p_bx, p_by):
        # Initialize the start and end points of the line using pygame.Vector2 for easy math operations
        self.start_point = pygame.Vector2(p_ax, p_ay)
        self.end_point = pygame.Vector2(p_bx, p_by)
    
    def draw(self):
        pygame.draw.line(DISPLAY,(255,255,255), self.start_point, self.end_point)

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
    
    def line_of_sight(self, obstacles):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1])
        angle_to_mouse = math.atan2(mouse_pos.y - self.rect.y, mouse_pos.x - self.rect.x) # Ensures it Follows Mouse
        rays = []
        intersection_groups = []
        polygon_points = []
        length = 200

        # Create Rays based on an Angle
        for angle in range(-20, 21, 1):
            radian = angle_to_mouse + math.radians(angle)
            start_point = pygame.Vector2(self.rect.x, self.rect.y)
            end_point = pygame.Vector2(
                self.pos.x + length * (math.cos(radian)),  # X value
                self.pos.y + length * (math.sin(radian))  # Y value
            )
            rays.append(Line(start_point.x ,start_point.y, end_point.x, end_point.y))
        polygon_points.append(rays[0].start_point) # After creating rays, append the first ray to the points

        for i, ray in enumerate(rays):
            closest_point = None
            closest_obstacle = None
            closest_distance = float('inf')

            # Check If Obstacle is Only One:
            if isinstance(obstacles, list):
                for obstacle in obstacles: # On the set of obstacle, check if ray hits either of them
                    point = ray.intersect(obstacle) # If there is an intersecting point, return that value
                    
                    # If a Point Exist
                    if point:
                        # Handle Point Intersection 
                        distance = (point - ray.start_point).length() # Store the distance
                        if distance < closest_distance: # Check if that distance is the closest
                            closest_distance = distance
                            closest_point = point
                            closest_obstacle = obstacle

                if closest_point:
                    polygon_points.append(closest_point)
                    intersection_groups.append((i, closest_point, closest_obstacle))
                else:
                    polygon_points.append(ray.end_point)
                
                if len(polygon_points) > 2:  # Need at least 3 points for a polygon
                    # Draw Visible Line
                    pygame.gfxdraw.filled_polygon(DISPLAY, polygon_points, (255, 255, 0, 100))
                    # Linestart → Lineend → Next_Linestart → Next_Lineend → Linestart (closing the shape)
            
                # Handle Intersection Info
                self.draw_visible_edges(intersection_groups) # Pass the Collection of Intersecting Point
            else:
                intersection_point = ray.intersect(obstacles)
                
                if intersection_point:
                    polygon_points.append(intersection_point)
                    intersection_groups.append(intersection_point)
                else:
                    polygon_points.append(ray.end_point)

                if len(intersection_groups) > 2:
                    pygame.draw.line(DISPLAY, 'white', intersection_groups[0], intersection_groups[-1], 5)
                if len(polygon_points) > 2:
                    pygame.gfxdraw.filled_polygon(DISPLAY, polygon_points, (255, 255, 0, 20))
                    

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

        # Base Movement
        self.pos += self.direction * dt * 300
        self.rect.center = self.pos
    
    def update(self,dt,other_line):
        self.move(dt)
        pygame.gfxdraw.circle(DISPLAY, self.rect.x,self.rect.y,self.radius,self.color)
        self.line_of_sight(other_line)

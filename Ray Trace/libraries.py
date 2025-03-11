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
        self.color = (255,255,255) 

        # Ray Properties
        self.ray_length = 200
        self.ray_angle = 90
        self.ray_step = 1
        self.show_ray_lines = False

        # Create Rays
        self.line_of_sight = self.create_rays(self.ray_angle, self.ray_length, self.ray_step)
        self.fov = self.create_rays(360, 30, 20)
        
    def create_rays(self, ray_angle=90, ray_length=100, ray_step=10):
        """
            Creates and returns a list of ray segments originating from the object's position.
            
            Args:
                ray_angle (float): The total spread of rays in degrees (e.g., 90°).
                ray_length (float): The length of each ray.
                ray_step (float): The angle difference between each ray.
            
            Returns:
                list: A list of Line objects representing the rays.
        """

        rays = [] # List to store generated rays
        num_rays = int(ray_angle / ray_step) + 1 # Calculate the number of rays based on step size

        for i in range(num_rays):
            # Calculate the angle offset for each ray (starting from -half the angle spread)
            angle_offset = -ray_angle / 2 + i * ray_step
            radian = math.radians(angle_offset)  # Convert angle to radians

            # Calculate the end point of the ray using trigonometry (cosine and sine for x, y)
            end_point = pygame.Vector2(self.rect.x + ray_length * (math.cos(radian)),
                                       self.rect.y + ray_length * (math.sin(radian)))
            
            # Create a Line object from the starting point (self.pos) to the calculated end point
            rays.append(Line(self.pos.x, self.pos.y, end_point.x, end_point.y))

        return rays

    def update_rays(self, rays, ray_angle, ray_length, mouse_follow=False):
        """
            Updates the position and direction of rays based on the object's position 
            and an optional mouse-following behavior.

            Args:
                rays (list): List of Line objects representing the rays.
                ray_angle (float): Total spread of rays in degrees.
                ray_length (float): Length of each ray.
                mouse_follow (bool): If True, rays will follow the mouse position.
            """
        
        if mouse_follow:
            # Get mouse position as a Vector2
            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            # Calculate angle from the object position to the mouse position using atan2
            mouse_angle = math.atan2(mouse_pos.y - self.pos.y, mouse_pos.x - self.pos.x)
        else:
            # If not following mouse, set default values
            mouse_pos, mouse_angle = 0, 0
        
        for i, ray in enumerate(rays):
            # Calculate the angle offset for each ray (starting from -half the angle spread)
            angle_offset = -ray_angle / 2 + i * (ray_angle / (len(rays) - 1))
            # Add the base angle (mouse_angle) to the offset
            radian = mouse_angle + math.radians(angle_offset)

            # Set the ray's starting point to the object's position
            ray.start_point = self.pos
            # Calculate the end point of the ray using trigonometry (cosine and sine for x, y)
            ray.end_point   = pygame.Vector2(
                self.pos.x + ray_length * math.cos(radian),
                self.pos.y + ray_length * math.sin(radian)
            )

    def handle_rays(self, ray, angle, ray_length, mouse_follow=False, show_lines=False, obstacles=None):
        """
            Handles the raycasting process, including updating rays, detecting intersections,
            and drawing the resulting visibility polygon.

            Args:
                ray (list): List of Line objects representing the rays.
                angle (float): Total spread of rays in degrees.
                ray_length (float): Maximum length of each ray.
                mouse_follow (bool): If True, rays will follow the mouse position.
                show_lines (bool): If True, shows the rays as lines for visualization.
                obstacles (list or object): List of obstacles (or a single obstacle) that rays can intersect.
        """

        # Step 1: Update ray positions
        self.update_rays(ray, angle, ray_length, mouse_follow)

        # Step 2: Initialize data for tracking intersections and polygon points
        intersection_groups = []    # Tracks intersected points and their obstacles
        polygon_points = []         # List of points that will form the visibility polygon
        polygon_points.append(ray[0].start_point)  # First polygon point is the ray's starting point

        # Step 3: Ray-Obstacle Intersection Logic
        for i, line in enumerate(ray):
            closest_point = None           # Tracks the nearest intersection point
            closest_obstacle = None        # Tracks the obstacle associated with the nearest point
            closest_distance = float('inf')  # Starts with infinity to ensure finding the closest point

            # Step 4: Ensure `obstacles` is iterable (handles both list and single obstacle cases)
            obstacle_list = (
                obstacles if isinstance(obstacles, list)
                else [obstacles] if obstacles is not None
                else []
            )

            # Step 5: Check each obstacle for intersections with the current ray
            for obstacle in obstacle_list:
                point = line.intersect(obstacle)  # Calculate intersection point

                if point:
                    # Calculate distance between ray start and intersection point
                    distance = (point - line.start_point).length()

                    # Step 6: Track the closest intersection point
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_point = point
                        closest_obstacle = obstacle

            # Step 7: Append the closest point (or endpoint if no intersection)
            if closest_point:
                polygon_points.append(closest_point)  # Closest point becomes part of the visibility polygon
                intersection_groups.append((i, closest_point, closest_obstacle))
            else:
                polygon_points.append(line.end_point)

        # Step 8: Draw the visibility polygon if it has enough points
        if len(polygon_points) > 2:  # At least 3 points are required for a valid polygon
            self.draw_rays(polygon_points, show_lines)  # Draws the filled polygon (or outlines if specified)
            self.draw_visible_edges(intersection_groups)  # Draws edges connecting intersection points
            
    def draw_rays(self, polygon_points, show_line=False, ray_color=(255, 255, 150, 50)):
        if show_line or self.show_ray_lines:
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

    def handle_collisions(self, lines=None):
        for line in lines:
            collision_point = line.collide(self.pos, self.radius)
            if collision_point is not None:
                collision_vector = pygame.Vector2(self.pos - collision_point)
                collision_vector = collision_vector.normalize()
                
                self.pos = collision_point + collision_vector * self.radius

    def move(self,dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction

        # Base Movement
        self.pos += self.direction * dt * 300
        self.rect.center = self.pos
    
    def update(self,dt,lines=None):
        self.move(dt)
        self.handle_rays(self.line_of_sight,self.ray_angle, self.ray_length, True, False, lines)
        self.handle_rays(self.fov,360, 50, False, False, lines)
        self.handle_collisions(lines)

        pygame.draw.circle(DISPLAY, self.color, self.pos, self.radius)


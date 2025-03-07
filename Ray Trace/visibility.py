import pygame, sys, math
from pygame import gfxdraw
import pygame.gfxdraw
import pygame.gfxdraw

# Initialize
pygame.init()
WIDTH, HEIGHT = 800,800
display = pygame.display.set_mode((WIDTH,HEIGHT))

# Variables
running = True
clock = pygame.time.Clock()

# Classes
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
        length = 1000

        # Create Rays based on an Angle
        for angle in range(0, 361, 1):
            radian = math.radians(angle)
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
                """ Store additional information about the intersection in intersection_groups.
                -- This includes:
                # i: The index of the ray that caused this intersection.
                      This helps us keep track of the order in which rays were cast.
                # closest_point: The point where the ray intersected the obstacle.
                     This is the actual location of the intersection in the scene.
                # closest_obstacle: The obstacle that was hit by the ray.
                      This allows us to group intersections by obstacle later."""
            else:
                polygon_points.append(ray.end_point)
            
        if len(polygon_points) > 2:  # Need at least 3 points for a polygon
            # Draw Visible Line
            pygame.gfxdraw.filled_polygon(display, polygon_points, (255, 255, 0, 100))
            # Linestart → Lineend → Next_Linestart → Next_Lineend → Linestart (closing the shape)
        
        # Handle Intersection Info
        self.draw_visible_edges(intersection_groups) # Pass the Collection of Intersecting Point

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
                        pygame.draw.line(display, 'white', current_point, next_point, 5)


    def move(self,dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])

        # Base Movement
        self.pos += self.direction * dt * 300
        self.rect.center = self.pos
    
    def update(self,dt,other_line):
        self.move(dt)
        pygame.gfxdraw.circle(display, self.rect.x,self.rect.y,self.radius,self.color)
        self.line_of_sight(other_line)

class Line:
    def __init__(self, p_ax, p_ay, p_bx, p_by):
        # Initialize the start and end points of the line using pygame.Vector2 for easy math operations
        self.start_point = pygame.Vector2(p_ax, p_ay)
        self.end_point = pygame.Vector2(p_bx, p_by)\
    
    def draw(self):
        pygame.draw.line(display,(255,255,255), self.start_point, self.end_point)

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
        
player = Observer(20,20,15,15)
lines = [Line(100,200,100,400),
         Line(100,600,400,600),
         Line(100,100,600,100)]
while running:
    dt = clock.tick() / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    display.fill('grey')

    player.update(dt,lines)

    pygame.display.update()
pygame.quit()
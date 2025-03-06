import pygame, sys, math

# Initialize
pygame.init()
WIDTH, HEIGHT = 600, 600
display = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Line Interpolation')

# Variables
running = True
clock = pygame.time.Clock()

class Line:
    def __init__(self, p_ax, p_ay, p_bx, p_by):
        self.start_point = pygame.Vector2(p_ax, p_ay)
        self.end_point = pygame.Vector2(p_bx, p_by)

    def draw(self, current_line,next_line, thickness):
        pygame.draw.line(display, 'white', current_line, next_line,5)

    def intersect(self, other_line):
        # Unpack Line Coordinates
        x1, y1 = self.start_point
        x2, y2 = self.end_point
        x3, y3 = other_line.start_point
        x4, y4 = other_line.end_point

        # Calculate Denominator
        denominator = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)

        # Check if Parallel
        if denominator == 0:
            return None

        # Calculate Intersection Parameters
        ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denominator
        ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denominator

        # Check If Intersect
        if 0 <= ua <= 1 and 0 <= ub <= 1:
            # Calculate Intersection Point
            x = x1 + ua * (x2 - x1)
            y = y1 + ua * (y2 - y1)
            return pygame.Vector2(x, y)
        
soft_yellow = (255, 255, 100, 200)

class Observer:
    def __init__(self):
        self.surface = pygame.Surface((32, 32), pygame.SRCALPHA)  # Transparent surface
        self.rect = self.surface.get_frect(center= (WIDTH / 2, HEIGHT / 2))
        self.radius = 15
        self.pos = pygame.Vector2(self.rect.center)  # Corrected position initialization
        self.direction = pygame.Vector2(0, 0)

    def move(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])

        # Apply movement
        self.pos += self.direction * dt * 100
        self.rect.center = self.pos  # Update rect position

    def ray(self, other_lines):
        line_objects = []
        for angle in range(0, 360, 1):
            radian = math.radians(angle)
            start_point = self.pos
            end_point = pygame.Vector2(
                self.pos.x + self.radius * (100 * math.cos(radian)), # X Value
                self.pos.y + self.radius * (100 * math.sin(radian))  # y Value
            )
            line_objects.append(Line(start_point.x,start_point.y,end_point.x,end_point.y))
        
    # Draw polygons between adjacent rays
        for i, line in enumerate(line_objects):
            # Get next line (wrap around to 0 if at the end)
            next_index = (i + 1) % len(line_objects)
            next_line = line_objects[next_index]
            
            # Find intersections for current and next ray
            current_intersection = None
            next_intersection = None
            min_distance_current = float('inf')
            min_distance_next = float('inf')
            
            # Check all obstacle lines for intersections
            for obstacle in other_lines:
                # Check current ray intersection
                point = line.intersect(obstacle)
                if point:
                    distance = (point - line.start_point).length()
                    if distance < min_distance_current:
                        min_distance_current = distance
                        current_intersection = point
                
                # Check next ray intersection
                point = next_line.intersect(obstacle)
                if point:
                    distance = (point - next_line.start_point).length()
                    if distance < min_distance_next:
                        min_distance_next = distance
                        next_intersection = point
            
            # Draw polygon based on intersection results
            if current_intersection and next_intersection:
                # Both rays hit obstacles
                obstacle.draw(current_intersection,next_intersection,2)
                pygame.draw.polygon(display, soft_yellow, [
                    line.start_point, 
                    current_intersection, 
                    next_intersection,
                    next_line.start_point
                ])
            elif current_intersection:
                # Only current ray hit an obstacle
                pygame.draw.polygon(display, soft_yellow, [
                    line.start_point, 
                    current_intersection, 
                    next_line.end_point,
                    next_line.start_point
                ])
            elif next_intersection:
                # Only next ray hit an obstacle
                pygame.draw.polygon(display, soft_yellow, [
                    line.start_point, 
                    line.end_point, 
                    next_intersection,
                    next_line.start_point
                ])
            else:
                # No obstacles hit by either ray
                pygame.draw.polygon(display, soft_yellow, [
                    line.start_point, 
                    line.end_point, 
                    next_line.end_point,
                    next_line.start_point
                ])
                    

    def update(self, dt, line):
        self.move(dt)
        self.ray(line)
        pygame.draw.circle(display, 'white', self.rect.center, self.radius)  # Draw observer


# Initialize observer
player = Observer()
# Create multiple lines with different positions & angles
lines = [
    Line(100,50,100,200),
    Line(50, 400, 200, 400),
    Line(200, 200, 200, 350),
    Line(300, 500, 100, 550),
    Line(500, 250, 300, 400)
]


# Main loop
running = True
while running:
    dt = clock.tick(60) / 1000  # Delta time for smooth movement
    display.fill((0, 0, 0))  # Clear screen

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player.update(dt, lines)

    pygame.display.flip()

pygame.quit()

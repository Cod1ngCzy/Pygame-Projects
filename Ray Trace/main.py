import pygame, sys, math

# Initialize Pygame
pygame.init()

# Set the width and height of the display window
WIDTH, HEIGHT = 600, 600
display = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Ray Casting')  # Set the window title

# Variables
running = True  # Control the main loop
clock = pygame.time.Clock()  # Create a clock object to control frame rate

# Define a class to represent a line segment
class Line:
    def __init__(self, p_ax, p_ay, p_bx, p_by):
        # Initialize the start and end points of the line using pygame.Vector2 for easy math operations
        self.start_point = pygame.Vector2(p_ax, p_ay)
        self.end_point = pygame.Vector2(p_bx, p_by)

    def draw(self, current_line, next_line, thickness):
        # Draw a line on the display surface
        pygame.draw.line(display, 'white', current_line, next_line, 5)

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

# Define a soft yellow color with transparency
soft_yellow = (255, 255, 150, 255)

# Define a class to represent the observer (player)
class Observer:
    def __init__(self):
        # Create a transparent surface for the observer
        self.surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        # Get the rectangle of the surface and center it in the display
        self.rect = self.surface.get_frect(center=(WIDTH / 2, HEIGHT / 2))
        self.radius = 15  # Radius of the observer
        self.pos = pygame.Vector2(self.rect.center)  # Position of the observer
        self.direction = pygame.Vector2(0, 0)  # Direction of movement

    def move(self, dt):
        # Get the state of the keyboard keys
        keys = pygame.key.get_pressed()
        # Calculate the direction vector based on key presses
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])

        # Update the position based on the direction and delta time
        self.pos += self.direction * dt * 100
        self.rect.center = self.pos  # Update the rectangle position

    def ray(self, other_lines):
        # Create a list to store ray lines
        line_objects = []
        # Loop through angles from 0 to 360 degrees
        for angle in range(0, 360, 1):
            radian = math.radians(angle)  # Convert angle to radians
            start_point = self.pos  # Start point of the ray is the observer's position
            # Calculate the end point of the ray based on the angle
            end_point = pygame.Vector2(
                self.pos.x + self.radius * (100 * math.cos(radian)),  # X value
                self.pos.y + self.radius * (100 * math.sin(radian))  # Y value
            )
            # Create a Line object for the ray and add it to the list
            line_objects.append(Line(start_point.x, start_point.y, end_point.x, end_point.y))
        
        # Draw polygons between adjacent rays
        for i, line in enumerate(line_objects):
            # Get the next line (wrap around to 0 if at the end)
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
                # Draw the visibility polygon
                pygame.draw.line(display, soft_yellow, line.start_point, current_intersection)
                #pygame.draw.polygon(display, soft_yellow, [line.start_point, current_intersection, next_intersection,next_line.start_point])
            elif current_intersection:
                # Only current ray hit an obstacle
                pygame.draw.line(display, soft_yellow, line.end_point, current_intersection)
               # pygame.draw.polygon(display, soft_yellow, [line.start_point, current_intersection, next_line.end_point,next_line.start_point])
            elif next_intersection:
                # Only next ray hit an obstacle
                pygame.draw.line(display, soft_yellow, line.start_point, next_intersection)
                #pygame.draw.polygon(display, soft_yellow, [line.start_point, line.end_point, next_intersection,next_line.start_point])
            else:
                # No obstacles hit by either ray
                pygame.draw.line(display, soft_yellow, line.start_point, line.end_point)
                #pygame.draw.polygon(display, soft_yellow, [line.start_point, line.end_point, next_line.end_point,next_line.start_point])
                    
    def update(self, dt, line):
        # Update the observer's position and draw the rays
        self.move(dt)
        self.ray(line)
        # Draw the observer as a circle
        pygame.draw.circle(display, 'white', self.rect.center, self.radius)

# Initialize the observer (player)
player = Observer()

# Create multiple lines with different positions & angles
lines = [
    Line(100, 50, 100, 200),
    Line(50, 400, 200, 400),
    Line(200, 200, 200, 350),
    Line(300, 500, 100, 550),
    Line(500, 250, 300, 400)
]

# Main loop
running = True
while running:
    dt = clock.tick(60) / 1000  # Calculate delta time for smooth movement
    display.fill('grey')  # Clear the screen with black

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  # Exit the loop if the window is closed

    # Update the observer and draw everything
    player.update(dt, lines)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
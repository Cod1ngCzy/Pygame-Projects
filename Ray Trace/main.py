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

    def draw(self, other_line=None):
        if other_line:
            point = self.intersect(other_line)

        if other_line and point:
            pygame.draw.line(display, 'white', self.start_point, point)
        else:
            pygame.draw.line(display, 'white', self.start_point, self.end_point)

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


class Observer:
    def __init__(self):
        self.surface = pygame.Surface((32, 32), pygame.SRCALPHA)  # Transparent surface
        self.rect = self.surface.get_frect(center=(WIDTH / 2, HEIGHT / 2))
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

    def draw_v_shape(self, line):
        """Draws a 'V' shape that follows the mouse direction."""
        center = pygame.Vector2(self.rect.center)
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

        # Get direction vector and angle
        direction = (mouse_pos - center).normalize()
        angle = math.atan2(direction.y, direction.x)  # Angle in radians
        length = 500  # V arm length
        angle_offset = math.radians(20)  # Angle difference between V arms

        # Calculate rotated points
        point1_start = center + pygame.Vector2(length * math.cos(angle - angle_offset),
                                               length * math.sin(angle - angle_offset))
        point1_end = center + pygame.Vector2(length * math.cos(angle - angle_offset + 0.1),  # Slight angle variation
                                             length * math.sin(angle - angle_offset + 0.1))

        point2_start = center + pygame.Vector2(length * math.cos(angle + angle_offset),
                                            length * math.sin(angle + angle_offset))
        point2_end = center + pygame.Vector2(length * math.cos(angle + angle_offset + 0.1),  # Slight angle variation
                                            length * math.sin(angle + angle_offset + 0.1))
        
        point_a = Line(self.rect.x,self.rect.y,point1_end.x,point1_end.y)
        point_b = Line(self.rect.x,self.rect.y,point2_end.x,point2_end.y)

        endp1 = point_a.intersect(line)
        endp2 = point_b.intersect(line)

        if endp1 and endp2:
            pygame.draw.line(display, 'white', endp1, point_a.start_point)
            pygame.draw.line(display, 'white', endp2, point_b.start_point)
            pygame.draw.polygon(display, 'yellow', [point_a.start_point, point_b.start_point, endp1, endp2])
        elif endp1:
            pygame.draw.line(display, 'white', endp1, point_a.start_point)
            point_b.draw()
            pygame.draw.polygon(display, 'yellow', [point_a.start_point, point_b.start_point, endp1, point_b.end_point])
        elif endp2:
            pygame.draw.line(display, 'white', endp2, point_b.start_point)
            point_a.draw()
            pygame.draw.polygon(display, 'yellow', [point_a.start_point, point_b.start_point, point_a.end_point, endp2])
        else:
            point_a.draw()
            point_b.draw()
            pygame.draw.polygon(display, 'yellow', [point_a.start_point, point_b.start_point, point_a.end_point, point_b.end_point])


    def update(self, dt, line):
        self.move(dt)
        self.draw_v_shape(line)
        pygame.draw.circle(display, 'white', self.rect.center, self.radius)  # Draw observer


# Initialize observer
player = Observer()
line = Line(100,50,100,200)

# Main loop
running = True
while running:
    dt = clock.tick(60) / 1000  # Delta time for smooth movement
    display.fill((0, 0, 0))  # Clear screen

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player.update(dt, line)
    line.draw()
    pygame.display.flip()

pygame.quit()

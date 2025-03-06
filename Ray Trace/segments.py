import pygame
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BG_COLOR = (30, 30, 30)  # Dark gray
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Visibility Algorithm")

# Clock for controlling the frame rate
clock = pygame.time.Clock()


class Segment():
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect((x, y, width, height))
        self.pos = pygame.Vector2(x, y)
        self.corners = self.update_corners()
        self.corner_radius = 5
    
    def show_rect_properties(self, circle=False, lines=False, color=WHITE):
        if lines:
            pygame.draw.line(screen, color, self.corners[0], self.corners[1])
            pygame.draw.line(screen, color, self.corners[1], self.corners[3])
            pygame.draw.line(screen, color, self.corners[2], self.corners[3])
            pygame.draw.line(screen, color, self.corners[2], self.corners[0]) 
        if circle:
            for corner in self.corners:
                pygame.draw.circle(screen, RED, corner, self.corner_radius)

    def update_corners(self):
        self.corners = [pygame.Vector2(self.rect.left, self.rect.top),
                        pygame.Vector2(self.rect.right, self.rect.top),
                        pygame.Vector2(self.rect.left, self.rect.bottom),
                        pygame.Vector2(self.rect.right, self.rect.bottom)]
        return self.corners

    def handle_position(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0]:  # Dragging
                self.rect.center = mouse_pos
                self.update_corners()
    
    def update(self):
        self.handle_position()
        self.show_rect_properties(True, True)


class Observer:
    def __init__(self):
        self.radius = 10  
        self.pos = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)  
        self.direction = pygame.Vector2(0, 0)  

    def move(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        self.pos += self.direction * dt * 200  # Move speed

    def get_sorted_endpoints(self, segments):
        points = []
        for segment in segments:
            for px, py in segment.corners:
                angle = math.atan2(py - self.pos.y, px - self.pos.x)
                points.append((angle, px, py))
        points.sort()  # Sort by angle
        return points

    def cast_rays(self, segments):
        sorted_points = self.get_sorted_endpoints(segments)
        rays = []
        for angle, px, py in sorted_points:
            for offset in [-0.0001, 0, 0.0001]:  # Slight variation to avoid gaps
                ang = angle + offset
                dx = math.cos(ang) * 1000
                dy = math.sin(ang) * 1000
                rays.append((self.pos.x, self.pos.y, self.pos.x + dx, self.pos.y + dy))
        return rays

    def update(self, dt, segments):
        self.move(dt)
        rays = self.cast_rays(segments)

        # Draw observer
        pygame.draw.circle(screen, WHITE, (int(self.pos.x), int(self.pos.y)), self.radius)

        # Draw rays
        for x1, y1, x2, y2 in rays:
            pygame.draw.line(screen, RED, (x1, y1), (x2, y2), 1)


# Create objects
segments = [
    Segment(200, 150, 100, 100),
    Segment(400, 250, 120, 80),
    Segment(600, 100, 100, 150)
]
player = Observer()


# Main game loop
def main():
    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(BG_COLOR)

        for box in segments:
            box.update()
        player.update(dt, segments)

        pygame.display.flip()


if __name__ == "__main__":
    main()

import pygame
import math
import sys
from pygame import gfxdraw

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
YELLOW = (255, 255, 0)
GREEN = (100, 200, 50)
VISIBILITY_COLOR = (255, 255, 100, 100)  # Semi-transparent green

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Visibility Algorithm")

# Create a separate surface for drawing the visibility polygon
visibility_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

# Clock for controlling the frame rate
clock = pygame.time.Clock()


class Segment():
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect((x, y, width, height))
        self.pos = pygame.Vector2(x, y)
        self.corners = self.update_corners()
        self.corner_radius = 5
        self.dragging_corner = None
        self.edges = []
        self.update_edges()
    
    def show_rect_properties(self, circle=False, lines=False, color=WHITE):
        pygame.draw.rect(screen, GREEN, self.rect)
        
        if lines:
            for edge in self.edges:
                pygame.draw.line(screen, color, edge[0], edge[1], 2)
        
        if circle:
            for corner in self.corners:
                pygame.draw.circle(screen, YELLOW, corner, self.corner_radius)

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
                pygame.draw.circle(screen, (255, 255, 0), corner, self.corner_radius)
                
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


class Observer:
    def __init__(self):
        self.radius = 15
        self.pos = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.direction = pygame.Vector2(0, 0)
        self.visibility_polygon = []

    def move(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        self.pos += self.direction * dt * 200  # Move speed
        
        # Keep player within screen bounds
        self.pos.x = max(self.radius, min(self.pos.x, SCREEN_WIDTH - self.radius))
        self.pos.y = max(self.radius, min(self.pos.y, SCREEN_HEIGHT - self.radius))

    def calculate_endpoints(self, segments):
        endpoints = []
        
        # Get all corners from all segments
        for segment in segments:
            for corner in segment.corners:
                # Calculate the angle from observer to corner
                angle = math.atan2(corner.y - self.pos.y, corner.x - self.pos.x)
                
                # Add a tiny offset in both directions to handle edge cases
                for offset in [-0.0001, 0, 0.0001]:
                    endpoints.append((angle + offset, corner))
        
        # Sort endpoints by angle
        endpoints.sort(key=lambda x: x[0])
        return endpoints

    def cast_ray(self, angle, segments):
        # Create a ray that extends far beyond the screen
        ray_length = max(SCREEN_WIDTH, SCREEN_HEIGHT) * 2
        end_point = pygame.Vector2(
            self.pos.x + math.cos(angle) * ray_length,
            self.pos.y + math.sin(angle) * ray_length
        )
        
        closest_intersection = None
        closest_distance = float('inf')
        
        # Check for intersections with all segment edges
        for segment in segments:
            for edge in segment.edges:
                # Line segment intersection algorithm
                x1, y1 = self.pos
                x2, y2 = end_point
                x3, y3 = edge[0]
                x4, y4 = edge[1]
                
                # Calculate denominator
                den = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
                
                # Check if lines are parallel
                if den == 0:
                    continue
                
                # Calculate ua and ub
                ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / den
                ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den
                
                # Check if intersection is within both line segments
                if 0 <= ua <= 1 and 0 <= ub <= 1:
                    # Calculate intersection point
                    intersection_x = x1 + ua * (x2 - x1)
                    intersection_y = y1 + ua * (y2 - y1)
                    intersection = pygame.Vector2(intersection_x, intersection_y)
                    
                    # Calculate distance to intersection
                    distance = self.pos.distance_to(intersection)
                    
                    # Keep track of closest intersection
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_intersection = intersection
        
        # Return the closest intersection point or the end point if no intersection
        return closest_intersection if closest_intersection else end_point

    def calculate_visibility(self, segments):
        # Clear the visibility polygon
        self.visibility_polygon = []
        
        # Get endpoints sorted by angle
        endpoints = self.calculate_endpoints(segments)
        
        # For each endpoint, cast a ray and find the closest intersection
        for angle, _ in endpoints:
            intersection = self.cast_ray(angle, segments)
            self.visibility_polygon.append(intersection)
    
    def draw_visibility(self):
        # Clear the visibility surface
        visibility_surface.fill((0, 0, 0, 0))
        
        if len(self.visibility_polygon) > 2:
            # Draw the visibility polygon
            points = [(int(point.x), int(point.y)) for point in self.visibility_polygon]
            points.insert(0, (int(self.pos.x), int(self.pos.y)))  # Add observer position as the first point
            
            # Draw filled polygon with semi-transparent color
            gfxdraw.filled_polygon(visibility_surface, points, VISIBILITY_COLOR)
            
            # Draw outline
            gfxdraw.aapolygon(visibility_surface, points, WHITE)
        
        # Draw rays for debugging
        for point in self.visibility_polygon:
            pygame.draw.line(visibility_surface, (255, 255, 0, 100), self.pos, point, 1)

    def update(self, dt, segments):
        self.move(dt)
        self.calculate_visibility(segments)
        self.draw_visibility()
        
        # Draw observer
        pygame.draw.circle(screen, YELLOW, (int(self.pos.x), int(self.pos.y)), self.radius)


# Create objects
segments = [
    Segment(200, 150, 100, 100),
    Segment(500, 300, 100, 100),
    Segment(300, 400, 100, 100),
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Add a new segment
                    segments.append(Segment(400, 200, 80, 80))

        screen.fill(BG_COLOR)

        # Update and draw segments
        for box in segments:
            box.update()
        
        # Update and draw player and visibility
        player.update(dt, segments)
        
        # Blit the visibility surface onto the screen
        screen.blit(visibility_surface, (0, 0))

        # Display instructions
        font = pygame.font.SysFont(None, 24)
        text = font.render("WASD: Move | Click & Drag: Move Segments | Space: Add Segment", True, WHITE)
        screen.blit(text, (10, 10))
        
        # Update the display
        pygame.display.flip()


if __name__ == "__main__":
    main()
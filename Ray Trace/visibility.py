import pygame
import math
import sys

# Screen dimensions
WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (50, 60, 70)

# Polygon and ray settings
RAY_COLOR = (255, 255, 0)
POLYGON_COLOR = (0, 255, 0)
PLAYER_COLOR = (255, 255, 0)

class Segment:
    def __init__(self, x1, y1, x2, y2):
        self.start = pygame.Vector2(x1, y1)
        self.end = pygame.Vector2(x2, y2)

    def draw(self, screen):
        pygame.draw.line(screen, (255, 255, 255), self.start, self.end, 2)

class VisibilityPolygon:
    def __init__(self, screen):
        self.screen = screen
        self.segments = []
        self.player_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
        
        # Create boundary segments
        self.create_boundary_segments()
        
        # Add some obstacle segments
        self.add_obstacles()

    def create_boundary_segments(self):
        # Screen boundary segments
        self.segments.extend([
            Segment(0, 0, WIDTH, 0),
            Segment(WIDTH, 0, WIDTH, HEIGHT),
            Segment(WIDTH, HEIGHT, 0, HEIGHT),
            Segment(0, HEIGHT, 0, 0)
        ])

    def add_obstacles(self):
        # Add rectangular obstacles
        obstacles = [
            (100, 100, 200, 200),
            (500, 300, 600, 400),
            (300, 400, 400, 500)
        ]
        
        for x1, y1, x2, y2 in obstacles:
            # Create rectangle segments
            self.segments.extend([
                Segment(x1, y1, x2, y1),
                Segment(x2, y1, x2, y2),
                Segment(x2, y2, x1, y2),
                Segment(x1, y2, x1, y1)
            ])

    def get_intersection(self, ray_origin, ray_angle, segments):
        closest_intersection = None
        min_distance = float('inf')

        for segment in segments:
            # Ray-segment intersection calculation
            x1, y1 = ray_origin.x, ray_origin.y
            x2 = x1 + math.cos(ray_angle) * 2000
            y2 = y1 + math.sin(ray_angle) * 2000

            x3, y3 = segment.start.x, segment.start.y
            x4, y4 = segment.end.x, segment.end.y

            # Denominator for line intersection
            denominator = ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1))
            
            if denominator == 0:
                continue  # Lines are parallel

            ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denominator
            ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denominator

            # Check if intersection is within line segments
            if 0 <= ua <= 1 and 0 <= ub <= 1:
                intersection_x = x1 + ua * (x2 - x1)
                intersection_y = y1 + ua * (y2 - y1)
                intersection = pygame.Vector2(intersection_x, intersection_y)
                
                distance = (intersection - ray_origin).length()
                
                if distance < min_distance:
                    min_distance = distance
                    closest_intersection = intersection

        return closest_intersection

    def calculate_visibility_polygon(self, segments, beam_angle, beam_width):
        visibility_points = []
        
        # Calculate min and max angles for the flashlight beam
        min_beam_angle = beam_angle - beam_width / 2
        max_beam_angle = beam_angle + beam_width / 2
        
        # Cast rays at segment endpoints and slightly offset angles
        unique_angles = set()
        for segment in segments:
            angle_to_start = math.atan2(segment.start.y - self.player_pos.y, 
                                         segment.start.x - self.player_pos.x)
            angle_to_end = math.atan2(segment.end.y - self.player_pos.y, 
                                       segment.end.x - self.player_pos.x)
            
            # Only add angles within the beam range
            if min_beam_angle <= angle_to_start <= max_beam_angle:
                unique_angles.add(angle_to_start)
            if min_beam_angle <= angle_to_end <= max_beam_angle:
                unique_angles.add(angle_to_end)

        # Add beam boundary angles
        unique_angles.add(min_beam_angle)
        unique_angles.add(max_beam_angle)

        # Calculate intersection points for each angle
        for angle in sorted(unique_angles):
            # Only process angles within the beam
            if min_beam_angle <= angle <= max_beam_angle:
                intersection = self.get_intersection(self.player_pos, angle, segments)
                if intersection:
                    visibility_points.append(intersection)

        return visibility_points

    def draw(self):
        # Draw segments
        for segment in self.segments:
            segment.draw(self.screen)

        # Get mouse angle for beam direction
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        beam_angle = math.atan2(mouse_pos.y - self.player_pos.y, 
                                 mouse_pos.x - self.player_pos.x)
        
        # Calculate visibility polygon with a narrow beam
        visibility_points = self.calculate_visibility_polygon(
            self.segments, 
            beam_angle,  # Direction of the beam
            math.radians(45)  # Width of the beam (45 degrees)
        )

        # Draw visibility polygon
        if len(visibility_points) > 2:
            # Ensure the player's position is the first point
            visibility_points.insert(0, self.player_pos)
            pygame.draw.polygon(self.screen, (255, 255, 0, 100), visibility_points, 0)

        # Draw player
        pygame.draw.circle(self.screen, PLAYER_COLOR, 
                           (int(self.player_pos.x), int(self.player_pos.y)), 5)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Visibility Polygon")
    clock = pygame.time.Clock()

    visibility_polygon = VisibilityPolygon(screen)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Move player with mouse
            if event.type == pygame.MOUSEMOTION:
                visibility_polygon.player_pos = pygame.Vector2(event.pos)

        screen.fill(BACKGROUND_COLOR)
        visibility_polygon.draw()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
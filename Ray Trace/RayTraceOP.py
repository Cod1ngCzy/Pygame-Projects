import pygame
import math

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ray Tracing Simulation")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Ray properties
RAY_LENGTH = 300
RAY_COUNT = 360
RAY_ANGLE_INCREMENT = 360 / RAY_COUNT

# Object (obstacle) properties
obstacles = [
    pygame.Rect(300, 250, 100, 100),
    pygame.Rect(500, 400, 150, 80),
]

# Function to cast a ray and check for collisions
def cast_ray(x, y, angle):
    # Convert angle to radians
    angle_rad = math.radians(angle)
    
    # Calculate the direction of the ray
    dx = math.cos(angle_rad)
    dy = math.sin(angle_rad)

    # Cast the ray until it hits an obstacle or reaches max length
    for length in range(1, RAY_LENGTH):
        ray_x = x + dx * length
        ray_y = y + dy * length
        
        # Check if ray hits any obstacle
        for obs in obstacles:
            if obs.collidepoint(ray_x, ray_y):
                return (ray_x, ray_y, length)  # Return the hit point and length
    return (x + dx * RAY_LENGTH, y + dy * RAY_LENGTH, RAY_LENGTH)  # No collision, return max distance

# Main loop
running = True
clock = pygame.time.Clock()
player_x, player_y = WIDTH // 2, HEIGHT // 2  # Ray source in the center of the screen

while running:
    screen.fill(BLACK)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw obstacles
    for obs in obstacles:
        pygame.draw.rect(screen, WHITE, obs)

    # Cast rays
    for angle in range(0, 360, int(RAY_ANGLE_INCREMENT)):
        end_x, end_y, hit_length = cast_ray(player_x, player_y, angle)

        # Change color based on distance
        if hit_length == RAY_LENGTH:
            pygame.draw.line(screen, GREEN, (player_x, player_y), (end_x, end_y), 1)  # No hit, green
        else:
            pygame.draw.line(screen, RED, (player_x, player_y), (end_x, end_y), 1)  # Hit, red

    # Draw the ray source
    pygame.draw.circle(screen, WHITE, (player_x, player_y), 5)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

import pygame
import math
import random

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Enhanced Ray Tracing Simulation")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# Light source position (can be moved with mouse)
light_pos = [WIDTH // 2, HEIGHT // 4]
light_radius = 20

# Spheres (position x, y, radius, color)
spheres = [
    [200, 400, 50, RED],
    [400, 450, 70, GREEN],
    [600, 350, 60, BLUE],
    [300, 280, 40, PURPLE],
    [500, 220, 35, CYAN]
]

# Ray properties
RAY_COUNT = 180  # Increased from 50 to 180 rays
ray_length = 2000  # Long enough to reach screen edges
ray_speed = 5
ray_intensity = 0.8  # Added for intensity falloff

# Physics properties
reflection_enabled = True
shadows_enabled = True
intensity_falloff_enabled = True

# Refraction indices
REFRACTION_INDEX = 1.5

# Function to calculate distance between two points
def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

# Function to normalize a vector
def normalize(vector):
    length = math.sqrt(vector[0]**2 + vector[1]**2)
    if length == 0:
        return [0, 0]
    return [vector[0]/length, vector[1]/length]

# Function to check ray intersection with sphere
def ray_sphere_intersect(ray_origin, ray_dir, sphere):
    sphere_pos = [sphere[0], sphere[1]]
    sphere_radius = sphere[2]
    
    # Vector from ray origin to sphere center
    oc = [ray_origin[0] - sphere_pos[0], ray_origin[1] - sphere_pos[1]]
    
    # Quadratic formula components
    a = ray_dir[0]**2 + ray_dir[1]**2
    b = 2 * (oc[0] * ray_dir[0] + oc[1] * ray_dir[1])
    c = oc[0]**2 + oc[1]**2 - sphere_radius**2
    
    # Discriminant
    discriminant = b**2 - 4 * a * c
    
    if discriminant < 0:
        return None  # No intersection
    
    # Calculate intersection point (nearest one)
    t = (-b - math.sqrt(discriminant)) / (2 * a)
    
    if t < 0:
        return None  # Intersection behind ray origin
    
    # Calculate intersection point
    intersection = [ray_origin[0] + t * ray_dir[0], ray_origin[1] + t * ray_dir[1]]
    
    # Calculate normal at intersection point
    normal = [intersection[0] - sphere_pos[0], intersection[1] - sphere_pos[1]]
    normal = normalize(normal)
    
    return {
        "point": intersection,
        "normal": normal,
        "distance": t,
        "sphere": sphere
    }

# Function to calculate ray intensity based on distance
def calculate_intensity(base_intensity, distance_traveled, falloff_factor=0.001):
    if not intensity_falloff_enabled:
        return base_intensity
    return base_intensity * math.exp(-falloff_factor * distance_traveled)

# Function to cast rays and handle reflections
def cast_ray(origin, direction, intensity=1.0, depth=0, max_depth=3):
    if depth > max_depth or intensity < 0.1:  # Stop if too dim or too many bounces
        return []
    
    # Find closest intersection
    closest_hit = None
    min_distance = float('inf')
    
    for sphere in spheres:
        hit = ray_sphere_intersect(origin, direction, sphere)
        if hit and hit["distance"] < min_distance:
            min_distance = hit["distance"]
            closest_hit = hit
    
    if not closest_hit:
        # Ray doesn't hit anything, draw straight line
        end_point = [origin[0] + ray_length * direction[0], 
                     origin[1] + ray_length * direction[1]]
        # Calculate color based on intensity
        color_intensity = int(255 * intensity)
        ray_color = (color_intensity, color_intensity, color_intensity)
        return [(origin, end_point, ray_color, 1)]
    
    lines = []
    hit_point = closest_hit["point"]
    
    # Calculate intensity at hit point
    hit_distance = closest_hit["distance"]
    hit_intensity = calculate_intensity(intensity, hit_distance)
    
    # Calculate color based on intensity
    color_intensity = int(255 * hit_intensity)
    ray_color = (color_intensity, color_intensity, color_intensity)
    
    # Add primary ray
    lines.append((origin, hit_point, ray_color, 2))
    
    if reflection_enabled and depth < max_depth:
        # Calculate reflection direction
        normal = closest_hit["normal"]
        dot_product = direction[0] * normal[0] + direction[1] * normal[1]
        reflection_dir = [
            direction[0] - 2 * dot_product * normal[0],
            direction[1] - 2 * dot_product * normal[1]
        ]
        
        # Slightly offset reflection start point to avoid self-intersection
        reflection_origin = [
            hit_point[0] + 0.001 * normal[0],
            hit_point[1] + 0.001 * normal[1]
        ]
        
        # Cast reflected ray with reduced intensity
        reflected_intensity = hit_intensity * 0.7  # Reflection loses some energy
        reflected_lines = cast_ray(reflection_origin, reflection_dir, reflected_intensity, depth + 1, max_depth)
        lines.extend(reflected_lines)
    
    # Check if point is in shadow
    if shadows_enabled:
        # Vector from hit point to light
        to_light = [light_pos[0] - hit_point[0], light_pos[1] - hit_point[1]]
        distance_to_light = math.sqrt(to_light[0]**2 + to_light[1]**2)
        to_light = normalize(to_light)
        
        # Shadow ray origin (slightly offset from hit point)
        shadow_origin = [
            hit_point[0] + 0.001 * closest_hit["normal"][0],
            hit_point[1] + 0.001 * closest_hit["normal"][1]
        ]
        
        # Check for shadow intersections
        in_shadow = False
        for sphere in spheres:
            shadow_hit = ray_sphere_intersect(shadow_origin, to_light, sphere)
            if shadow_hit and shadow_hit["distance"] < distance_to_light:
                in_shadow = True
                break
        
        # Calculate shadow ray intensity
        shadow_intensity = hit_intensity * 0.5  # Shadow rays dimmer
        shadow_color_intensity = int(120 * shadow_intensity)
        shadow_color = (shadow_color_intensity, shadow_color_intensity, shadow_color_intensity)
        
        # Draw shadow ray
        if in_shadow:
            shadow_end = shadow_hit["point"]
            lines.append((shadow_origin, shadow_end, shadow_color, 1))  # Dim gray for shadow rays
        else:
            # Draw line to light if not in shadow
            shadow_end = [shadow_origin[0] + distance_to_light * to_light[0],
                         shadow_origin[1] + distance_to_light * to_light[1]]
            # Yellow tint for light rays
            light_color = (int(255 * shadow_intensity), int(255 * shadow_intensity), int(180 * shadow_intensity))
            lines.append((shadow_origin, shadow_end, light_color, 1))
    
    return lines

# Main game loop
running = True
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# Animation parameters
animation_phase = 0
animation_speed = 0.01

# Performance tracking
fps_counter = 0
fps_time = 0
fps = 0

while running:
    start_time = pygame.time.get_ticks()
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Move light source with left mouse button
            if event.button == 1:
                light_pos = list(pygame.mouse.get_pos())
            # Add/remove spheres with right mouse button
            elif event.button == 3:
                new_pos = list(pygame.mouse.get_pos())
                # Check if clicked on existing sphere to remove it
                sphere_clicked = False
                for i, sphere in enumerate(spheres):
                    if distance(new_pos, [sphere[0], sphere[1]]) < sphere[2]:
                        spheres.pop(i)
                        sphere_clicked = True
                        break
                # Add new sphere if didn't click on existing one
                if not sphere_clicked and len(spheres) < 8:  # Cap at 8 spheres for performance
                    new_color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
                    spheres.append([new_pos[0], new_pos[1], random.randint(30, 60), new_color])
        elif event.type == pygame.MOUSEMOTION:
            # Drag light if mouse button is held
            if pygame.mouse.get_pressed()[0]:
                light_pos = list(pygame.mouse.get_pos())
        elif event.type == pygame.KEYDOWN:
            # Toggle reflection with R key
            if event.key == pygame.K_r:
                reflection_enabled = not reflection_enabled
            # Toggle shadows with S key
            elif event.key == pygame.K_s:
                shadows_enabled = not shadows_enabled
            # Toggle intensity falloff with I key
            elif event.key == pygame.K_i:
                intensity_falloff_enabled = not intensity_falloff_enabled
            # Add more rays with + key
            elif event.key == pygame.K_EQUALS and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                RAY_COUNT = min(RAY_COUNT + 20, 360)
            # Reduce rays with - key
            elif event.key == pygame.K_MINUS:
                RAY_COUNT = max(RAY_COUNT - 20, 20)
            # Reset scene with space
            elif event.key == pygame.K_SPACE:
                spheres = [
                    [200, 400, 50, RED],
                    [400, 450, 70, GREEN],
                    [600, 350, 60, BLUE],
                    [300, 280, 40, PURPLE],
                    [500, 220, 35, CYAN]
                ]
                light_pos = [WIDTH // 2, HEIGHT // 4]
    
    # Animation - move the spheres slightly
    animation_phase += animation_speed
    for i, sphere in enumerate(spheres):
        # Different movement patterns for each sphere
        if i % 3 == 0:
            sphere[1] = sphere[1] + math.sin(animation_phase + i) * 1.5
        elif i % 3 == 1:
            sphere[0] = sphere[0] + math.cos(animation_phase * 0.7 + i) * 1.5
        else:
            sphere[0] = sphere[0] + math.cos(animation_phase * 0.5 + i) * 1.0
            sphere[1] = sphere[1] + math.sin(animation_phase * 0.8 + i) * 1.0
    
    # Clear screen
    screen.fill(BLACK)
    
    # Draw spheres
    for sphere in spheres:
        pygame.draw.circle(screen, sphere[3], (int(sphere[0]), int(sphere[1])), sphere[2])
        # Draw outline
        pygame.draw.circle(screen, WHITE, (int(sphere[0]), int(sphere[1])), sphere[2], 1)
    
    # Draw light source with a glow effect
    for radius in range(light_radius, 0, -4):
        alpha = int(255 * (radius / light_radius))
        glow_color = (min(255, 200 + alpha), min(255, 200 + alpha), 100)
        pygame.draw.circle(screen, glow_color, (int(light_pos[0]), int(light_pos[1])), radius)
    
    # Cast rays from light source in all directions
    all_lines = []
    for i in range(RAY_COUNT):
        angle = 2 * math.pi * i / RAY_COUNT
        direction = [math.cos(angle), math.sin(angle)]
        lines = cast_ray(light_pos, direction, ray_intensity)
        all_lines.extend(lines)
    
    # Draw all ray segments
    for line in all_lines:
        start, end, color, width = line
        pygame.draw.line(screen, color, 
                         (int(start[0]), int(start[1])), 
                         (int(end[0]), int(end[1])), width)
    
    # Draw UI text
    reflection_text = font.render(f"Reflections: {'ON' if reflection_enabled else 'OFF'} (press R to toggle)", True, WHITE)
    shadows_text = font.render(f"Shadows: {'ON' if shadows_enabled else 'OFF'} (press S to toggle)", True, WHITE)
    intensity_text = font.render(f"Intensity Falloff: {'ON' if intensity_falloff_enabled else 'OFF'} (press I to toggle)", True, WHITE)
    rays_text = font.render(f"Ray Count: {RAY_COUNT} (press +/- to change)", True, WHITE)
    reset_text = font.render("Press SPACE to reset scene", True, WHITE)
    fps_text = font.render(f"FPS: {fps}", True, WHITE)
    instruction_text = font.render("Left-Click: Move light | Right-Click: Add/Remove sphere", True, WHITE)
    
    screen.blit(reflection_text, (10, 10))
    screen.blit(shadows_text, (10, 35))
    screen.blit(intensity_text, (10, 60))
    screen.blit(rays_text, (10, 85))
    screen.blit(reset_text, (10, 110))
    screen.blit(fps_text, (WIDTH - 100, 10))
    screen.blit(instruction_text, (WIDTH // 2 - 200, HEIGHT - 30))
    
    # Update display
    pygame.display.flip()
    
    # Calculate FPS
    fps_counter += 1
    current_time = pygame.time.get_ticks()
    if current_time - fps_time > 1000:  # Update FPS every second
        fps = fps_counter
        fps_counter = 0
        fps_time = current_time
    
    # Cap the frame rate
    clock.tick(60)

# Quit pygame
pygame.quit()
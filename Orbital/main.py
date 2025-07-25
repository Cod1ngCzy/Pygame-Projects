import pygame, math, sys

#Test
class CelestialBody:
    def __init__(self, mass=1.0, position=(0,0), velocity=(0,0), radius=20, color=(255,255,255), name="", fixed=False):
        self.mass = mass
        self.radius = radius
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(velocity)
        self.acceleration = pygame.Vector2(0,0)
        self.color = color
        self.name = name
        self.trail = []  # Store position history for trails
        self.max_trail_length = 500
        self.fixed = fixed  # Whether the body is fixed in place (e.g., the Sun)
    
    def update_physics(self, delta_time, other_bodies):
        # Calculate gravitational force
        fx_total = 0
        fy_total = 0

        for other in other_bodies:
            if other is not self:
                # Skip fixed bodies (e.g., the Sun)
                if self.fixed:
                    return

                # Distance between bodies
                dx = other.position.x - self.position.x
                dy = other.position.y - self.position.y
                distance = math.sqrt(dx**2 + dy**2)

                if distance < 10:  # Prevent division by zero
                    distance = 10
                
                # Gravitational force magnitude (scaled for visualization)
                G = 500  # Increased gravitational constant
                force = G * self.mass * other.mass / (distance ** 2)

                fx_total += force * (dx / distance)
                fy_total += force * (dy / distance)
        
        # Update Velocity using F = ma
        ax = fx_total / self.mass
        ay = fy_total / self.mass

        self.velocity.x += ax * delta_time
        self.velocity.y += ay * delta_time

        self.position.x += self.velocity.x * delta_time
        self.position.y += self.velocity.y * delta_time

        # Add current position to trail
        self.trail.append((int(self.position.x), int(self.position.y)))
        
        # Limit trail length
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

    def draw(self, screen):
        # Draw trail
        if len(self.trail) > 2:
            for i in range(1, len(self.trail)):
                alpha = i / len(self.trail)  # Fade effect
                trail_color = tuple(int(c * alpha) for c in self.color)
                if i > 0:
                    pygame.draw.line(screen, trail_color, self.trail[i-1], self.trail[i], 1)
    
        # Draw the celestial body
        pygame.draw.circle(screen, self.color, (int(self.position.x), int(self.position.y)), self.radius)
        
        # Draw name label
        if self.name:
            font = pygame.font.Font(None, 24)
            text = font.render(self.name, True, (255, 255, 255))
            screen.blit(text, (int(self.position.x) + self.radius + 5, int(self.position.y) - 10))

class SolarSystem:
    def __init__(self, center_x, center_y):
        self.center_x = center_x
        self.center_y = center_y
        self.bodies = []
        self.create_solar_system()
    
    def create_solar_system(self):
        # Sun (at center)
        sun = CelestialBody(
            mass=10000,  # Much larger mass for central body
            position=(self.center_x, self.center_y),
            velocity=(0, 0),
            radius=25,
            color=(255, 255, 0),  # Yellow
            name="Sun",
            fixed=True  # Sun is fixed in place
        )
        self.bodies.append(sun)
        
        # Calculate proper orbital velocities using v = sqrt(GM/r)
        G = 500  # Our scaled gravitational constant
        
        # Earth
        earth_distance = 150
        earth_orbital_velocity = math.sqrt(G * sun.mass / earth_distance)
        earth = CelestialBody(
            mass=10,
            position=(self.center_x + earth_distance, self.center_y),
            velocity=(0, earth_orbital_velocity),  # Proper orbital velocity
            radius=8,
            color=(100, 149, 237),  # Blue
            name="Earth"
        )
        self.bodies.append(earth)

        # Satellite orbiting Earth only
        satellite_distance = 25  # Distance from Earth's center
        satellite_orbital_velocity = math.sqrt(G * (earth.mass * 100) / satellite_distance)
        satellite_position = earth.position + pygame.Vector2(satellite_distance, 0)
        satellite_velocity_vector = pygame.Vector2(0, satellite_orbital_velocity)
        satellite_velocity = earth.velocity + satellite_velocity_vector
        satellite = CelestialBody(
            mass=1,
            position=satellite_position,
            velocity=satellite_velocity,
            radius=6,
            color=(200, 200, 255),  # Light blue
            name="Satellite"
        )
        self.bodies.append(satellite)

        # Mars
        mars_distance = 220
        mars_orbital_velocity = math.sqrt(G * sun.mass / mars_distance)
        mars = CelestialBody(
            mass=8,
            position=(self.center_x + mars_distance, self.center_y),
            velocity=(0, mars_orbital_velocity),
            radius=6,
            color=(255, 99, 71),  # Red
            name="Mars"
        )
        self.bodies.append(mars)
        
        # Venus
        venus_distance = 100
        venus_orbital_velocity = math.sqrt(G * sun.mass / venus_distance)
        venus = CelestialBody(
            mass=9,
            position=(self.center_x + venus_distance, self.center_y),
            velocity=(0, venus_orbital_velocity),
            radius=7,
            color=(255, 165, 0),  # Orange
            name="Venus"
        )
        self.bodies.append(venus)

        # Jupiter
        jupiter_distance = 300
        jupiter_orbital_velocity = math.sqrt(G * sun.mass / jupiter_distance)
        jupiter = CelestialBody(
            mass=20,
            position=(self.center_x + jupiter_distance, self.center_y),
            velocity=(0, jupiter_orbital_velocity),
            radius=12,
            color=(255, 215, 0),  # Gold
            name="Jupiter"
        )
        self.bodies.append(jupiter)
        
        # Small asteroid with elliptical orbit
        asteroid_distance = 180
        asteroid_orbital_velocity = math.sqrt(G * sun.mass / asteroid_distance) * 0.8  # Slightly slower for ellipse
        asteroid = CelestialBody(
            mass=1,
            position=(self.center_x + asteroid_distance, self.center_y + 30),
            velocity=(20, asteroid_orbital_velocity),
            radius=3,
            color=(169, 169, 169),  # Gray
            name="Asteroid"
        )
        self.bodies.append(asteroid)
    
    def update(self, delta_time):
        for body in self.bodies:
            body.update_physics(delta_time, self.bodies)
        
    def draw(self, screen):
        for body in self.bodies:
            body.draw(screen)
    
    def reset(self):
        self.bodies.clear()
        self.create_solar_system()
    
    def clear_trails(self):
        for body in self.bodies:
            body.trail.clear()

class Game:
    def __init__(self):
        pygame.init()
        self.GAME_WIDTH = 800
        self.GAME_HEIGHT = 600
        self.GAME_SCREEN = pygame.display.set_mode((self.GAME_WIDTH, self.GAME_HEIGHT))
        pygame.display.set_caption("Orbital Motion Simulation")
        
        self.GAME_CLOCK = pygame.time.Clock()
        self.RUNNING = True
        self.PAUSED = False

        # Create Solar System
        self.solar_system = SolarSystem(self.GAME_WIDTH // 2, self.GAME_HEIGHT // 2)
        
        # UI
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

    def handle_game_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.RUNNING = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.RUNNING = False
                elif event.key == pygame.K_SPACE:
                    self.PAUSED = not self.PAUSED
                elif event.key == pygame.K_r:
                    self.solar_system.reset()
                elif event.key == pygame.K_c:
                    self.solar_system.clear_trails()
    
    def draw_ui(self):
        # Instructions
        instructions = [
            "SPACE: Pause/Resume",
            "C: Clear trails",
            "R: Reset simulation",
            "ESC: Exit",
            f"Status: {'PAUSED' if self.PAUSED else 'RUNNING'}"
        ]
        
        y_offset = 10
        for instruction in instructions:
            text = self.small_font.render(instruction, True, (255, 255, 255))
            self.GAME_SCREEN.blit(text, (10, y_offset))
            y_offset += 25
        
        # Title
        title = self.font.render("Solar System Simulation", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.GAME_WIDTH // 2, 30))
        self.GAME_SCREEN.blit(title, title_rect)
    
    def run(self):
        while self.RUNNING:
            delta_time = self.GAME_CLOCK.tick(60) / 1000
            
            self.handle_game_events()
            
            # Update physics
            if not self.PAUSED:
                self.solar_system.update(delta_time)
            
            # Draw everything
            self.GAME_SCREEN.fill((0, 0, 0))
            self.solar_system.draw(self.GAME_SCREEN)
            self.draw_ui()

            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
    sys.exit()
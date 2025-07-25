import pygame, math, sys

class CelestialBody:
    def __init__(self, mass=1.0, position=(0,0), velocity=(0,0), radius=20, color=(255,255,255), name="", fixed=False):
        self.mass = mass
        self.radius = radius
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(velocity)
        self.acceleration = pygame.Vector2(0,0)
        self.color = color
        self.name = name
        self.trail = []
        self.max_trail_length = 800
        self.fixed = fixed
    
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
                G = 100  # Increased gravitational constant
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
        # Draw trail with fade
        if len(self.trail) > 2:
            for i in range(1, len(self.trail)):
                alpha = (i / len(self.trail)) * 0.5  # More subtle trails
                trail_color = tuple(int(c * alpha) for c in self.color)
                if i > 0:
                    pygame.draw.line(screen, trail_color, self.trail[i-1], self.trail[i], 1)
    
        # Draw body
        pygame.draw.circle(screen, self.color, (int(self.position.x), int(self.position.y)), self.radius)
        
        # Draw name
        if self.name:
            font = pygame.font.Font(None, 18)
            text = font.render(self.name, True, (255, 255, 255))
            screen.blit(text, (int(self.position.x) + self.radius + 3, int(self.position.y) - 8))

class SolarSystem:
    def __init__(self, center_x, center_y):
        self.center_x = center_x
        self.center_y = center_y
        self.bodies = []
        self.G = 100  # Gravitational constant
        self.create_solar_system()
    
    def calculate_circular_velocity(self, central_mass, distance):
        """Calculate the velocity needed for a circular orbit"""
        return math.sqrt(self.G * central_mass / distance)
    
    def create_solar_system(self):
        # Sun at center - much more massive for stable system
        sun = CelestialBody(
            mass=100000,  # Dominant central mass
            position=(self.center_x, self.center_y),
            velocity=(0, 0),
            radius=20,
            color=(255, 255, 0),
            name="Sun",
            fixed=True
        )
        self.bodies.append(sun)
        
        # Mercury
        mercury_dist = 80
        mercury_vel = self.calculate_circular_velocity(sun.mass, mercury_dist)
        mercury = CelestialBody(
            mass=30,
            position=(self.center_x + mercury_dist, self.center_y),
            velocity=(0, mercury_vel),
            radius=3,
            color=(169, 169, 169),
            name="Mercury"
        )
        self.bodies.append(mercury)
        
        # Venus
        venus_dist = 110
        venus_vel = self.calculate_circular_velocity(sun.mass, venus_dist)
        venus = CelestialBody(
            mass=80,
            position=(self.center_x + venus_dist, self.center_y),
            velocity=(0, venus_vel),
            radius=5,
            color=(255, 165, 0),
            name="Venus"
        )
        self.bodies.append(venus)
        
        # Earth - positioned for stable orbit
        earth_dist = 150
        earth_vel = self.calculate_circular_velocity(sun.mass, earth_dist)
        earth = CelestialBody(
            mass=100,
            position=(self.center_x + earth_dist, self.center_y),
            velocity=(0, earth_vel),
            radius=6,
            color=(100, 149, 237),
            name="Earth"
        )
        self.bodies.append(earth)
        
        # Mars
        mars_dist = 200
        mars_vel = self.calculate_circular_velocity(sun.mass, mars_dist)
        mars = CelestialBody(
            mass=60,
            position=(self.center_x + mars_dist, self.center_y),
            velocity=(0, mars_vel),
            radius=4,
            color=(255, 99, 71),
            name="Mars"
        )
        self.bodies.append(mars)
        
        # Jupiter - far out for stability
        jupiter_dist = 280
        jupiter_vel = self.calculate_circular_velocity(sun.mass, jupiter_dist)
        jupiter = CelestialBody(
            mass=300,
            position=(self.center_x + jupiter_dist, self.center_y),
            velocity=(0, jupiter_vel),
            radius=10,
            color=(255, 215, 0),
            name="Jupiter"
        )
        self.bodies.append(jupiter)
        
        # Asteroid with slightly elliptical orbit
        asteroid_dist = 175
        asteroid_vel = self.calculate_circular_velocity(sun.mass, asteroid_dist) * 0.9  # Slower for ellipse
        asteroid = CelestialBody(
            mass=0.5,
            position=(self.center_x + asteroid_dist, self.center_y - 20),
            velocity=(10, asteroid_vel),  # Some tangential component
            radius=2,
            color=(139, 69, 19),
            name="Asteroid"
        )
        self.bodies.append(asteroid)
    
    def update(self, delta_time):
        # Use smaller timestep for numerical stability
        max_dt = 0.008  # Maximum timestep
        if delta_time > max_dt:
            steps = int(delta_time / max_dt) + 1
            small_dt = delta_time / steps
            for _ in range(steps):
                for body in self.bodies:
                    body.update_physics(small_dt, self.bodies)
        else:
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
        pygame.display.set_caption("Stable Solar System with Earth-Moon System")
        
        self.GAME_CLOCK = pygame.time.Clock()
        self.RUNNING = True
        self.PAUSED = False
        self.time_scale = 1.0

        self.solar_system = SolarSystem(self.GAME_WIDTH // 2, self.GAME_HEIGHT // 2)
        
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 18)

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
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    self.time_scale = min(8.0, self.time_scale + 0.25)
                elif event.key == pygame.K_MINUS:
                    self.time_scale = max(0.10, self.time_scale - 0.25)
    
    def draw_ui(self):
        instructions = [
            "SPACE: Pause/Resume",
            "C: Clear trails", 
            "R: Reset",
            "+/-: Speed control",
            "ESC: Exit",
            "",
            f"Status: {'PAUSED' if self.PAUSED else 'RUNNING'}",
            f"Speed: {self.time_scale:.2f}x"
        ]
        
        y = 10
        for instruction in instructions:
            if instruction:  # Skip empty strings
                text = self.small_font.render(instruction, True, (255, 255, 255))
                self.GAME_SCREEN.blit(text, (10, y))
            y += 20
        
        title = self.font.render("Stable Solar System", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.GAME_WIDTH // 2, 25))
        self.GAME_SCREEN.blit(title, title_rect)
    
    def run(self):
        while self.RUNNING:
            # Fixed timestep with scaling
            delta_time = (1.0 / 60.0) * self.time_scale
            self.GAME_CLOCK.tick(60)
            
            self.handle_game_events()
            
            if not self.PAUSED:
                self.solar_system.update(delta_time)
            
            self.GAME_SCREEN.fill((5, 5, 15))  # Dark space background
            self.solar_system.draw(self.GAME_SCREEN)
            self.draw_ui()

            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
    sys.exit()
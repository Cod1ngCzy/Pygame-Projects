import pygame, sys, math
from random import randint

pygame.init()

# Screen Dimensions
D_WIDTH, D_HEIGHT = 1280, 700
display = pygame.display.set_mode((D_WIDTH, D_HEIGHT))
pygame.display.set_caption('Collision Simulation')

class Ball:
    def __init__(self, x, y, width, height, radius=20):
        """Initialize ball properties including position, velocity, physics, and appearance."""
        self.pos = pygame.Vector2(x, y)  # Stores the precise position of the ball
        self.surface = pygame.Rect(x, y, width, height)  # Rect for collision detection (not used in physics)
        self.radius = radius  # The radius of the ball (affects collisions)
        self.velocity = pygame.Vector2(2000, 0)  # Initial velocity (movement direction & speed)
        self.bounce_retention = 0.6  # Energy retention when bouncing off walls
        self.gravity = 9.8  # Simulated gravity force
        self.color = 'red'  # Ball color
        self.mass = 1  # Mass of the ball (used in velocity exchange during collisions)

    def move(self, dt):
        """Update the ball's position based on its velocity and delta time."""
        self.pos += self.velocity * dt  # Apply movement

        # Sync the pygame Rect with the ball's position
        self.surface.center = (int(self.pos.x), int(self.pos.y))

    def drag_ball(self):
    
        """Allows the user to drag the ball using the mouse."""
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos()) # Get Mouse Position

        if self.surface.collidepoint(mouse_pos):  # If mouse hovers over ball
            if pygame.mouse.get_pressed()[0]:  # If left mouse button is clicked
                self.pos.x, self.pos.y = mouse_pos  # Move ball to cursor position
                self.velocity = pygame.Vector2(0, 0)  # Stop movement
                self.gravity = 0  # Disable gravity while dragging
            else:
                self.gravity = 9.8  # Restore gravity when released

    def ball_physics(self):
        """Apply gravity and handle bouncing when hitting the ground."""
        if self.pos.y <= D_HEIGHT - self.radius:
            self.velocity.y += self.gravity * dt * 500  # Simulate acceleration due to gravity

        # If the ball hits the ground, apply bounce physics
        if self.pos.y + self.radius >= D_HEIGHT and self.velocity.y > 0:  
            """Collision Detection"""
            self.pos.y = D_HEIGHT - self.radius  # Prevent sinking into the ground
            """Collision Resolution"""
            self.velocity.y = -self.velocity.y * self.bounce_retention  # Reverse velocity with energy loss
            self.velocity.x *= 0.86 # Apply ground friction (reduces horizontal speed gradually)
            
            # Prevent tiny bounces by stopping very small velocities
            if abs(self.velocity.y) < 1:  
                self.velocity.y = 0  
                self.pos.y = D_HEIGHT - self.radius
        
        print(self.velocity)
        print(abs(self.velocity.y))

            
    def collisions(self):
        """Handle collisions with the screen borders (left, right)."""
        if self.pos.x + self.radius >= D_WIDTH:  # Right wall collision
            self.pos.x = D_WIDTH - self.radius  # Prevent going outside
            self.velocity.x = -self.velocity.x * 0.7  # Bounce with energy loss

        elif self.pos.x - self.radius <= 0:  # Left wall collision
            self.pos.x = self.radius  # Prevent going outside
            self.velocity.x = -self.velocity.x * 0.7  # Bounce with energy loss

    def ball_collisions(self, other_ball):
        """Detect and resolve ball collisions (velocity swap & overlap resolution)."""
        distance = self.pos.distance_to(other_ball.pos)  # Compute distance between centers
        radii = self.radius + other_ball.radius  # Sum of both radii (collision threshold)

        if distance < radii:  # If collision occurs (balls are overlapping)
            # Prevent division by zero in extreme cases (identical positions)
            if distance == 0:
                return

            # Calculate overlap distance
            overlap = radii - distance

            # Get normalized direction vector of collision (from other_ball to self)
            direction = (self.pos - other_ball.pos).normalize()

            # Push the balls apart to resolve overlap
            self.pos += direction * (overlap / 2)
            other_ball.pos -= direction * (overlap / 2)

            # Compute relative velocity along the collision normal
            relative_velocity = self.velocity - other_ball.velocity
            velocity_along_normal = relative_velocity.dot(direction)

            # If balls are separating, no need to resolve further
            if velocity_along_normal > 0:
                return

            # Calculate impulse scalar (assume equal masses)
            restitution = min(self.bounce_retention, other_ball.bounce_retention)  # Energy retention factor
            impulse = -(1 + restitution) * velocity_along_normal
            impulse /= (1 / self.mass + 1 / other_ball.mass)  # Adjust for mass

            # Apply impulse to both balls (affecting their velocity)
            self.velocity += (impulse / self.mass) * direction
            other_ball.velocity -= (impulse / other_ball.mass) * direction

    def update(self, dt, balls):
        """Update all physics & drawing operations."""
        self.move(dt)
        self.drag_ball()
        self.ball_physics()
        self.collisions()

        # Check for collisions with other balls
        for ball in balls:
            if ball != self:  # Ensure a ball doesn't collide with itself
                self.ball_collisions(ball)

        # Draw the ball onto the screen
        pygame.draw.circle(display, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)


# Game Loop Variables
running = True
clock = pygame.time.Clock()

# Create multiple ball instances
balls = [Ball(randint(0, D_WIDTH), randint(0, D_HEIGHT), 50, 50) for _ in range(50)]

while running:
    dt = clock.tick(60) / 1000  # Limit FPS to 60 and calculate delta time

    # Event Handling (Quit Event)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear screen (fill with black)
    display.fill('black')

    # Update all balls
    for ball in balls:
        ball.update(dt, balls)

    # Refresh screen
    pygame.display.flip()

pygame.quit()

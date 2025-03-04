from settings import *  # Import all settings, including TILE_SIZE and GRID_MAP
import pygame  # Import Pygame for handling graphics and game logic
import random  # Import random for ghost movement logic

class Entities(pygame.sprite.Sprite):  # Base class for all game entities
    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))  # Create a square surface for the entity
        self.image.fill('yellow')  # Set the default entity color to yellow
        self.rect = self.image.get_frect()  # Get the rectangle for positioning and collisions
        self.pos = pygame.Vector2()  # Position of the entity in the grid
        self.direction = pygame.Vector2(0, 0)  # Direction of movement
        self.speed = 5  # Movement speed of the entity
        self.move_timer = 0  # Timer to regulate movement speed
        self.rows = len(GRID_MAP)  # Number of rows in the grid
        self.cols = len(GRID_MAP[0]) if self.rows > 0 else 0  # Number of columns in the grid

    def wall_collisions(self, walls):  # Handle collisions with walls
        for wall in walls:
            if self.rect.colliderect(wall):  # Check if entity collides with a wall
                if self.direction.x > 0:  # Moving right
                    self.rect.right = wall.left  # Stop movement at the wall
                    self.pos.x = self.rect.x / TILE_SIZE  # Update grid position
                elif self.direction.x < 0:  # Moving left
                    self.rect.left = wall.right  # Stop movement at the wall
                    self.pos.x = self.rect.x / TILE_SIZE  # Update grid position
                if self.direction.y > 0:  # Moving down
                    self.rect.bottom = wall.top  # Stop movement at the wall
                    self.pos.y = self.rect.y / TILE_SIZE  # Update grid position
                elif self.direction.y < 0:  # Moving up
                    self.rect.top = wall.bottom  # Stop movement at the wall
                    self.pos.y = self.rect.y / TILE_SIZE  # Update grid position

    def collisions(self, other_object):  # Handle collisions with other objects
        if isinstance(other_object, (list, tuple, set)):  # If checking multiple objects
            for obj in other_object:
                if self.rect.colliderect(obj.rect):  # Check if colliding
                    print(self.rect, obj.rect)  # Print collision details
        else:  # If checking a single object
            if self.rect.colliderect(other_object.rect):  # Check if colliding
                print(self.rect, other_object.rect)  # Print collision details

    def update(self, dt, walls, pacman, ghost, pellets, game_data):  # Update entity state each frame
        self.move_timer += dt  # Increment move timer
        self.wall_collisions(walls)  # Check for wall collisions

class Pacman(Entities):  # Class for Pacman player
    def __init__(self, groups):
        super().__init__(groups)
        self.pos = pygame.Vector2(1, 1)  # Set initial position
        self.rect.topleft = self.pos * TILE_SIZE  # Position Pacman on the grid

    def input_movement(self):  # Handle player input for movement
        keys = pygame.key.get_pressed()  # Get keyboard input
        if keys[pygame.K_d]:  # Move right
            self.direction = pygame.Vector2(1, 0)
        elif keys[pygame.K_a]:  # Move left
            self.direction = pygame.Vector2(-1, 0)
        elif keys[pygame.K_w]:  # Move up
            self.direction = pygame.Vector2(0, -1)
        elif keys[pygame.K_s]:  # Move down
            self.direction = pygame.Vector2(0, 1)
    
    def eat_pellets(self, pellets):
        for row_index, pellet in enumerate(pellets):
            if self.rect.colliderect(pellet):
                pellets.pop(row_index)
                return True

    def update(self, dt, walls, pacman, ghost, pellets, game_data):  # Update Pacman each frame
        self.input_movement()  # Process movement input
    
        if self.move_timer >= 1 / self.speed:  # Check if it's time to move
            self.move_timer = 0  # Reset move timer
            self.pos += self.direction  # Move based on direction
            self.rect.topleft = self.pos * TILE_SIZE  # Update position on the grid 
        
        if self.eat_pellets(pellets):
            game_data['points'] += 10
            
        self.collisions(ghost)  # Check for collisions with ghosts
        super().update(dt, walls, pacman, ghost, pellets, game_data)  # Call parent update method

class Ghosts(Entities):  # Class for Ghost enemies
    def __init__(self, groups, color, pos_x, pos_y):
        super().__init__(groups)
        self.pos = pygame.Vector2(pos_x, pos_y)  # Set initial position
        self.rect.topleft = self.pos * TILE_SIZE  # Position ghost on the grid
        self.image.fill(color)  # Set ghost color
        self.path = []  # Store possible movement paths
        self.last_move = []  # Track previous movement
        self.direction = pygame.Vector2(0, 0)  # Initial movement direction
        self.move_timer = 0  # Timer for controlling movement speed

    def walkable_path(self):  # Find valid movement paths for the ghost
        self.path = []  # Reset path list
        row, col = int(self.pos.y), int(self.pos.x)  # Convert position to grid indexes
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # Up, Right, Down, Left

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc  # Calculate new position

            if (0 <= new_row < len(GRID_MAP) and  # Ensure within grid bounds
                0 <= new_col < len(GRID_MAP[0]) and  
                GRID_MAP[new_row][new_col] == '0'):  # Check if walkable
                self.path.append((dc, dr))  # Add walkable direction

        return self.path  # Return list of possible moves

    def update(self, dt, walls, pacman, ghost, pellets, game_data):  # Update ghost each frame
        self.walkable_path()  # Get possible movement paths

        if self.move_timer >= 1 / self.speed:  # Check if it's time to move
            if self.path:  # If there are valid paths
                next_move = random.choice(self.path)  # Choose a random move
                next_pos = (self.pos.x + next_move[0], self.pos.y + next_move[1])  # Calculate next position
                current_pos = self.pos.x, self.pos.y  # Store current position

                if len(self.last_move) > 1:
                    self.last_move.pop(0)  # Remove oldest move to track movement history
                self.last_move.append(current_pos)  # Store new position

                if next_pos == self.last_move[0]:  # Prevent backtracking
                    next_move = random.choice(self.path)

                self.direction = pygame.Vector2(next_move[0], next_move[1])  # Update direction

            self.move_timer = 0  # Reset move timer
            self.pos += self.direction  # Move based on updated direction
            self.rect.topleft = self.pos * TILE_SIZE  # Update position

        self.collisions(pacman)  # Check for collisions with Pacman
        super().update(dt, walls, pacman, ghost, pellets, game_data)  # Call parent update method

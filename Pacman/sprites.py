from settings import *

class Character(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.image =  pygame.Surface((TILE_SIZE,TILE_SIZE))
        self.image.fill('yellow')
        self.rect = self.image.get_frect()
        self.pos = pygame.Vector2()
        self.direction = pygame.Vector2(0,0)
        self.speed = 5
        self.move_timer = 0
        self.rows = len(GRID_MAP)
        self.cols = len(GRID_MAP[0]) if self.rows > 0 else 0
    
    def wall_collisions(self, walls):
        for wall in walls:
            if self.rect.colliderect(wall):
                if self.direction.x > 0:
                    self.rect.right = wall.left
                    self.pos.x = self.rect.x / TILE_SIZE
                elif self.direction.x < 0:
                    self.rect.left = wall.right
                    self.pos.x = self.rect.x / TILE_SIZE
                if self.direction.y > 0:  # Moving down
                    self.rect.bottom = wall.top
                    self.pos.y = self.rect.y / TILE_SIZE
                elif self.direction.y < 0:  # Moving up
                    self.rect.top = wall.bottom
                    self.pos.y = self.rect.y / TILE_SIZE
    
    def update(self, dt, walls, paths):
        self.move_timer += dt

        self.wall_collisions(walls)

class Pacman(Character):
    def __init__(self, groups):
        super().__init__(groups)
        self.pos = pygame.Vector2(1,1)

    def input_movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.direction = pygame.Vector2(1,0)
        elif keys[pygame.K_a]:
            self.direction = pygame.Vector2(-1,0)
        elif keys[pygame.K_w]:
            self.direction = pygame.Vector2(0,-1)
        elif keys[pygame.K_s]:
            self.direction = pygame.Vector2(0,1)
            
    def update(self, dt, walls, paths):
        self.input_movement()
        
        if self.move_timer >= 1 / self.speed:
            self.move_timer = 0
            self.pos += self.direction  # Move based on direction
            self.rect.topleft = self.pos * TILE_SIZE  # Update position

        super().update(dt, walls, paths)  # Call parent update method
        #print(self.pos, self.direction, self.rect)

class Ghosts(Character):
    def __init__(self, groups):
        super().__init__(groups)
        self.pos = pygame.Vector2(6, 8)  # Initial position
        self.image.fill('orange')
        self.speed = 5  # Move one tile per step
        self.path = []
        self.last_move = []
        self.direction = pygame.Vector2(0, 0)  # Initial movement direction
        self.move_timer = 0  # Timer to control movement speed
    
    def walkable_path(self):
        """Updates and returns the list of walkable tiles around the ghost."""
        self.path = []  # Reset path list
        row, col = int(self.pos.y), int(self.pos.x)  # Convert position to grid indexes
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # Up, Right, Down, Left


        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc

            if (0 <= new_row < len(GRID_MAP) and 
                0 <= new_col < len(GRID_MAP[0]) and 
                GRID_MAP[new_row][new_col] == '0'):  
                self.path.append((dc,dr)) # Flipped

        return self.path  # Return updated walkable path
    
        
    def update(self, dt, walls, paths):
        self.walkable_path()

        if self.move_timer >= 1 / self.speed:
            if self.path:  # If there are valid paths
                next_move = self.path.pop(0)  # Get the first available move
                next_pos = (self.pos.x + next_move[0],self.pos.y + next_move[1])
                current_pos = self.pos.x, self.pos.y
                
                if len(self.last_move) > 1:
                    self.last_move.pop(0)
                self.last_move.append(current_pos)

                #print(f'Movement List{self.last_move}\n Current Pos: {current_pos} Next Pos: {next_pos}')
                if next_pos == self.last_move[0]:     
                    next_move = random.choice(self.path)

                self.direction = pygame.Vector2(next_move[0], next_move[1])  # Convert to vector
                #print(f'Current Pos:{self.pos} \n Last Pos: {self.last_move} \n')


            self.move_timer = 0
            self.pos += self.direction # Move based on updated direction
            self.rect.topleft = self.pos * TILE_SIZE  # Update sprite position

        super().update(dt, walls, paths)
    
        


      


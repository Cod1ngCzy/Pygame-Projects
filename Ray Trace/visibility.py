import pygame, sys, math
from pygame import gfxdraw
import pygame.gfxdraw

# Initialize
pygame.init()
WIDTH, HEIGHT = 800,800
display = pygame.display.set_mode((WIDTH,HEIGHT))

# Variables
running = True
clock = pygame.time.Clock()

# Classes
class Observer():
    def __init__(self,x,y,width,height):
        self.rect = pygame.Rect(x,y,width,height)
        self.radius = 15
        self.pos = pygame.Vector2(x,y)
        self.direction = pygame.Vector2(0,0)
        self.color = (255,255,255) # White
    
    def line_of_sight(self, other_line):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1])
        angle_to_mouse = math.atan2(mouse_pos.y - self.rect.y, mouse_pos.x - self.rect.x)
        length = 500
        line_objects = []

        # Create Rays
        for angle in range(-15, 16, 1):
            radian = angle_to_mouse + math.radians(angle)
            start_point = pygame.Vector2(self.rect.x, self.rect.y)
            end_point = pygame.Vector2(
                self.pos.x + length * (math.cos(radian)),  # X value
                self.pos.y + length * (math.sin(radian))  # Y value
            )
            line_objects.append(Line(start_point.x ,start_point.y, end_point.x, end_point.y))

        # Draw Rays
        for i, line in enumerate(line_objects):
            next_index = (i + 1) % len(line_objects)
            next_line = line_objects[next_index]

            intersection_point = line.intersect(other_line)
            next_intersection_point = next_line.intersect(other_line)

            if next_intersection_point and intersection_point:
                pygame.draw.polygon(display, (255, 255, 0, 100),[line.start_point, intersection_point, next_intersection_point, next_line.start_point])
            elif intersection_point:
                pygame.draw.polygon(display, (255, 255, 0, 100), [line.start_point, intersection_point, next_line.end_point, next_line.start_point])
            elif next_intersection_point:
                pygame.draw.polygon(display, (255, 255, 0, 100), [line.start_point, line.end_point, next_intersection_point, next_line.start_point])
            else:
                pygame.draw.polygon(display, (255, 255, 0, 100), [line.start_point, line.end_point, next_line.end_point, next_line.start_point])
                
            
            

    

    def move(self,dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])

        # Base Movement
        self.pos += self.direction * dt * 300
        self.rect.center = self.pos
    
    def update(self,dt,other_line):
        self.move(dt)
        self.line_of_sight(other_line)
        pygame.gfxdraw.circle(display, self.rect.x,self.rect.y,self.radius,self.color)

class Line:
    def __init__(self, p_ax, p_ay, p_bx, p_by):
        # Initialize the start and end points of the line using pygame.Vector2 for easy math operations
        self.start_point = pygame.Vector2(p_ax, p_ay)
        self.end_point = pygame.Vector2(p_bx, p_by)\
    
    def draw(self):
        pygame.draw.line(display,(255,255,255), self.start_point, self.end_point)

    def intersect(self, other_line):
        # Unpack the coordinates of the start and end points of both lines
        x1, y1 = self.start_point
        x2, y2 = self.end_point
        x3, y3 = other_line.start_point
        x4, y4 = other_line.end_point

        # Calculate the denominator for the intersection formula
        denominator = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)

        # If the denominator is zero, the lines are parallel and do not intersect
        if denominator == 0:
            return None

        # Calculate the parameters ua and ub to determine if the lines intersect
        ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denominator
        ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denominator

        # If both parameters are between 0 and 1, the lines intersect
        if 0 <= ua <= 1 and 0 <= ub <= 1:
            # Calculate the intersection point
            x = x1 + ua * (x2 - x1)
            y = y1 + ua * (y2 - y1)
            return pygame.Vector2(x, y)
        
player = Observer(20,20,15,15)
test_line = Line(200,200,400,400)
while running:
    dt = clock.tick() / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    display.fill('black')
    player.update(dt,test_line)
    test_line.draw()

    pygame.display.update()
pygame.quit()
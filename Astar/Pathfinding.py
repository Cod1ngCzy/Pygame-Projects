import pygame, sys, math
from os.path import join
from random import randint

# Initialize 
pygame.init()
D_WIDTH, D_HEIGHT = 1280, 720
display = pygame.display.set_mode((D_WIDTH, D_HEIGHT))
pygame.display.set_caption('Graph')

# Class
class Nodes():
    def __init__(self,x,y,width,height):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.color = 'white'
        self.rect = pygame.Rect(self.x,self.y,self.width,self.height)

        # Path Finding Attribute
        self.parent = None
        self.g = float('inf')  # Cost from start to this node
        self.h = 0  # Heuristic (estimated cost from this node to the end)
        self.f = float('inf')  # Total cost (g + h)
    
    def render(self):
        pygame.draw.rect(display,self.color,self.rect,0)
    
    def calculate_distance(self, target):
        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery
        return math.sqrt(dx ** 2 + dy ** 2)

class Player(pygame.sprite.Sprite):
    def __init__(self,groups):
        super().__init__(groups)
        self.load_image = pygame.image.load('0.png').convert_alpha()
        self.image = pygame.transform.scale(self.load_image, (32,32))
        self.rect = self.image.get_frect(center = start_point)
    
    def update(self, *args, **kwargs):
        return super().update(*args, **kwargs)

# Functions
def render_nodes(rows, cols):
    """
    Creates a grid of nodes based on the given number of rows and columns.

    Args:
        rows (int): Number of rows in the grid.
        cols (int): Number of columns in the grid.

    Returns:
        list: A list of Nodes positioned in a uniform grid.
    """
    nodes = []  # List to store the created nodes
    
    # Calculate the spacing between nodes to distribute them evenly (based on the display)
    spacing_x = D_WIDTH // (cols + 1)  # Horizontal spacing
    spacing_y = D_HEIGHT // (rows + 1)  # Vertical spacing

    # Loop through the grid positions and create nodes
    for row in range(1, rows + 1):  # Start from 1 to avoid placing at the edges
        for col in range(1, cols + 1):
            x = col * spacing_x  # X-coordinate based on column
            y = row * spacing_y  # Y-coordinate based on row
            
            # Create a node at the computed position and add it to the list
            nodes.append(Nodes(x, y, 10, 10))  

    return nodes  # Return the list of nodes

def build_graph(nodes):
    """
    Builds a graph where each node is connected to its three closest neighbors.

    Args:
        nodes (list): A list of Nodes.

    Returns:
        dict: A dictionary where each node is mapped to a list of its closest neighbors.
    """
    graph = {}  # Dictionary to store node connections

    # Iterate through each node in the list
    for node in nodes:
        list_nodes = []  # List to store neighboring nodes with their distances

        # Compare the current node with every other node
        for other_node in nodes:
            if node != other_node:  # Avoid calculating distance to itself
                distance = node.calculate_distance(other_node)  # Compute Euclidean distance
                list_nodes.append((other_node, distance))  # Store node with its distance
        
        # Sort neighbors by distance (ascending order)
        list_nodes.sort(key=lambda x: x[1])

        # Select the 3 closest neighbors
        closest_nodes = list_nodes[:5]

        # Store the closest neighbors in the graph dictionary
        graph[node] = closest_nodes

    return graph  # Return the complete graph

def a_star(start_node, end_node, graph):
    """
    Implements A* pathfinding algorithm.

    Args:
        start_node (Nodes): The starting node.
        end_node (Nodes): The goal node.
        graph (dict): A dictionary of nodes with their neighbors.

    Returns:
        list: The shortest path from start to end.
    """
    open_set = []  # Nodes to be evaluated
    closed_set = set()  # Nodes already evaluated

    start_node.g = 0
    start_node.h = start_node.calculate_distance(end_node)
    start_node.f = start_node.g + start_node.h
    open_set.append(start_node)

    while open_set:
        # Get node with lowest F value
        open_set.sort(key=lambda node: node.f)
        current_node = open_set.pop(0)
        closed_set.add(current_node)

        # If reached the goal, reconstruct the path
        if current_node == end_node:
            path = []
            while current_node:
                path.append(current_node)
                current_node = current_node.parent
            return path[::-1]  # Return reversed path

        for neighbor, _ in graph[current_node]:  # Loop through neighbors
            if neighbor in closed_set:
                continue  # Skip if already evaluated

            temp_g = current_node.g + current_node.calculate_distance(neighbor)

            if temp_g < neighbor.g:
                neighbor.parent = current_node
                neighbor.g = temp_g
                neighbor.h = neighbor.calculate_distance(end_node)
                neighbor.f = neighbor.g + neighbor.h

                if neighbor not in open_set:
                    open_set.append(neighbor)

    return None  # No path found

def regenerate_path():
    global nodes, start_point, end_point, path_locations, counter
    nodes = render_nodes(GRID_ROW, GRID_COL)
    graph = build_graph(nodes)
    
    # New start and end points
    start_point = nodes[randint(0, len(nodes)-1)].rect.center
    end_point = nodes[randint(0, len(nodes)-1)].rect.center
    
    # Find corresponding nodes
    start_node = None
    end_node = None

    for node in nodes:
        if node.rect.center == start_point:
            start_node = node
        if node.rect.center == end_point:
            end_node = node

    # Run A* to find the path
    paths = a_star(start_node, end_node, graph)

    # Reset path locations and counter
    path_locations = [node.rect.center for node in paths]
    counter = 0  # Reset counter to start from the new start point

    # Render the nodes with updated colors
    for node in nodes:
        if node.rect.center == start_point:
            node.color = 'blue'
        elif node.rect.center == end_point:
            node.color = 'red'
        elif node in paths:
            node.color = 'green'
        else:
            node.color = 'white'
        node.render()
        
# Variables
GRID_ROW, GRID_COL = 5, 7
nodes = render_nodes(GRID_ROW, GRID_COL)
graph = build_graph(nodes)
clock = pygame.time.Clock()
start_point = nodes[randint(0, len(nodes)-1)].rect.center
end_point = nodes[randint(0, len(nodes)-1)].rect.center
path_locations = []
counter = 0

# Game State
running = True

# Instantiate player
all_sprite = pygame.sprite.Group()
player = Player(all_sprite)

# Run A* to find the path
start_node = None
end_node = None

for node in nodes:
    if node.rect.center == start_point:
        start_node = node
    if node.rect.center == end_point:
        end_node = node

paths = a_star(start_node, end_node, graph)

for path in paths:
    path_locations.append(path.rect.center)


# Event
move_event = pygame.event.custom_type()
pygame.time.set_timer(move_event, 500)

# Game loop
while running:
    dt = clock.tick() // 1000

    # Event Handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == move_event:
            if counter < len(path_locations):
                player.rect.center = path_locations[counter]
                counter += 1
                print(f"Player moving to: {player.rect.center}") 
            else:
                regenerate_path()

    display.fill('black')

    # Render all nodes
    for node in nodes:
        if node.rect.center == start_point:
            node.color = 'blue'
        elif node.rect.center == end_point:
            node.color = 'red'
        elif node.rect.center in path_locations:
            node.color = 'green'
        else:
            node.color = 'white'
        node.render()

    # Update player and draw sprites
    all_sprite.update()
    all_sprite.draw(display)

    #for node, neighbors in graph.items():
        #for neighbor, distance in neighbors:
            #pygame.draw.line(display,'red',node.rect.center, neighbor.rect.center)

    pygame.display.flip()

pygame.quit()

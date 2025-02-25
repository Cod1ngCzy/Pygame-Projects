import pygame, sys, math
from random import randint
from queue import PriorityQueue

# Initialize Pygame and set up the display
pygame.init()
D_WIDTH, D_HEIGHT = 1280, 720  # Display dimensions
display = pygame.display.set_mode((D_WIDTH, D_HEIGHT))
pygame.display.set_caption('A* Pathfinding')  # Window title

# Classes
class Node():
    def __init__(self, x, y, width, height):
        # Initialize node properties
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.color = 'white'  # Default color for nodes
        self.rect = pygame.Rect(x, y, width, height)  # Rectangle for rendering and collision
        self.font = pygame.font.Font(None, 18)
        self.text = self.font.render(str(self.rect.center), True, 'blue')
        self.text_rect = self.text.get_frect(center=(self.rect.centerx, self.rect.centery - 20))

    def render(self):
        # Draw the node on the display
        display.blit(self.text, self.text_rect)
        pygame.draw.rect(display, self.color, self.rect)

# Function to calculate the Euclidean distance between two nodes
def calculate_distance(node, other_node):
    dx = other_node.rect.centerx - node.rect.centerx
    dy = other_node.rect.centery - node.rect.centery
    return math.sqrt(dx ** 2 + dy ** 2)

# Function to build connections between nodes based on proximity
def build_node_connections(nodes):
    graph = {}  # Dictionary to store node connections

    for node in nodes:
        node_objects = []  # List to store neighboring nodes and their distances
        for other_node in nodes:
            if node != other_node:  # Avoid connecting a node to itself
                distance = calculate_distance(node, other_node)
                node_objects.append((other_node, distance))

        # Sort neighbors by distance (closest first)
        node_objects.sort(key=lambda x: x[1])

        # Keep only the 3 closest neighbors
        closest_nodes = node_objects[:3]

        # Add the node and its closest neighbors to the graph
        graph[node] = closest_nodes

    return graph

# Draw connections between nodes
def show_node_connections(graph):
    for node, neighbors in graph.items():
        for neighbor, distance in neighbors:
            font_surface = font.render(str(int(distance)), True, 'red')
            display.blit(font_surface, ((node.rect.centerx + neighbor.rect.centerx) // 2,
                                        (node.rect.centery + neighbor.rect.centery) // 2))
            pygame.draw.line(display, 'white', node.rect.center, neighbor.rect.center, 1)

# Function to randomly select a start and end point from the nodes
def generate_points(nodes):
    if not nodes:
        raise ValueError('List of Nodes is Empty')

    while True:
        start = nodes[randint(0, len(nodes) - 1)]
        end = nodes[randint(0, len(nodes) - 1)]
        if start != end:
            start.color = 'green'  # Mark start node with green color
            end.color = 'blue'  # Mark end node with blue color
            return start, end

# A* Algorithm
def a_star(start, end, graph):
    open_set = PriorityQueue()  # Priority queue to store nodes to be explored
    open_set.put((0, start))  # Add the start node with priority 0

    # Dictionaries to store:
    # g_scores: Cost from the start node to the current node
    g_scores = {node: float('inf') for node in graph}
    # f_scores: Estimated total cost (g_score + heuristic)
    f_scores = {node: float('inf') for node in graph}
    # parents: To reconstruct the final path
    parents = {node: None for node in graph}

    # Initialize start node costs
    g_scores[start] = 0  # Cost from start to start is 0
    f_scores[start] = calculate_distance(start, end)  # Estimated total cost using heuristic

    while not open_set.empty():  # Continue exploring nodes until there are none left
        current = open_set.get()[1]  # Get the node with the lowest f_score

        if current == end:  # If we reached the destination, reconstruct the path
            return reconstruct_path(current, parents)

        # Explore neighbors of the current node
        for neighbor, distance in graph[current]:
            tentative_g_score = g_scores[current] + distance  # Compute tentative g_score

            # If this new path to the neighbor is better, update its values
            if tentative_g_score < g_scores[neighbor]:  
                parents[neighbor] = current  # Update parent for path reconstruction
                g_scores[neighbor] = tentative_g_score  # Update cost to reach neighbor
                f_scores[neighbor] = tentative_g_score + calculate_distance(neighbor, end)  # Update estimated total cost
                
                # Add the neighbor to the open set if it's not already in it
                if neighbor not in [node[1] for node in open_set.queue]:
                    open_set.put((f_scores[neighbor], neighbor))

    return None  # No path found


# Function to reconstruct the path from end to start
def reconstruct_path(current, parents):
    path = []
    while current:
        path.append(current)
        current = parents[current]
    return path[::-1]  # Reverse the path to get it from start to end

# Main program variables
running = True  # Control the main loop
clock = pygame.time.Clock()  # Manage frame rate
nodes = [Node(randint(0, 1200), randint(0, 700), 10, 10) for x in range(10)]  # Generate 20 randomly placed nodes
graph = build_node_connections(nodes)  # Build connections between nodes
font = pygame.font.Font(None, 18)
start_point, end_point = generate_points(nodes)  # Select start and end points
path = None  # Variable to store the final path

# Main game loop
while running:
    dt = clock.tick() // 1000  # Delta time for frame rate control

    # Event Handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Quit if the window is closed
            running = False

    # Run A* algorithm once to find the path
    if not path:
        path = a_star(start_point, end_point, graph)

    # Clear the display
    display.fill('black')

    # Render all nodes
    for node in nodes:
        node.render()
    
    show_node_connections(graph)

    # Draw the path if it exists
    if path:
        for i in range(len(path) - 1):
            pygame.draw.line(display, 'yellow', path[i].rect.center, path[i + 1].rect.center, 3)

    # Update the display
    pygame.display.flip()

# Clean up and quit Pygame
pygame.quit()
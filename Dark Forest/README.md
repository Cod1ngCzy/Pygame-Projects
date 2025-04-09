"""
README - BLACK FOREST GAME CLASSES
-----------------------------------

This file defines the core classes used in the "Black Forest" game. The key classes are:

1. **Line** - Represents a line segment with methods for detecting intersection and collision.
2. **Segment** - Represents a draggable and resizable rectangular segment.
3. **Ray** - Represents a collection of ray lines used for raycasting.
4. **Observer** - Represents the player or observer in the game, capable of movement, raycasting, and collision handling.

---

# CLASS DESCRIPTIONS

## 1. Line
### Purpose:
- Represents a line segment with a starting and ending point.
- Provides methods for calculating intersection with other lines and collision with circles.

### Attributes:
- `start_point` (Vector2): Starting point of the line.
- `end_point` (Vector2): Ending point of the line.

### Methods:
- `intersect(other_line)`  
    - Checks for intersection between two line segments.
    - Returns the intersection point if they intersect; otherwise, returns `None`.

- `collide(circle_center, circle_radius)`  
    - Checks if a line segment collides with a circle.
    - Returns the closest point of contact if a collision occurs.

- `draw()`  
    - Draws the line on the display window.

---

## 2. Segment
### Purpose:
- Represents a rectangular object that can be dragged and resized using the mouse.
- Used for obstacles or boundaries in the game.

### Attributes:
- `rect` (pygame.Rect): Rectangle representing the segment.
- `pos` (Vector2): Position of the segment.
- `corners` (list): List of corner points.
- `edges` (list): List of edges formed by connecting the corners.

### Methods:
- `update_corners()`  
    - Updates the positions of the segment’s corners.

- `update_edges()`  
    - Updates the edges based on the corner positions.

- `handle_position()`  
    - Allows dragging and resizing the segment using the mouse.

- `show_rect_properties(circle, lines, color)`  
    - Draws the rectangle and optionally shows corners and edges.

- `update()`  
    - Handles user interaction and updates the segment's state.

---

## 3. Ray
### Purpose:
- Represents a collection of rays emitted from a single point.
- Used for line-of-sight and field-of-view calculations.

### Attributes:
- `origin` (Vector2): Starting position of the rays.
- `ray_length` (float): Length of each ray.
- `ray_angle` (float): Spread angle of the rays.
- `ray_num` (int): Number of rays created.

### Methods:
- `create(ray_angle, ray_length, step)`  
    - Creates a list of rays based on angle, length, and step size.

- `cast()`  
    - Draws each ray.

---

## 4. Observer
### Purpose:
- Represents the player or observer in the game.
- Handles movement, raycasting, and collision detection.

### Attributes:
- `rect` (pygame.Rect): Player rectangle.
- `pos` (Vector2): Current position of the player.
- `direction` (Vector2): Current movement direction.
- `ray_length`, `ray_angle`, `ray_step` - Properties for raycasting.
- `line_of_sight` (list): List of rays for line-of-sight.
- `fov` (list): List of rays for field-of-view.

### Methods:
- `create_rays(ray_angle, ray_length, ray_step)`  
    - Creates and returns a list of ray segments based on the specified parameters.

- `update_rays(rays, ray_angle, ray_length, mouse_follow)`  
    - Updates the position and direction of rays.

- `handle_rays(ray, angle, ray_length, mouse_follow, show_lines, obstacles)`  
    - Handles raycasting and intersection with obstacles.

- `draw_rays(polygon_points, show_line, ray_color)`  
    - Draws the visibility polygon or individual rays.

- `draw_visible_edges(intersection_groups)`  
    - Draws the edges of the visibility polygon.

- `handle_collisions(lines)`  
    - Detects and handles collisions with line segments.

- `move(dt)`  
    - Moves the player based on input direction and speed.

- `update(dt, lines)`  
    - Updates player state, handles movement, raycasting, and collisions.

---

# USAGE:
- The `Line` class is used to create barriers or obstacles.
- The `Segment` class is used for creating draggable and resizable obstacles.
- The `Ray` class is used for raycasting (line-of-sight and field-of-view).
- The `Observer` class represents the player and handles interaction with the environment.

---

# GAME LOGIC FLOW:
1. The game creates `Line` objects to define boundaries and obstacles.
2. The player (defined by `Observer`) emits rays to calculate visibility.
3. Rays are updated and checked for intersection with obstacles.
4. The player moves and adjusts direction based on input.
5. The screen is updated every frame to reflect player movement and visibility changes.

---

# STATUS:
🚧 **This is an ongoing project**  
- The objects and methods defined here are currently working but are not finalized.  
- Additional features, optimizations, and adjustments may be made in future versions.  

---
"""

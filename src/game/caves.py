class CaveHelper:
    """
    Manages cave generation, state, and interaction within the terrain grid.

    This class is responsible for creating randomized cave structures using cellular 
    automata smoothing (`generate_caves`), determining when caves should be visually 
    revealed based on player proximity (`check_if_in_cave`), and resetting cave data 
    for world regeneration or transitions (`reset_caves`).

    Attributes:
        _terrain (Terrain): Reference to the terrain system containing grid and event logic.
        grid_size (int): Size of the terrain grid, used for placement boundaries.
        terrain_types (terrainTypes): Enum-like access to terrain tile types (e.g., Floor, Stone).
        caves (dict[int: Cave]): Dictionary storing cave instances by their unique IDs.
        cave_amount (int): Count of caves generated so far, used as indexing.
        wall_probability (float): Chance that a tile is initialized as a wall during cave generation.
    """
    def __init__(self, terrain):
        from src.game import Terrain, terrainTypes
        self._terrain: Terrain = terrain
        self.grid_size = self._terrain.grid_size
        self.terrain_types: terrainTypes = self._terrain.terrain_types
        self.caves: dict[int: Cave] = {}
        self.cave_amount = 0
        self.wall_probability = 0.35

    def generate_caves(self):
        """
        Generates multiple cave structures within the terrain grid.

        This method calculates the number of caves to generate based on grid size,
        selects a consistent cave size (currently 'Large'), and finds valid positions
        within the terrain for each cave. Once a location is found, it invokes 
        generate_cave() to create the cave structure and increments the cave counter.

        Requirements:
        - grid_size must be between 20 and 50 inclusive.
        - Cave size is defined using the CaveSizes enum.
        - Relies on self.find_valid_cave_location() and self.generate_cave() to handle placement and generation.
        """

        cave_amount = 0

        # Determine number of caves based on grid size.
        if 50 >= self.grid_size >= 20:
            cave_amount = round((self.grid_size - 10) // 2)

        if cave_amount != 0:
            for i in range(1, cave_amount + 1):
                cave_size = CaveSizes.Large  # Fixed size used for all generated caves.

                # Attempt to find a valid location for the cave of given size.
                cave_pos = self.find_valid_cave_location(cave_size.value)

                if cave_pos:
                    self.cave_amount += 1
                    cave_x, cave_y = cave_pos
                    width, height = cave_size.value, cave_size.value

                    # Generate the actual cave structure at the computed location.
                    self.generate_cave(cave_x, cave_y, width, height)


    def find_valid_cave_location(self, size: int):
        """
        Attempts to find a valid location for placing a cave of the given size.

        The method makes up to 200 randomized placement attempts within the grid bounds,
        ensuring each candidate location satisfies cave placement rules defined in 
        is_cave_location_valid(). If a valid position is found, it returns the (x, y) 
        coordinates; otherwise, it returns None.

        Parameters:
            size (int): The width and height of the cave to place.

        Returns:
            tuple[int, int] or None: Coordinates of the valid cave position, or None if none found.
        """

        import random
        attempts = 0

        # Try up to 200 random positions within grid bounds to find a valid cave spot.
        while attempts < 200:
            x = random.randint(0, self.grid_size - size)
            y = random.randint(0, self.grid_size - size)

            # Check if this position satisfies cave placement criteria.
            if self.is_cave_location_valid(x, y, size):
                return x, y

            attempts += 1

        return None  # Return None if no valid position found after all attempts.
    
    def is_cave_location_valid(self, x, y, size):
        """
        Determines if a cave of the given size can be placed at position (x, y) without overlap
        or violating proximity rules with existing caves or the grid's middle region.

        Placement rules enforced:
        - Each cave must maintain a `cave_buffer` of empty tiles around other caves.
        - Caves cannot intersect the central area (within ± middle_buffer of terrain.middle).
        - Placement must be fully within bounds, considering size.

        Parameters:
            x (int): Top-left x-coordinate of the potential cave.
            y (int): Top-left y-coordinate of the potential cave.
            size (int): Width and height of the square cave.

        Returns:
            bool: True if the location is valid for cave placement, otherwise False.
        """

        cave_buffer = 1          # Minimum space to maintain between caves.
        middle_buffer = 3        # Buffer around the terrain's middle area.
        end_x, end_y = x + size, y + size  # Bottom-right corner of cave.

        # Iterate through all existing caves to validate placement.
        for cave_id, cave_data in self.caves.items():
            top_l_cave, bot_r_cave = cave_data.rect

            # Check if the cave is completely outside the buffered area of another cave.
            if (end_x <= top_l_cave[0] - cave_buffer or x >= bot_r_cave[0] + cave_buffer) and \
            (end_y <= top_l_cave[1] - cave_buffer or y >= bot_r_cave[1] + cave_buffer):

                # Check if cave intersects with the middle buffered zone of the terrain.
                middle = self._terrain.middle
                middle_min = middle - middle_buffer
                middle_max = middle + middle_buffer

                if x <= middle_max and end_x >= middle_min and \
                y <= middle_max and end_y >= middle_min:
                    return False  # Reject if overlapping with middle zone.

                continue  # Valid with respect to this cave, check next.

            return False  # Overlapping another cave, reject placement.

        return True  # Valid placement — no overlaps or conflicts.


    def generate_cave(self, x_start, y_start, width, height):
        """
        Generates a cave at the specified grid location using cellular automata smoothing.

        This method initializes a randomized grid of terrain types (Stone or Floor), then applies 
        a two-pass smoothing algorithm:
        1. Evaluates each tile's surrounding wall density and converts it to Stone if it meets 
        a threshold.
        2. Refines sparse floor tiles by removing isolated ones based on cardinal neighbor count.

        Parameters:
            x_start (int): Starting x-coordinate for the cave.
            y_start (int): Starting y-coordinate for the cave.
            width (int): Width of the cave.
            height (int): Height of the cave.

        Cave details are stored in self.caves using cave_amount as the unique key.
        """

        import random

        # Clamp cave bounds within grid limits
        x_end, y_end = min(x_start + width, self.grid_size), min(y_start + height, self.grid_size)
        cave_rect = [(x_start, y_start), (x_end - 1, y_end - 1)]  # Bounding box of cave

        # Step 1: Randomize initial grid with walls and floors based on wall_probability
        cave_init = [
            [
                self.terrain_types.Stone if random.random() < self.wall_probability else self.terrain_types.Floor
                for _ in range(width)
            ]
            for _ in range(height)
        ]

        # Initialize new grid for processed cave layout and store floor coordinates
        new_grid = [[self.terrain_types.Floor for _ in range(width)] for _ in range(height)]
        coords_broken = []

        # Step 2: Apply cellular automata smoothing (1st pass)
        for y in range(y_start, y_end):
            for x in range(x_start, x_end):
                local_y = y - y_start
                local_x = x - x_start

                # Count surrounding wall tiles (8 neighbors)
                wall_count = sum(
                    cave_init[local_y][local_x].value
                    for dy in [-1, 0, 1]
                    for dx in [-1, 0, 1]
                    if not (dy == 0 and dx == 0)
                    if 0 <= local_y + dy < height and 0 <= local_x + dx < width
                )

                # Determine transformation threshold based on current tile type
                threshold = 4 if cave_init[local_y][local_x] == self.terrain_types.Stone else 5

                # Transform tile based on neighborhood density
                if wall_count >= threshold:
                    new_grid[local_y][local_x] = self.terrain_types.Stone
                else:
                    coords_broken.append((x, y))  # Mark as a valid walkable tile

        # Step 3: Refine walkable areas (2nd pass) — remove isolated floors
        for y in range(y_start, y_end):
            for x in range(x_start, x_end):
                local_y = y - y_start
                local_x = x - x_start

                # Count adjacent floor tiles in cardinal directions (N/S/E/W)
                floor_count = sum(
                    1
                    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]
                    if 0 <= local_y + dy < height and 0 <= local_x + dx < width
                    and new_grid[local_y + dy][local_x + dx] == self.terrain_types.Floor
                )

                # Remove orphaned floor tiles with few floor neighbors
                if new_grid[local_y][local_x] == self.terrain_types.Floor and floor_count < 2:
                    new_grid[local_y][local_x] = self.terrain_types.Stone
                    coords_broken.remove((x, y))

        # Step 4: Store cave data
        self.caves[self.cave_amount] = Cave(coords_broken, new_grid, cave_rect)
    

    def render_cave(self, cave_id):
        """
        Triggers rendering of a cave's visible floor tiles within the terrain system.

        This method retrieves the cave data associated with the given ID and uses the
        terrain event handler to mark its walkable tiles as 'broken', enabling their
        appearance in the game world.

        Parameters:
            cave_id (int): Identifier for the cave to render.
        """

        cave_data: dict = self.caves[cave_id]  # Retrieve stored cave information.
        coords_visible = cave_data.floor       # Get all visible (walkable) tile coordinates.

        # Invoke terrain system’s event to display the cave tiles.
        self._terrain._event_handler.call_tile_broken(coords_visible)

    def reset_caves(self):
        """
        Clears all existing cave data and resets the cave counter.
        """
        self.caves = {}
        self.cave_amount = 0
    
    def check_if_in_cave(self, coord: tuple[int, int]):
        """
        Checks whether the given coordinate is adjacent to an unrevealed cave
        and renders the cave if one is discovered.

        This method scans nearby tiles (N, S, E, W) to detect if any neighbor lies within 
        the bounds of a hidden cave and is marked as walkable. If such a cave is found, 
        it is marked as rendered and visually revealed.

        Parameters:
            coord (tuple[int, int]): The (x, y) coordinate to check near for cave proximity.

        Side Effects:
            - Updates the _rendered flag of discovered cave(s).
            - Calls render_cave() to visually show discovered cave tiles.
        """

        coord_x, coord_y = coord
        cave_rendered = set()

        # Loop through all caves that haven't been revealed yet
        for cave_id, cave_data in self.caves.items():
            if not cave_data._rendered:
                rect: list[tuple[int, int], tuple[int, int]] = cave_data.rect
                rect_x1, rect_y1 = rect[0]  # Top-left of cave
                rect_x2, rect_y2 = rect[1]  # Bottom-right of cave

                # Cardinal directions from the current coordinate
                directions = [
                    (coord_x + 1, coord_y),
                    (coord_x - 1, coord_y),
                    (coord_x, coord_y + 1),
                    (coord_x, coord_y - 1)
                ]

                for x, y in directions:
                    # If neighbor is inside this cave's rectangle
                    if rect_x1 <= x <= rect_x2 and rect_y1 <= y <= rect_y2:
                        cave_coord_x, cave_coord_y = x - rect_x1, y - rect_y1

                        # If tile at local cave position is floor, reveal the cave
                        if cave_data.cave_grid[cave_coord_y][cave_coord_x] == self.terrain_types.Floor:
                            cave_data.update_rendered()
                            self.render_cave(cave_id)
                            cave_rendered.add(cave_id)

        for cave in cave_rendered:
            del self.caves[cave]



class Cave:
    """
    Represents a cave structure within the terrain grid.

    Stores metadata about the cave's walkable floor coordinates, terrain layout,
    bounding rectangle, and render state.
    """

    def __init__(self, coords, grid, rect):
        self.floor = coords              # List of walkable (floor) tile coordinates.
        self.cave_grid = grid            # 2D list representing cave terrain (Floor/Stone).
        self.rect = rect                 # Bounding box of cave as [(x1, y1), (x2, y2)].
        self._rendered = False           # Flag indicating if the cave has been visually revealed.

    def update_rendered(self):
        """
        Marks the cave as rendered to prevent redundant visual updates.
        """
        self._rendered = True



from enum import Enum
class CaveSizes(Enum):
    Large = 10
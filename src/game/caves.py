class CaveHelper:
    def __init__(self, terrain):
        from src.game import Terrain, terrainTypes
        self._terrain: Terrain = terrain
        self.grid_size = self._terrain.grid_size
        self.terrain_types: terrainTypes = self._terrain.terrain_types
        self.caves: dict[int: Cave] = {}
        self.cave_amount = 0
        self.wall_probability = 0.35

    def generate_caves(self):
        import random
        cave_amount = 0
        if 30 > self.grid_size >= 20:
            cave_options = [CaveSizes.Medium]
            cave_option_weights = [100.0]
            cave_amount = round((self.grid_size - 10) // 2.5)
        elif 100 >= self.grid_size >= 30:
            cave_options = [CaveSizes.Medium, CaveSizes.Large]
            cave_option_weights = [75.0, 25.0]
            cave_amount = round(self.grid_size // 5)

        if cave_amount != 0:
            for i in range(1, cave_amount + 1):
                cave_size = random.choices(cave_options, cave_option_weights, k=1)[0]
                cave_pos = self.find_valid_cave_location(cave_size.value)
                if not cave_pos and cave_size == CaveSizes.Large:
                    cave_size = CaveSizes.Medium
                    cave_pos = self.find_valid_cave_location(cave_size.value)

                if cave_pos:
                    self.cave_amount += 1
                    cave_x, cave_y = cave_pos
                    width, height = cave_size.value, cave_size.value
                    self.generate_cave(cave_x, cave_y, width, height)


    def find_valid_cave_location(self, size: int):
        import random
        attempts = 0
        while attempts < 100:
            x = random.randint(0, self.grid_size - size)
            y = random.randint(0, self.grid_size - size)

            if self.is_cave_location_valid(x, y, size):
                return x, y
            attempts += 1
        return None  # fallback if nothing found
    
    def is_cave_location_valid(self, x, y, size):
        cave_buffer = 2
        middle_buffer = 3
        end_x, end_y = x + size, y + size
        for cave_id, cave_data in self.caves.items():
            top_l_cave, bot_r_cave = cave_data.rect
            if (end_x <= top_l_cave[0] - cave_buffer or x >= bot_r_cave[0] + cave_buffer) and \
                (end_y <= top_l_cave[1] - cave_buffer or y >= bot_r_cave[1] + cave_buffer):
                    # Reject caves that would overlap the middle ± buffer zone
                    middle = self._terrain.middle

                    # Compute buffered middle zone bounds
                    middle_min = middle - middle_buffer
                    middle_max = middle + middle_buffer

                    # Check if cave overlaps that zone — reject it!
                    if x <= middle_max and end_x >= middle_min and \
                        y <= middle_max and end_y >= middle_min:
                        return False
                    continue

            return False
        
        return True


    def generate_cave(self, x_start, y_start, width, height):
        import random
        x_end, y_end = min(x_start + width, self.grid_size), min(y_start + height, self.grid_size)
        cave_rect = [(x_start, y_start), (x_end - 1, y_end - 1)]

        cave_init = [[self.terrain_types.Stone if random.random() < self.wall_probability else self.terrain_types.Floor
                       for _ in range(width)] for _ in range(height)]
        new_grid = [[self.terrain_types.Floor for _ in range(width)] for _ in range(height)]
        coords_broken = []

        for y in range(y_start, y_end):
            for x in range(x_start, x_end):
                local_y = y - y_start
                local_x = x - x_start

                wall_count = sum(
                    cave_init[local_y][local_x].value
                    for dy in [-1, 0, 1]
                    for dx in [-1, 0, 1]
                    if not (dy == 0 and dx == 0)
                    if 0 <= local_y + dy < height and 0 <= local_x + dx < width

                )

                threshold = 4 if cave_init[local_y][local_x] == self.terrain_types.Stone else 5
                if wall_count >= threshold:
                    new_grid[local_y][local_x] = self.terrain_types.Stone
                else:
                    coords_broken.append((x, y))

        
        for y in range(y_start, y_end):
            for x in range(x_start, x_end):
                local_y = y - y_start
                local_x = x - x_start

                floor_count = sum(
                    1
                    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]  # N, S, W, E
                    if 0 <= local_y + dy < height and 0 <= local_x + dx < width
                    and new_grid[local_y + dy][local_x + dx] == self.terrain_types.Floor
                )

                if new_grid[local_y][local_x] == self.terrain_types.Floor and floor_count < 2:
                    new_grid[local_y][local_x] = self.terrain_types.Stone
                    coords_broken.remove((x, y))


        self.caves[self.cave_amount] = Cave(coords_broken, new_grid, cave_rect)
    

    def render_cave(self, cave_id):
        cave_data: dict = self.caves[cave_id]
        coords_visible = cave_data.floor
        self._terrain._event_handler.call_tile_broken(coords_visible)

    def reset_caves(self):
        self.caves = {}
        self.cave_amount = 0
    
    def check_if_in_cave(self, coord: tuple[int, int]):
        coord_x, coord_y = coord
        cave_rendered = []
        for cave_id, cave_data in self.caves.items():
            if not cave_data._rendered:
                rect: list[tuple[int, int], tuple[int, int]] = cave_data.rect
                rect_x1, rect_y1 = rect[0]
                rect_x2, rect_y2 = rect[1]

                directions = [(coord_x + 1, coord_y), (coord_x - 1, coord_y), 
                            (coord_x, coord_y + 1), (coord_x, coord_y - 1)]
                for x, y in directions:
                    if rect_x1 <= x <= rect_x2 and rect_y1 <= y <= rect_y2:
                        cave_coord_x, cave_coord_y = x - rect_x1, y - rect_y1
                        if cave_data.cave_grid[cave_coord_y][cave_coord_x] == self.terrain_types.Floor:
                            cave_data.update_rendered()
                            self.render_cave(cave_id)
                            cave_rendered.append(cave_id)

        for cave in cave_rendered:
            del self.caves[cave]


class Cave:
    def __init__(self, coords, grid, rect):
        self.floor = coords
        self.cave_grid = grid
        self.rect = rect
        self._rendered = False

    def update_rendered(self):
        self._rendered = True

from enum import Enum
class CaveSizes(Enum):
    Medium = 7
    Large = 14
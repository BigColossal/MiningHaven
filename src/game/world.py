from src.game import terrainTypes

class Terrain:
    def __init__(self):
        import src.graphics as gfx

        self._surface: gfx.TerrainSurface = None
        self._outlines: gfx.OutlineSurface = None
        self._shadows: gfx.ShadowSurface = None
        self.data = []
        self.visible_tiles = set()
        self.grid_size = 10
        self.tile_amount = self.grid_size * self.grid_size
        self.initialize_terrain()

        self._ore_amount = 3
        self._ore_appearance_rate = 30
        self.ore_base_chances = []
        self.create_ore_chances()

        self._ore_chances = {}
        self.ore_luck = 1
        self.modify_chances_with_luck()

        self.edge_map = {}


    def initialize_terrain(self):
        self.data = [[terrainTypes.Stone for _ in range(self.grid_size)] for _ in range(self.grid_size)]

    def update_luck(self):
        self.ore_luck += 1

    def set_surface(self, terrain_surface):
        self._surface = terrain_surface

    def set_outlines(self, outline_surface):
        self._outlines = outline_surface

    def set_shadows(self, shadow_surface):
        self._shadows = shadow_surface

    def wipe_terrain_data(self):
        self.data = []

    def break_terrain(self, coord: tuple[int, int]):
        if self.tile_amount > 0:
            self.tile_amount -= 1
            
        x, y = coord
        self.data[y][x] = terrainTypes.Floor
        self.visible_tiles.add(coord)

        def check_surroundings(og_coord: tuple[int, int]):
            x, y = og_coord
            changeable_terrain = []
            coords_to_check: list[tuple[str, tuple[int, int]]] = [("Right", (x + 1, y)), ("Left", (x - 1, y)), ("Down", (x, y + 1)), ("Up", (x, y - 1)), 
                            ("Top Left", (x - 1, y - 1)), ("Down Left", (x - 1, y + 1)), ("Down Right", (x + 1, y + 1)), ("Top Right", (x + 1, y - 1))]

            adjacent_directions = ["Right", "Left", "Down", "Up"]
            for direction, coord in coords_to_check:
                new_x, new_y = coord
                if (new_x >= 0 and new_x < self.grid_size) and (new_y >= 0 and new_y < self.grid_size): # check if in bounds

                    if direction in adjacent_directions:
                        # edge map construction
                        handle_edge_map(direction, og_coord, (new_x, new_y))

                    if coord not in self.visible_tiles:
                        # visible terrain construction
                        self.visible_tiles.add(coord)
                        changeable_terrain.append(coord)
                    else:
                        continue

            return changeable_terrain
        
        def handle_edge_map(direction: str, og_coord: tuple[int, int], new_coord: tuple[int, int]):
            new_x, new_y = new_coord
            if self.data[new_y][new_x] != terrainTypes.Floor:
                if og_coord in self.edge_map:
                    self.edge_map[og_coord].add(direction)
                else:
                    self.edge_map[og_coord] = {direction}
            else:
                # if terrain being currently checked is a floor tile, remove its edge reference to the removed block
                opposite_direction = {"Right": "Left", "Left": "Right", "Up": "Down", "Down": "Up"}[direction]
                self.edge_map[new_coord].remove(opposite_direction)

        def create_ores(coords: list[tuple[int, int]]):
            """
            As ore will be created when theyre revealed, or adjacent to a floor tile and in other terms everything starts
            as stone but gets converted to ore as theyre exposed as the player can upgrade their ore luck mid game, this will
            handle the creation of the ore dependant on the luck
            """
            for coord in coords:
                x, y = coord
                ore_type = choose_ore_type()
                self.data[y][x] = terrainTypes(ore_type)

        def choose_ore_type() -> int:
            import random
            """
            Picks an ore index based on weighted chances in self._ore_chances.
            """
            chances = self._ore_chances
            total = sum(chances.values())

            rand_val = random.uniform(0, total)
            cumulative = 0

            for ore_index, weight in chances.items():
                cumulative += weight
                if rand_val <= cumulative:
                    return ore_index

            # Fallback: just in case of float rounding edge cases
            return 1
        

        surroundings_to_be_changed = check_surroundings(coord)
        create_ores(surroundings_to_be_changed)


    def create_ore_chances(self):
        init_chance = 1.5
        change_rate = 4
        chances = []
        for i in range(self._ore_amount):
            chances.append(round(init_chance * max(1, ((change_rate ** i) * (i * 1.05))), 1))

        self.ore_base_chances = chances

    def modify_chances_with_luck(self, soft_cap=65, decay_rate=0.5):
        modified = {}
        index = 2  # Start from 1 so we reserve index 0 for stone
        for base_chance in self.ore_base_chances:
            num = base_chance
            chance = (self.ore_luck / num) * 100

            if chance > soft_cap:
                overflow = chance - soft_cap
                chance = soft_cap - (overflow * decay_rate)

            if chance <= 0.01:
                continue  # Skip negligible chance ores

            modified[index] = chance
            index += 1

        # Normalize to match ore appearance rate
        total = sum(modified.values())
        normalized = {}

        if total > 0:
            for i, chance in modified.items():
                normalized[i] = round((chance / total) * self._ore_appearance_rate, 2)

        # Force stone to be the remaining chance
        normalized[1] = round(100 - self._ore_appearance_rate, 2)

        self._ore_chances = normalized

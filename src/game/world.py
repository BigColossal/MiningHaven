

class Terrain:
    def __init__(self):
        import src.graphics as gfx
        from src.game import EventHandler, CaveHelper, Miner

        self._cave_surface: gfx.CaveSurface = None
        self._miner_surface: gfx.MinerSurface = None
        self._ui_surface: gfx.UISurface = None
        self._event_handler: EventHandler = None

        self.data = []

        self._miners: list[Miner] = None

        self.grid_size = 50
        self.middle = None
        self.visible_tiles = None

        self._ore_amount = 3
        self._ore_appearance_rate = 30
        self.ore_base_chances = []
        self.create_ore_chances()
        self.ore_base_healths = []
        self.create_ore_healths()
        self.ore_base_golds = []
        self.ore_value_mult = 1
        self.create_ore_golds()
        self.ores_damaged: dict[tuple[int, int]: tuple[float, float]] = {}

        self._ore_chances = {}
        self.ore_luck = 1
        self.modify_chances_with_luck()

        from src.game import terrainTypes
        self.terrain_types = terrainTypes

        self.edge_map = {}
        self._cave_helper: CaveHelper = CaveHelper(self)

        self._objects = {}


    def initialize_terrain(self):
        from src.game import Ore
        self.visible_tiles = set()
        self.middle = self.grid_size // 2
        self.restart_objects()
        self.tile_amount = self.grid_size * self.grid_size
        stone_health = self.get_ore_health(self.terrain_types.Stone)
        stone_gold = self.get_ore_gold(self.terrain_types.Stone)
        self.data = [[Ore(self.terrain_types.Stone, stone_health, stone_gold, (x, y), self._event_handler) for x in range(self.grid_size)] for y in range(self.grid_size)]
        self._event_handler.call_tile_broken([(self.middle, self.middle)])
        self._cave_helper.generate_caves()
        self.spawn_miners()

    def clear_ores_damaged(self):
        self.ores_damaged = {}

    def restart_objects(self):
        self._objects = {}
        self.create_object("Ladder", (self.middle, self.middle), on_floor=True)
    
    def spawn_miners(self):
        for miner in self._miners:
            miner.spawn_miner()

    def miner_decision_make(self, dt):
        for miner in self._miners:
            miner.decision_make(dt)

    def create_object(self, name, pos, on_floor):
        from src.game import GameObject
        obj = GameObject(name, pos, on_floor)
        self._objects[pos] = obj
        

    def check_surroundings(self, og_coord: tuple[int, int]):
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
                    self.handle_edge_map(direction, og_coord, (new_x, new_y))

                if coord not in self.visible_tiles:
                    # visible terrain construction
                    self.visible_tiles.add(coord)
                    if self.data[new_y][new_x].type != self.terrain_types.Floor:
                        changeable_terrain.append(coord)
                else:
                    continue

        return changeable_terrain
    
    def handle_edge_map(self, direction: str, og_coord: tuple[int, int], new_coord: tuple[int, int]):
        new_x, new_y = new_coord
        if self.data[new_y][new_x].type != self.terrain_types.Floor:
            if og_coord in self.edge_map:
                self.edge_map[og_coord].add(direction)
            else:
                self.edge_map[og_coord] = {direction}
        else:
            # if terrain being currently checked is a floor tile, remove its edge reference to the removed block
            opposite_direction = {"Right": "Left", "Left": "Right", "Up": "Down", "Down": "Up"}[direction]
            self.edge_map.get(new_coord, set()).discard(opposite_direction)

    def create_ores(self, coords: list[tuple[int, int]]):
        from src.game import Ore
        """
        As ore will be created when theyre revealed, or adjacent to a floor tile and in other terms everything starts
        as stone but gets converted to ore as theyre exposed as the player can upgrade their ore luck mid game, this will
        handle the creation of the ore dependant on the luck
        """
        for coord in coords:
            x, y = coord
            ore_type = self.terrain_types(self.choose_ore_type())
            ore_health = self.get_ore_health(ore_type)
            ore_gold = self.get_ore_gold(ore_type)
            self.data[y][x] = Ore(ore_type, ore_health, ore_gold, coord, self._event_handler)

    def choose_ore_type(self, ) -> int:
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


    def update_luck(self):
        self.ore_luck += 1

    def set_cave_surface(self, cave_surface):
        self._cave_surface = cave_surface

    def set_miners(self, miners):
        self._miners = miners

    def set_miner_surface(self, miner_surface):
        self._miner_surface = miner_surface

    def set_event_handler(self, event_handler):
        self._event_handler = event_handler

    def set_ui_surface(self, ui_surface):
        self._ui_surface = ui_surface

    def wipe_terrain_data(self):
        self.data = []

    def break_terrain(self, coord: tuple[int, int], initialization: bool, imported_grid=None):
        from src.game import Ore
        if imported_grid:
            grid = imported_grid
        else:
            grid = self.data
        if self.tile_amount > 0:
            self.tile_amount -= 1
        x, y = coord
        grid[y][x] = Ore(self.terrain_types.Floor, 0, 0, (x, y), self._event_handler)
        self.visible_tiles.add(coord)
        self._cave_helper.check_if_in_cave((x, y))

        if not initialization:
            surroundings_to_be_changed = self.check_surroundings(coord)
            self.create_ores(surroundings_to_be_changed)


    def create_ore_chances(self):
        init_chance = 1.5
        change_rate = 4
        chances = []
        for i in range(self._ore_amount):
            chances.insert(0, round(init_chance * max(1, ((change_rate ** i) * (i * 1.05))), 1))

        self.ore_base_chances = chances

    def modify_chances_with_luck(self, soft_cap=65, decay_rate=0.5):
        modified = {}
        index = 2  # Start from 1 so we reserve index 0 for stone
        for base_chance in self.ore_base_chances:
            num = base_chance
            chance = self.ore_luck * num

            if chance > soft_cap:
                overflow = chance - soft_cap
                chance = soft_cap - (overflow * decay_rate)
                if index == len(self.ore_base_chances) + 1:
                    chance = max(1, chance) # Make the last, most valuable ore always spawn no matter what

            if chance <= 0.01:
                index += 1  # Skip negligible chance ores
                continue

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

    def create_ore_healths(self):
        init_health = 5
        change_rate = 5
        healths = []
        for i in range(self._ore_amount + 1): # + 1 because of stone
            healths.append(round(init_health * (change_rate ** i), 1))

        self.ore_base_healths = healths
    
    def create_ore_golds(self):
        init_gold = 1 * self.ore_value_mult
        change_rate = 2.5
        golds = []
        for i in range(self._ore_amount + 1): # + 1 because of stone
            golds.append(round(init_gold * (change_rate ** i)))

        self.ore_base_golds = golds

    def get_ore_health(self, type):
        index = type.value - 1
        return self.ore_base_healths[index]
    
    def get_ore_gold(self, type):
        index = type.value - 1
        return self.ore_base_golds[index]

    def check_if_cleared(self):
        if self.tile_amount == 0:
            self._event_handler.call_darkening_screen()

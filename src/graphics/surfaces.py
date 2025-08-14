import pygame as pg
import src.graphics as gfx

class GameSurface:
    from src.game import Terrain
    def __init__(self):
        self.dynamic_surface = None
        self.static_surface = None
        self.off_x, self.off_y = None, None
        self._terrain = None

    def set_terrain(self, terrain: Terrain):
        self._terrain = terrain

    def set_dynamic_screen(self, screen):
        self.dynamic_surface = screen

    def create_static_surface(self):
        # Create new surface (static surfaces used for non moving tiles, such as terrain, shadows, outlines, UI, etc)
        grid_pixels = self._terrain.grid_size * gfx.TILE_SIZE
        self.static_surface = pg.Surface((grid_pixels, grid_pixels), pg.SRCALPHA).convert_alpha()


class TerrainSurface(GameSurface):
    def __init__(self):
        super().__init__()

    def create_static_surface(self):
        # Create new surface (static surfaces used for non moving tiles, such as terrain, shadows, outlines, UI, etc)
        grid_pixels = self._terrain.grid_size * gfx.TILE_SIZE
        self.static_surface = pg.Surface((grid_pixels, grid_pixels)).convert()

    def update_static(self, game_sprites: gfx.GameSprites, coord: tuple[int, int]):
        x, y = coord
        tile = game_sprites.get_terrain_tile(self._terrain.data[y][x].type)
        self.static_surface.blit(tile, (x * gfx.TILE_SIZE, y * gfx.TILE_SIZE))

    def load_new(self, game_sprites: gfx.GameSprites):
        self.create_static_surface()
        for y in range(self._terrain.grid_size):
            for x in range(self._terrain.grid_size):
                if (x, y) in self._terrain.visible_tiles:
                    self.update_static(game_sprites, (x, y))



class OutlineShadowSurface(GameSurface):
    def __init__(self):
        super().__init__()
        self._tmp_tile = self._tmp_tile = pg.Surface((gfx.TILE_SIZE, gfx.TILE_SIZE), pg.SRCALPHA)
        self.padding = 2
        self.dark_tile = pg.Surface((gfx.TILE_SIZE, gfx.TILE_SIZE), pg.SRCALPHA)
        self.dark_tile.fill((1, 1, 1, 255))

    def update_static(self, game_sprites: gfx.GameSprites, coord: tuple[int, int]):
        x, y = coord
        directions = []
        if coord in self._terrain.edge_map:
            directions = self._terrain.edge_map[coord]

        surrounding_floor, shadow_surf = self.create_shadow_surf(game_sprites, directions, coord)
        self.static_surface.blit(shadow_surf, ((x + self.padding) * gfx.TILE_SIZE, (y + self.padding) * gfx.TILE_SIZE))

        outl_surf = self.create_outline_surf(game_sprites, directions)
        self.static_surface.blit(outl_surf, ((x + self.padding) * gfx.TILE_SIZE, (y + self.padding) * gfx.TILE_SIZE))

        direction_coords = {
            "Up": (x, y - 1), "Down": (x, y + 1),
            "Right": (x + 1, y), "Left": (x - 1, y),
            "Up Right": (x + 1, y - 1), "Up Left": (x - 1, y - 1),
            "Down Right": (x + 1, y + 1), "Down Left": (x - 1, y + 1)
        }
        for direction in surrounding_floor: # for all adjacent tiles that are floor
            neighbor_floor_pos = direction_coords[direction]
            neigh_x, neigh_y = neighbor_floor_pos

            neighbor_directions = None
            if neighbor_floor_pos in self._terrain.edge_map:
                neighbor_directions = self._terrain.edge_map[neighbor_floor_pos]

            self.static_surface.fill((0, 0, 0, 0), ((neigh_x + self.padding) * gfx.TILE_SIZE, (neigh_y + self.padding) * gfx.TILE_SIZE, 
                                              gfx.TILE_SIZE, gfx.TILE_SIZE)) # clear out neighbor tile as to update the outlines there
            
            _, neighbor_surf = self.create_shadow_surf(game_sprites, neighbor_directions, neighbor_floor_pos)
            self.static_surface.blit(neighbor_surf, ((neigh_x + self.padding) * gfx.TILE_SIZE, (neigh_y + self.padding) * gfx.TILE_SIZE))
            if neighbor_directions:
                neighbor_surf = self.create_outline_surf(game_sprites, neighbor_directions)
                self.static_surface.blit(neighbor_surf, ((neigh_x + self.padding) * gfx.TILE_SIZE, (neigh_y + self.padding) * gfx.TILE_SIZE))
        


    def create_outline_surf(self, game_sprites: gfx.GameSprites, edge_directions):
            direction_log = {"Up", "Right", "Down", "Left"}

            self._tmp_tile.fill((0,0,0,0))  # reset


            for direction in edge_directions:
                direction_log.discard(direction) # removes from list as it will be used to check which direction has no edge

                outline_tile = game_sprites.get_outline_tile(direction)
                self._tmp_tile.blit(outline_tile, (0, 0))

            return self._tmp_tile.copy()
    
    def create_shadow_surf(self, game_sprites: gfx.GameSprites, edge_directions, coord):
            """
            Composes the shadow surface for a tile based on directional edges and floor-type corners.

            Args:
                edge_directions (list[str]): Edge directions ("Up", "Right", etc.)
                coord (tuple[int, int]): Tile coordinate.

            Returns:
                surrounding_floor (list[str]): Directions with adjacent floor tiles.
                shadow_surface (pg.Surface): Composite shadow surface for this tile.
            """
            from src.game import terrainTypes
            x, y = coord

            # neighbor positions
            direction_coords = {"adjacent": {
                "Up": (x, y - 1), "Down": (x, y + 1),
                "Right": (x + 1, y), "Left": (x - 1, y)}, "diagonal": {
                "Up Right": (x + 1, y - 1), "Up Left": (x - 1, y - 1),
                "Down Right": (x + 1, y + 1), "Down Left": (x - 1, y + 1)}
            }
    
            diagonal_data = {}
            # Check bounds and collect terrain types from diagonal neighbors
            for name, corner_coord in direction_coords["diagonal"].items():
                corner_x, corner_y = corner_coord
                if 0 <= corner_y < len(self._terrain.data) and 0 <= corner_x < len(self._terrain.data[0]):
                    diagonal_data[name] = self._terrain.data[corner_y][corner_x]

            direction_log = ["Up", "Right", "Down", "Left"]
            shadow_surface = pg.Surface((gfx.TILE_SIZE, gfx.TILE_SIZE), pg.SRCALPHA).convert_alpha()

            # Add shadow edges for missing directions
            if edge_directions:
                for direction in edge_directions:
                    direction_log.remove(direction)
                    shadow_tile = game_sprites.get_shadow_tile(direction)
                    shadow_surface.blit(shadow_tile, (0, 0))

            valid_directions = []
            for direction in direction_log:
                checked_coord = direction_coords["adjacent"][direction]
                checked_x, checked_y = checked_coord
                if 0 <= checked_x < len(self._terrain.data[0]) and 0 <= checked_y < len(self._terrain.data):
                    valid_directions.append(direction)

            surrounding_floor = valid_directions  # Remaining directions are floor-adjacent

            # Determine valid corner combos for lighting
            corner_combos = [("Up", "Right"), ("Up", "Left"), ("Down", "Right"), ("Down", "Left")]
            corner_floors = [name for name, ore in diagonal_data.items() if ore.type == terrainTypes.Floor]

            surrounding_floor += corner_floors  # Merge floor-adjacent cardinal and diagonal

            # Check for corners eligible to light up
            for dir1, dir2 in corner_combos:
                if dir1 in surrounding_floor and dir2 in surrounding_floor:
                    corner = f"{dir1} {dir2}"
                    if corner not in corner_floors:
                        corner_shadow_tile = game_sprites.get_shadow_tile(corner)
                        shadow_surface.blit(corner_shadow_tile, (0, 0))

            return surrounding_floor, shadow_surface

    def add_surrounding_shadow(self, game_sprites: gfx.GameSprites, tile_coord: tuple[int, int], direction: str):
        shadow_tile = game_sprites.get_surrounding_shadow_tile(direction)
        x, y = tile_coord
        tile_size = gfx.TILE_SIZE

        # Convert tile coords to pixel coords
        pixel_x = x * tile_size
        pixel_y = y * tile_size

        self.static_surface.blit(shadow_tile, (pixel_x, pixel_y))

    def update_darkness(self, coord, darken=True):
        x, y = coord
        if darken:
            self.static_surface.blit(self.dark_tile, ((x + self.padding) * gfx.TILE_SIZE, (y + self.padding) * gfx.TILE_SIZE))
        else:
            self.static_surface.fill((0, 0, 0, 0), ((x + self.padding) * gfx.TILE_SIZE, (y + self.padding) * gfx.TILE_SIZE,
                                                gfx.TILE_SIZE, gfx.TILE_SIZE))


    def load_new(self, game_sprites: gfx.GameSprites):
        grid_size = self._terrain.grid_size
        tile_size = gfx.TILE_SIZE
        padding = self.padding

        padded_size = (grid_size + padding * 2) * tile_size
        self.create_static_surface(padded_size)

        # Shift the surface origin so (0,0) is at top-left of padded area
        self.origin_offset = (-padding * tile_size, -padding * tile_size)

        for y in range(-padding, grid_size + padding, 2):
            for x in range(-padding, grid_size + padding, 2):
                direction = None
                if x < 0 and y < 0:
                    direction = "Down Right"
                elif x >= grid_size and y < 0:
                    direction = "Down Left"
                elif x < 0 and y >= grid_size:
                    direction = "Up Right"
                elif x >= grid_size and y >= grid_size:
                    direction = "Up Left"
                elif x < 0:
                    direction = "Right"
                elif x >= grid_size:
                    direction = "Left"
                elif y < 0:
                    direction = "Down"
                elif y >= grid_size:
                    direction = "Up"

                if direction:
                    # Shift tile coords to match padded surface origin
                    draw_x = x + padding
                    draw_y = y + padding
                    self.add_surrounding_shadow(game_sprites, (draw_x, draw_y), direction)

        for y in range(self._terrain.grid_size):
            for x in range(self._terrain.grid_size):
                if (x, y) not in self._terrain.visible_tiles:
                    self.update_darkness((x, y))

    def create_static_surface(self, size):
        self.static_surface = pg.Surface((size, size), pg.SRCALPHA).convert_alpha()

class MinerSurface(GameSurface):
    def __init__(self):
        from src.game import Miner
        super().__init__()
        self.sprite = self.set_sprite()
        self.miners: list[Miner] = None
        self.miner_positions: dict[int: tuple[float, float]] = {}

    def update_miner_amount(self):
        self.miners = self._terrain._miners

    def set_sprite(self):
        surface = pg.Surface((gfx.TILE_SIZE, gfx.TILE_SIZE), pg.SRCALPHA)

        color = (100, 100, 10)
        circle_size = int(gfx.TILE_SIZE / 2)
        pg.draw.circle(surface, color, (circle_size, circle_size), circle_size - 25)
        return surface
    
    def update_pos(self):
        for miner in self.miners:
            id, pos = miner.id, miner.pos
            self.miner_positions[id] = pos

    
    def update_static(self):
        """Only redraws changed miner positions."""
        dirty_rects = []

        for miner in self.miners:
            old_x, old_y = self.miner_positions[miner.id]
            dirty_rects.append(pg.Rect(old_x * gfx.TILE_SIZE, old_y * gfx.TILE_SIZE, gfx.TILE_SIZE, gfx.TILE_SIZE))

        for rect in dirty_rects:
            self.static_surface.fill((0, 0, 0, 0), rect)

        for miner in self.miners:
            x, y = miner.pos
            self.static_surface.blit(self.sprite, (x * gfx.TILE_SIZE, y * gfx.TILE_SIZE))


    def load_new(self):
        self.create_static_surface()
        for miner in self.miners:
            self.miner_positions[miner.id] = miner.pos

        self.update_static()

class ObjectSurface(GameSurface):
    def __init__(self):
        super().__init__()
        self.objects: dict = {}

    def set_objects(self):
        self.objects = self._terrain._objects

    def update_static(self, obj, game_sprites: gfx.GameSprites):
        x, y = obj.pos
        obj_sprite = game_sprites.get_object_tile(obj.name)
        self.static_surface.blit(obj_sprite, (x * gfx.TILE_SIZE, y * gfx.TILE_SIZE))

    def load_new(self, game_sprites: gfx.GameSprites):
        self.create_static_surface()
        pg.draw.rect(self.static_surface, (175, 220, 240), (
            0,
            0,
            self._terrain.grid_size * gfx.TILE_SIZE,
            self._terrain.grid_size * gfx.TILE_SIZE
        ), 2)
        for obj_name, obj in self.objects.items():
            self.update_static(obj, game_sprites)

class HealthBarSurface(GameSurface):
    def __init__(self):
        super().__init__()
        self.health_bar_rect = pg.Rect(0, 0, gfx.TILE_SIZE, gfx.TILE_SIZE / 4)
        self.health_bars: dict[(int, int): pg.Surface] = {}

    def update_static(self, coord, health_percent):
        x, y = coord
        if health_percent > 0:
            pg.draw.rect(self.static_surface, (40, 40, 40), (x * gfx.TILE_SIZE, y * gfx.TILE_SIZE, gfx.TILE_SIZE, 10))

            # Fill (e.g., green) — scaled to health percentage
            fill_width = int(gfx.TILE_SIZE * (health_percent / 100))
            pg.draw.rect(self.static_surface, (0, 255, 0), (x * gfx.TILE_SIZE, y * gfx.TILE_SIZE, fill_width, 10))
        else:
            self.static_surface.fill((0, 0, 0, 0), rect=(x * gfx.TILE_SIZE, y * gfx.TILE_SIZE, gfx.TILE_SIZE, 10))

    def load_new(self):
        self.create_static_surface()
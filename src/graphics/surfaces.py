import pygame as pg
import src.graphics as gfx

class GameSurface:
    from src.game import Terrain
    def __init__(self):
        self.dynamic_surface = pg.Surface((gfx.SCREEN_WIDTH, gfx.SCREEN_HEIGHT), pg.SRCALPHA)
        self.static_surface = None
        self.off_x, self.off_y = None, None
        self.dirty = True
        self._terrain = None

    def set_terrain(self, terrain: Terrain):
        self._terrain = terrain

    def create_static_surface(self):
        # Create new surface (static surfaces used for non moving tiles, such as terrain, shadows, outlines, UI, etc)
        grid_pixels = self._terrain.grid_size * gfx.TILE_SIZE
        self.static_surface = pg.Surface((grid_pixels, grid_pixels), pg.SRCALPHA)

    def update_dynamic(self, offsets: tuple[float, float]):
        # Update dynamic screen (used for refreshing the screen and for parts of gfx that are NOT static, like animations)
        if self.dirty:
            self.empty_dynamic_screen()
            self.off_x, self.off_y = offsets
            self.dynamic_surface.blit(self.static_surface, (-self.off_x, -self.off_y))
            self.dirty = False

    def empty_dynamic_screen(self):
        self.dynamic_surface.fill((0, 0, 0, 0))



class TerrainSurface(GameSurface):
    def __init__(self):
        super().__init__()

    def update_static(self, game_sprites: gfx.GameSprites, coord: tuple[int, int]):
        self.dirty = True
        x, y = coord
        tile = game_sprites.get_terrain_tile(self._terrain.data[y][x])
        self.static_surface.blit(tile, (x * gfx.TILE_SIZE, y * gfx.TILE_SIZE))

    def create_new_cave(self, game_sprites: gfx.GameSprites):
        self.create_static_surface()
        for y in range(self._terrain.grid_size):
            for x in range(self._terrain.grid_size):
                self.update_static(game_sprites, (x, y))



class OutlineSurface(GameSurface):
    def __init__(self):
        super().__init__()


    def update_static(self, game_sprites: gfx.GameSprites, coord: tuple[int, int]):
        self.dirty = True
        x, y = coord
        directions = []
        if coord in self._terrain.edge_map:
            directions = self._terrain.edge_map[coord]


        def create_outline_surf(edge_directions):
            direction_log = ["Up", "Right", "Down", "Left"]
            outline_surface = pg.Surface((gfx.TILE_SIZE, gfx.TILE_SIZE), pg.SRCALPHA)

            for direction in edge_directions:
                direction_log.remove(direction) # removes from list as it will be used to check which direction has no edge

                outline_tile = game_sprites.get_outline_tile(direction)
                outline_surface.blit(outline_tile, (0, 0))

            return direction_log, outline_surface
        

        floors_surrounding, outl_surf = create_outline_surf(directions)
        self.static_surface.blit(outl_surf, (x * gfx.TILE_SIZE, y * gfx.TILE_SIZE))

        direction_coords = {"Up": (x, y - 1), "Down": (x, y + 1), "Right": (x + 1, y), "Left": (x - 1, y)}
        for direction in floors_surrounding: # for all adjacent tiles that are floor
            neighbor_floor_pos = direction_coords[direction]
            neigh_x, neigh_y = neighbor_floor_pos

            neighbor_directions = None
            if neighbor_floor_pos in self._terrain.edge_map:
                neighbor_directions = self._terrain.edge_map[neighbor_floor_pos]

            self.static_surface.fill((0, 0, 0, 0), (neigh_x * gfx.TILE_SIZE, neigh_y * gfx.TILE_SIZE, 
                                              gfx.TILE_SIZE, gfx.TILE_SIZE)) # clear out neighbor tile as to update the outlines there

            if neighbor_directions:
                _, neighbor_surf = create_outline_surf(neighbor_directions)
                self.static_surface.blit(neighbor_surf, (neigh_x * gfx.TILE_SIZE, neigh_y * gfx.TILE_SIZE))
            

    def create_new_outline_surface(self):
        self.create_static_surface()



class ShadowSurface(GameSurface):
    def __init__(self):
        super().__init__()


    def update_static(self, game_sprites: gfx.GameSprites, coord: tuple[int, int]):
        """
        Updates the static lighting layer at a given tile coordinate by:
        1. Drawing directional and corner shadows based on terrain edges and diagonal neighbors.
        2. Refreshing neighboring tiles to reflect any visual lighting changes triggered by the update.
        
        Args:
            game_sprites (gfx.GameSprites): Container with lighting/shadow sprite assets.
            coord (tuple[int, int]): Tile coordinate (x, y) to update.
        
        Notes:
            - Diagonal corner shadows are rendered based on surrounding terrainTypes.Floor, 
            even if no edge data exists for a tile.
            - Neighbor tiles are proactively cleared and re-rendered to preserve lighting consistency.
        """
        self.dirty = True  # Flag the surface as needing redraw
        x, y = coord
        directions = []
        
        # Get directional edge data if available
        if coord in self._terrain.edge_map:
            directions = self._terrain.edge_map[coord]

        def create_shadow_surf(edge_directions, coord):
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
            shadow_surface = pg.Surface((gfx.TILE_SIZE, gfx.TILE_SIZE), pg.SRCALPHA)

            # Add shadow edges for missing directions
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
            corner_floors = [name for name, type in diagonal_data.items() if type == terrainTypes.Floor]

            surrounding_floor += corner_floors  # Merge floor-adjacent cardinal and diagonal

            # Check for corners eligible to light up
            for dir1, dir2 in corner_combos:
                if dir1 in surrounding_floor and dir2 in surrounding_floor:
                    corner = f"{dir1} {dir2}"
                    if corner not in corner_floors:
                        corner_shadow_tile = game_sprites.get_shadow_tile(corner)
                        shadow_surface.blit(corner_shadow_tile, (0, 0))

            return surrounding_floor, shadow_surface

        # Main tile lighting update
        surrounding_floor, shadow_surf = create_shadow_surf(directions, coord)
        self.static_surface.blit(shadow_surf, (x * gfx.TILE_SIZE, y * gfx.TILE_SIZE))

        # Coordinates of all cardinal and diagonal directions
        direction_coords = {
            "Up": (x, y - 1), "Down": (x, y + 1),
            "Right": (x + 1, y), "Left": (x - 1, y),
            "Up Right": (x + 1, y - 1), "Up Left": (x - 1, y - 1),
            "Down Right": (x + 1, y + 1), "Down Left": (x - 1, y + 1)
        }

        # Neighbor lighting pass (ripple update)
        for floor_direction in surrounding_floor:
            neighbor_coord = direction_coords[floor_direction]
            neigh_x, neigh_y = neighbor_coord

            # Get edge data or default to empty
            neighbor_directions = []
            if neighbor_coord in self._terrain.edge_map:
                neighbor_directions = self._terrain.edge_map[neighbor_coord]

            # Clear existing shadow at neighbor tile
            self.static_surface.fill((0, 0, 0, 0), (neigh_x * gfx.TILE_SIZE, neigh_y * gfx.TILE_SIZE,
                                                gfx.TILE_SIZE, gfx.TILE_SIZE))

            # Recreate lighting based on terrain conditions
            test_floor, neighbor_surf = create_shadow_surf(neighbor_directions, neighbor_coord)
            self.static_surface.blit(neighbor_surf, (neigh_x * gfx.TILE_SIZE, neigh_y * gfx.TILE_SIZE))




    def create_new_shadow_surface(self):
        self.create_static_surface()
















import pygame as pg
import src.graphics as gfx

class GameSurface:
    from src.game import Terrain
    def __init__(self):
        self.dynamic_surface = pg.Surface((gfx.SCREEN_WIDTH, gfx.SCREEN_HEIGHT), pg.SRCALPHA)
        self.static_surface = None
        self.off_x, self.off_y = None, None
        self._terrain = None

    def set_terrain(self, terrain: Terrain):
        self._terrain = terrain

    def create_eraser(self):
        tile_eraser = pg.Surface((gfx.TILE_SIZE, gfx.TILE_SIZE), pg.SRCALPHA)
        return tile_eraser

    def create_static_surface(self):
        # Create new surface (static surfaces used for non moving tiles, such as terrain, shadows, outlines, UI, etc)
        grid_pixels = self._terrain.grid_size * gfx.TILE_SIZE
        self.static_surface = pg.Surface((grid_pixels, grid_pixels), pg.SRCALPHA)

    def update_dynamic(self, offsets: tuple[float, float]):
        # Update dynamic screen (used for refreshing the screen and for parts of gfx that are NOT static, like animations)
        self.empty_dynamic_screen()
        self.off_x, self.off_y = offsets
        self.dynamic_surface.blit(self.static_surface, (-self.off_x, -self.off_y))

    def empty_dynamic_screen(self):
        self.dynamic_surface.fill((0, 0, 0, 0))

class TerrainSurface(GameSurface):
    def __init__(self):
        super().__init__()

    def update_static(self, game_sprites: gfx.GameSprites, coord: tuple[int, int]):
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
        self.outline_map = {}


    def update_static(self, game_sprites: gfx.GameSprites, coord: tuple[int, int]):
        x, y = coord
        directions = self._terrain.edge_map[coord]


        def create_outline_surf(edge_directions):
            direction_log = ["Up", "Right", "Down", "Left"]
            outline_surface = pg.Surface((gfx.TILE_SIZE, gfx.TILE_SIZE), pg.SRCALPHA)

            for direction in edge_directions:
                if direction_log:
                    direction_log.remove(direction) # removes from list as it will be used to check which direction has no edge

                outline_tile = game_sprites.get_outline_tile(direction)
                outline_surface.blit(outline_tile, (0, 0))

            return direction_log, outline_surface
        

        all_directions, outl_surf = create_outline_surf(directions)
        self.static_surface.blit(outl_surf, (x * gfx.TILE_SIZE, y * gfx.TILE_SIZE))

        direction_coords = {"Up": (x, y - 1), "Down": (x, y + 1), "Right": (x + 1, y), "Left": (x - 1, y)}
        for direction in all_directions: # for all adjacent tiles that are floor
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







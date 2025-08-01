import pygame as pg
import src.graphics as gfx

class GameSurface:
    from src.game import Terrain
    def __init__(self):
        self.dynamic_surface = pg.Surface((gfx.SCREEN_WIDTH, gfx.SCREEN_HEIGHT), pg.SRCALPHA)
        self.static_surface = None
        self.dirty = True
        self.off_x, self.off_y = None, None
        self._terrain = None

    def set_terrain(self, terrain: Terrain):
        self._terrain = terrain

    def create_static_surface(self):
        grid_pixels = self._terrain.grid_size * gfx.TILE_SIZE
        self.static_surface = pg.Surface((grid_pixels, grid_pixels), pg.SRCALPHA)

    def empty_dynamic_screen(self):
        self.dynamic_surface.fill((0, 0, 0, 0))

    def draw(self, data):
        pass

    def update(self, data):
        pass

class TerrainSurface(GameSurface):
    def __init__(self):
        super().__init__()

    def update_static(self, game_sprites: gfx.GameSprites = None, coord: tuple[int, int] = None):
        x, y = coord
        tile = game_sprites.get_terrain_tile(self._terrain.data[y][x])
        self.static_surface.blit(tile, (x * gfx.TILE_SIZE, y * gfx.TILE_SIZE))

    def update_dynamic(self, offsets: tuple[float, float]):
        self.empty_dynamic_screen()
        self.off_x, self.off_y = offsets
        self.dynamic_surface.blit(self.static_surface, (-self.off_x, -self.off_y))

    def draw_new_cave(self, game_sprites: gfx.GameSprites):
        self.create_static_surface()
        for y in range(self._terrain.grid_size):
                for x in range(self._terrain.grid_size):
                    self.update_static(game_sprites, (x, y))



class OutlineSurface(GameSurface):
    def __init__(self):
        super().__init__()

    def update(self, game_sprites: gfx.GameSprites, coord: tuple[int, int] = None, full_screen: bool = False, 
               offsets: tuple[float, float] = None):
        if full_screen:
            # if the whole screen, as in the camera was moved or if the cave got restarted, itll run 
            # and set new offset coords while updating everything
            self.empty_screen()
            self.off_x, self.off_y = offsets
            for y in range(self._terrain.grid_size):
                for x in range(self._terrain.grid_size):
                    self.get_and_update_tile(x, y, game_sprites)



    def get_and_update_tile(self, coord, game_sprites: gfx.GameSprites):
        pass






import pygame as pg
import src.graphics as gfx
from src.game import Terrain

class RenderManager:
    def __init__(self, terrain: Terrain):
        self.__screen = pg.display.set_mode((gfx.SCREEN_WIDTH, gfx.SCREEN_HEIGHT))
        pg.display.set_caption("My Game Screen")
        self._GAME_SPRITES = gfx.extract_sprites()
        self._terrain = terrain
        self._terrain_surface: gfx.TerrainSurface = self._terrain._surface

        self.map_height, self.map_width = None, None
        self.offset_x, self.offset_y = None, None

        self.set_map_dimensions()
        self.set_initial_offset()

        self.load_new_cave()

    def set_map_dimensions(self):
        total_pixels = self._terrain.grid_size * gfx.TILE_SIZE
        self.map_height, self.map_width = total_pixels, total_pixels

    def set_initial_offset(self):
        self.offset_x = (gfx.SCREEN_WIDTH - self.map_width) // 2
        self.offset_y = (gfx.SCREEN_HEIGHT - self.map_height) // 2

    def load_new_cave(self): # for drawing brand new caves
        self._terrain_surface.update(self._GAME_SPRITES, full_screen=True, offsets=(self.offset_x, self.offset_y))

    def fill(self, color):
        self.__screen.fill(color)

    def render(self):
        self.fill(gfx.BG_COLOR)

        self.__screen.blit(self._terrain_surface.surface, (0, 0))
        pg.display.flip()

    def break_terrain(self, coord):
        self._terrain_surface.update(self._GAME_SPRITES, coord)


        
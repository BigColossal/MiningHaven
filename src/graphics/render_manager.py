import pygame as pg
import src.graphics as gfx
from src.game import Terrain

class RenderManager:
    def __init__(self, terrain: Terrain):
        self.__screen = pg.display.set_mode((gfx.SCREEN_WIDTH, gfx.SCREEN_HEIGHT))
        pg.display.set_caption("My Game Screen")
        self._GAME_SPRITES = gfx.extract_sprites()
        self._terrain = terrain
        self.grid_size = self._terrain.grid_size
        self._terrain_surface: gfx.TerrainSurface = self._terrain._surface

        self.map_height, self.map_width = None, None
        self.offset_x, self.offset_y = None, None

        self.set_map_dimensions()
        self.set_initial_offset()

        self.load_new_cave()

    def set_map_dimensions(self):
        total_pixels = self.grid_size * gfx.TILE_SIZE
        self.map_height, self.map_width = total_pixels, total_pixels

    def set_initial_offset(self): # to start the game at the center of the cave
        self.offset_x = -(gfx.SCREEN_WIDTH - self.map_width) // 2
        self.offset_y = -(gfx.SCREEN_HEIGHT - self.map_height) // 2

    def load_new_cave(self): # for drawing brand new caves
        self._terrain_surface.draw_new_cave(self._GAME_SPRITES)
        self._terrain_surface.update_dynamic((self.offset_x, self.offset_y))

    def fill(self, color): # fill background
        self.__screen.fill(color)

    def render(self):
        self.fill(gfx.BG_COLOR)

        self.__screen.blit(self._terrain_surface.dynamic_surface, (0, 0))
        pg.display.flip()

    def break_terrain(self, coord: tuple[int, int]):
        # updates the broken terrain and its surroundings
        x, y = coord
        coords_to_check = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1), 
                            (x - 1, y - 1), (x - 1, y + 1), (x + 1, y + 1), (x + 1, y -1)]
        
        self._terrain_surface.update_static(self._GAME_SPRITES, coord)
        for coord in coords_to_check:
            x, y = coord
            if (x >= 0 and x < self.grid_size) and (y >= 0 and y < self.grid_size):
                self._terrain_surface.update_static(self._GAME_SPRITES, coord)

    def move_camera(self, keys):
        move_x = 0
        move_y = 0

        if keys[pg.K_a]:
            move_x -= 1
        if keys[pg.K_d]:
            move_x += 1
        if keys[pg.K_w]:
            move_y -= 1
        if keys[pg.K_s]:
            move_y += 1

        # Normalize vector if moving diagonally
        if move_x != 0 and move_y != 0:
            norm = gfx.CAMERA_MOVEMENT_SPEED / (2 ** 0.5)  # ≈ 0.707
        else:
            norm = gfx.CAMERA_MOVEMENT_SPEED

        self.offset_x += move_x * norm
        self.offset_y += move_y * norm

        self._terrain_surface.update_dynamic((self.offset_x, self.offset_y))




        
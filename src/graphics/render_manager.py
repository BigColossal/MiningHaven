import pygame as pg
import src.graphics as gfx
from src.game import Terrain

class RenderManager:
    def __init__(self, terrain: Terrain):
        self.__screen = pg.display.set_mode((gfx.SCREEN_WIDTH, gfx.SCREEN_HEIGHT))
        pg.display.set_caption("Mining Mayhem")

        self._GAME_SPRITES = gfx.extract_sprites()
        self._terrain = terrain
        self.grid_size = self._terrain.grid_size
        self._terrain_surface: gfx.TerrainSurface = self._terrain._surface
        self._outline_surface: gfx.OutlineSurface = self._terrain._outlines
        self._shadow_surface: gfx.ShadowSurface = self._terrain._shadows
        self._darkness_surface: gfx.DarknessSurface = self._terrain._darkness
        self.surfaces = [self._terrain_surface, self._outline_surface, self._shadow_surface, self._darkness_surface]

        self.map_height, self.map_width = None, None
        self.offset_x, self.offset_y = None, None

        self.set_map_dimensions()
        self.set_initial_offset()
        self.darkening = False
        self.lightening = False
        self.dark_alpha = 0
        self.lighten_buffer_duration = 1500

    def set_map_dimensions(self):
        total_pixels = self.grid_size * gfx.TILE_SIZE
        self.map_height, self.map_width = total_pixels, total_pixels

    def set_initial_offset(self): # to start the game at the center of the cave
        self.offset_x = -(gfx.SCREEN_WIDTH - self.map_width) // 2
        self.offset_y = -(gfx.SCREEN_HEIGHT - self.map_height) // 2

    def load_new_cave(self): # for drawing brand new caves
        self._terrain_surface.create_new_cave(self._GAME_SPRITES)
        self._outline_surface.create_new_outline_surface()
        self._shadow_surface.create_new_shadow_surface()
        self._darkness_surface.create_new_cave()

    def fill(self, color): # fill background
        self.__screen.fill(color)

    def update(self):
        for surface in self.surfaces:
            surface.update_dynamic((self.offset_x, self.offset_y))

    def render(self, dt):
        self.fill(gfx.BG_COLOR)

        self.__screen.blit(self._terrain_surface.dynamic_surface, (0, 0))
        self.__screen.blit(self._shadow_surface.dynamic_surface, (0, 0))
        self.__screen.blit(self._outline_surface.dynamic_surface, (0, 0))
        self.__screen.blit(self._darkness_surface.dynamic_surface, (0, 0))
        if self.darkening:
            self.darken_screen(dt)
        elif self.lightening:
            self.lighten_screen(dt)
        pg.display.flip()

    def break_terrain(self, coord: tuple[int, int]):
        # updates the broken terrain and its surroundings
        x, y = coord
        coords_to_check = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1), 
                            (x - 1, y - 1), (x - 1, y + 1), (x + 1, y + 1), (x + 1, y -1)]
        
        self._terrain_surface.update_static(self._GAME_SPRITES, coord)
        self._darkness_surface.update_static((x, y), darken=False)
        self._outline_surface.update_static(self._GAME_SPRITES, coord)
        self._shadow_surface.update_static(self._GAME_SPRITES, coord)
        for coord in coords_to_check:
            x, y = coord
            if (x >= 0 and x < self.grid_size) and (y >= 0 and y < self.grid_size):
                self._terrain_surface.update_static(self._GAME_SPRITES, coord)
                self._darkness_surface.update_static((x, y), darken=False)

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

        for surface in self.surfaces:
            surface.dirty = True

    def darken_screen(self, dt):
        # Fade speed: pixels per second
        fade_rate = 300  # Increase for faster fade
        self.dark_alpha = min(self.dark_alpha + fade_rate * (dt / 1000), 255)

        fade_surface = pg.Surface(self.__screen.get_size())
        fade_surface.set_alpha(int(self.dark_alpha))
        fade_surface.fill((0, 0, 0))
        self.__screen.blit(fade_surface, (0, 0))

        if self.dark_alpha >= 255:
            self.darkening = False
            self._terrain._event_handler.call_cave_cleared()

    def lighten_screen(self, dt):
        # Only start buffer when darkening stops
        if not hasattr(self, 'lighten_buffer_time'):
            self.lighten_buffer_time = 0

        if self.lighten_buffer_time < self.lighten_buffer_duration:
            self.lighten_buffer_time += dt
            fade_surface = pg.Surface(self.__screen.get_size())
            fade_surface.fill((0, 0, 0))  # Full black during buffer
            self.__screen.blit(fade_surface, (0, 0))
            return

        # Fade out begins after buffer
        fade_rate = 300
        self.dark_alpha = max(self.dark_alpha - fade_rate * (dt / 1000), 0)

        fade_surface = pg.Surface(self.__screen.get_size())
        fade_surface.set_alpha(int(self.dark_alpha))
        fade_surface.fill((0, 0, 0))
        self.__screen.blit(fade_surface, (0, 0))

        if self.dark_alpha <= 0:
            self.lightening = False
            self.lighten_buffer_time = 0  # Reset for future use






        
import pygame as pg
import src.graphics as gfx
from src.game import Terrain

class RenderManager:
    def __init__(self, terrain: Terrain):
        self._screen = pg.display.set_mode((gfx.SCREEN_WIDTH, gfx.SCREEN_HEIGHT))
        pg.display.set_caption("Mining Mayhem")

        self._GAME_SPRITES = gfx.extract_sprites()
        self._terrain = terrain
        self.grid_size = self._terrain.grid_size
        self._terrain_surface: gfx.TerrainSurface = self._terrain._surface
        self._outline_surface: gfx.OutlineSurface = self._terrain._outlines
        self._shadow_surface: gfx.ShadowSurface = self._terrain._shadows
        self._darkness_surface: gfx.DarknessSurface = self._terrain._darkness
        self._miner_surface: gfx.MinerSurface = self._terrain._miner_surface
        self._object_surface: gfx.ObjectSurface = self._terrain._object_surface
        self.surfaces = [self._terrain_surface, self._object_surface, self._outline_surface, self._shadow_surface, 
                         self._darkness_surface, self._miner_surface]

        self.map_height, self.map_width = None, None
        self.offset_x, self.offset_y = None, None
        self.dirty = True

        self.set_map_dimensions()
        self.set_initial_offset()
        self.darkening = False
        self.lightening = False
        self.dark_alpha = 0
        self.lighten_buffer_duration = 1500

        self._text_handler: gfx.TextHandler = None
        self.fps_counter = None

    def set_renderer_to_surfaces(self):
        for surface in self.surfaces:
            surface.set_dynamic_screen(self._screen)

    def set_text_handler(self, text_handler):
        self._text_handler = text_handler

    def set_map_dimensions(self):
        total_pixels = self.grid_size * gfx.TILE_SIZE
        self.map_height, self.map_width = total_pixels, total_pixels

    def set_initial_offset(self): # to start the game at the center of the cave
        self.offset_x = -(gfx.SCREEN_WIDTH - self.map_width) // 2
        self.offset_y = -(gfx.SCREEN_HEIGHT - self.map_height) // 2

    def load_new_cave(self): # for drawing brand new caves
        self._object_surface.set_objects()
        self._miner_surface.update_miner_amount()
        for surface in self.surfaces:
            if surface == self._terrain_surface or surface == self._object_surface:
                surface.load_new(self._GAME_SPRITES)
            else:
                surface.load_new()

    def check_miner_pos(self):
        miners_changed = False
        for miner in self._terrain._miners:
            id = miner.id
            if miner.pos != self._miner_surface.miner_positions[id]:
                miners_changed = True
                break
        if miners_changed:
            self._miner_surface.update_static()
            self._miner_surface.update_pos()
            self.dirty = True


    def fill(self, color): # fill background
        self._screen.fill(color)

    def render(self, dt, fps):
        self.set_FPS_counter(fps)
        if self.dirty == True:
            self.fill(gfx.BG_COLOR)

            for surface in self.surfaces:
                surface.update_dynamic((self.offset_x, self.offset_y))

            if self.darkening:
                self.darken_screen(dt)
            elif self.lightening:
                self.lighten_screen(dt)
            self._screen.blit(self.fps_counter, (0, 0))
            pg.display.flip()
        self.dirty = False

    def break_terrain(self, coord: tuple[int, int]):
        # updates the broken terrain and its surroundings
        self.dirty = True
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

        self.offset_x += int(move_x * norm)
        self.offset_y += int(move_y * norm)
        

        self.dirty = True

    def darken_screen(self, dt):
        # Fade speed: pixels per second
        fade_rate = 300  # Increase for faster fade
        self.dark_alpha = min(self.dark_alpha + fade_rate * (dt), 255)

        fade_surface = pg.Surface(self._screen.get_size())
        fade_surface.set_alpha(int(self.dark_alpha))
        fade_surface.fill((0, 0, 0))
        self._screen.blit(fade_surface, (0, 0))

        if self.dark_alpha >= 255:
            self.darkening = False
            self._terrain._event_handler.call_cave_cleared()

    def lighten_screen(self, dt):
        # Only start buffer when darkening stops
        if not hasattr(self, 'lighten_buffer_time'):
            self.lighten_buffer_time = 0

        if self.lighten_buffer_time < self.lighten_buffer_duration:
            self.lighten_buffer_time += dt * 1000
            fade_surface = pg.Surface(self._screen.get_size())
            fade_surface.fill((0, 0, 0))  # Full black during buffer
            self._screen.blit(fade_surface, (0, 0))
            return

        # Fade out begins after buffer
        fade_rate = 300
        self.dark_alpha = max(self.dark_alpha - fade_rate * (dt), 0)

        fade_surface = pg.Surface(self._screen.get_size())
        fade_surface.set_alpha(int(self.dark_alpha))
        fade_surface.fill((0, 0, 0))
        self._screen.blit(fade_surface, (0, 0))

        if self.dark_alpha <= 0:
            self.lightening = False
            self.lighten_buffer_time = 0  # Reset for future use

    def set_FPS_counter(self, fps):
        self.fps_counter = self._text_handler.create_text(f"{int(fps)}fps", "agentfb", 40, (120, 225, 120))





        